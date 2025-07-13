from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from datetime import datetime
import numpy as np
import json
import os
from utility import validate_json_structure, safe_json_dump

model = "llama3-8b-8192"

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name=model,
    temperature=0.3
)


# Extend the JSONEncoder class
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def log_trade_decision_json(trade_data, log_file='out/logs/trade_decisions.jsonl'):
    """
    Appends a trade decision (dict) as JSON to a .jsonl (JSON Lines) file.
    Each line is a separate JSON object.
    """
    # Validate the trade_data structure
    required_keys = ['timestamp', 'symbol', 'decision']
    is_valid, error_msg = validate_json_structure(
        trade_data, required_keys=required_keys)

    if not is_valid:
        print(f"Warning: Invalid trade data structure: {error_msg}")
        return False

    # Ensure logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    try:
        with open(log_file, 'a') as f:
            json.dump(trade_data, f, cls=NpEncoder)
            f.write('\n')  # Each JSON object on a new line
        return True
    except Exception as e:
        print(f"Error writing to log file {log_file}: {e}")
        return False


def load_all_trades(log_path: str = 'logs/trades_log.json'):
    """
    Safely loads trades from JSON file with validation.
    """
    try:
        with open(log_path) as f:
            data = json.load(f)

        # Validate that data is a list of trade dictionaries
        if not isinstance(data, list):
            print(f"Warning: Expected list of trades, got {type(data)}")
            return []

        # Validate each trade entry
        valid_trades = []
        for i, trade in enumerate(data):
            if not isinstance(trade, dict):
                print(f"Warning: Trade {i} is not a dictionary, skipping")
                continue

            # Adjust based on your trade structure
            required_keys = ['symbol', 'pnl']
            is_valid, error_msg = validate_json_structure(
                trade, required_keys=required_keys)

            if is_valid:
                valid_trades.append(trade)
            else:
                print(f"Warning: Invalid trade {i}: {error_msg}")

        return valid_trades
    except FileNotFoundError:
        print(f"Trade log file not found: {log_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in trade log file {log_path}: {e}")
        return []
    except Exception as e:
        print(f"Error loading trades from {log_path}: {e}")
        return []


def analyze_log():
    # List of dicts with pnl, signal, strategy, etc.
    trades = load_all_trades()

    past_failures = [t for t in trades if t['pnl'] < 0]
    past_successes = [t for t in trades if t['pnl'] > 0]

    prompt = PromptTemplate(
        input_variables=["failures", "successes"],
        template="""
    You are an AI trading advisor.
    Here are trades that failed:
    {failures}

    And trades that succeeded:
    {successes}

    Please identify:
    - Common reasons for failure.
    - Strategy-symbol pairs to avoid.
    - Adjustments to make to strategy logic or parameters.
    - Suggest new stock-strategy combinations worth trying.

    Output structured improvement ideas.
    """
    )

    llm_input = prompt.format(
        failures="\n".join(str(f) for f in past_failures),
        successes="\n".join(str(s) for s in past_successes)
    )

    response = llm.invoke(llm_input)
    print(response.content)

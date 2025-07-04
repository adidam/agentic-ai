from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import json
import os

model = "llama3-8b-8192"

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name=model,
    temperature=0.3
)


def log_trade_decision_json(trade_data, log_file='logs/trade_decisions.jsonl'):
    """
    Appends a trade decision (dict) as JSON to a .jsonl (JSON Lines) file.
    Each line is a separate JSON object.
    """
    with open(log_file, 'a') as f:
        json.dump(trade_data, f)
        f.write('\n')  # Each JSON object on a new line


def load_all_trades(log_path: str = 'logs/trades_log.json'):
    with open(log_path) as f:
        data = json.load(f)
    return data


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

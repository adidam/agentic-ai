from langchain_core.prompts import PromptTemplate
import json


def load_all_trades(log_path: str = 'logs/trade_log_2025-06-15'):
    with open(log_path) as f:
        data = json.load(f)
    return data


trades = load_all_trades()  # List of dicts with pnl, signal, strategy, etc.

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

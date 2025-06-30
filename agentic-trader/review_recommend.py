from langchain_core.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI  # or Groq

llm = ChatOpenAI(model="gpt-4o")

prompt = PromptTemplate(
    input_variables=["benchmark"],
    template="""
You are a financial trading analyst AI. You've been given backtest results for multiple trading strategies across different stocks.

Here is the benchmark data:
{benchmark}

Your task:
1. Identify the top 2 performing strategies.
2. Identify which securities work best with which strategies.
3. Recommend the best strategy-symbol pair to trade going forward.
4. If a strategy performed poorly, explain why it might have failed (e.g., low volatility, few signals).
5. Recommend improvements or modifications.

Output your reasoning in detail, followed by final recommendations in this format:

### Top Strategy: {strategy_name}
### Best Stock: {stock_symbol}
### Suggested Improvements: ...
"""
)

benchmark_summary = "\n".join(
    [f"{r['strategy']} on {r['symbol']}: PnL ₹{r['total_pnl']}, Win Rate {r['win_rate']}%" for r in benchmark_results])

llm_input = prompt.format(benchmark=benchmark_summary)
response = llm.invoke(llm_input)
print(response.content)

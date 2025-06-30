from langchain.prompts import ChatPromptTemplate
from llm_router import get_llm


def run_agent(ohlc_data, volume, provider="openai"):
    llm = get_llm(provider)

    template = ChatPromptTemplate.from_messages([
        ("system", "You are a trading decision agent that gives cautious, well-reasoned advice."),
        ("human",
         "Based on OHLC data: {ohlc} and volume: {volume}, should I BUY, SELL, or HOLD? Respond with one word and a reason.")
    ])

    chain = template | llm
    response = chain.invoke({"ohlc": ohlc_data, "volume": volume})
    return response.content

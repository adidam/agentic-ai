from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(provider="local", model="llama3-70b-8192"):
    if provider == "groq":
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=model          # "mistral-saba-24b"
        )
    elif provider == "openai":
        return ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.4,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    else:
        return ChatOpenAI(
            base_url="http://localhost:1234/v1",    # or whatever port LM Studio uses
            api_key="api_key",                      # just a dummy, required by OpenAI SDK
            # optional if your server only exposes one model
            model="microsoft/phi-4-mini-reasoning"
        )


def ask_llm(prompt_text: str, provider="local", model="llama3-70b-8192"):
    """
    Query an LLM (OpenAI or Groq) with a given prompt and return the response.

    :param prompt_text: The user input or prompt to be passed to the LLM.
    :param provider: 'openai' or 'groq'
    :param model: model name (e.g., 'gpt-4o', 'llama3-70b-8192', etc.)
    :return: LLM response as a string
    """
    print(f"{provider}, {model}")
    llm = get_llm(provider=provider, model=model)
    if not llm:
        raise ValueError(f"Unsupported provider: {provider}")

    prompt = ChatPromptTemplate.from_template(
        "You are a helpful trading assistant. {prompt}")
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"prompt": prompt_text})
    return response

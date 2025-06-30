from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()


def get_llm(provider="openai"):
    if provider == "groq":
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="mistral-saba-24b"
        )
    else:
        return ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.4,
            api_key=os.getenv("OPENAI_API_KEY")
        )


def ask_llm(prompt_text: str, provider="groq", model="llama3-70b-8192"):
    """
    Query an LLM (OpenAI or Groq) with a given prompt and return the response.

    :param prompt_text: The user input or prompt to be passed to the LLM.
    :param provider: 'openai' or 'groq'
    :param model: model name (e.g., 'gpt-4o', 'llama3-70b-8192', etc.)
    :return: LLM response as a string
    """
    if provider == "openai":
        llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=model,
            temperature=0.3
        )
    elif provider == "groq":
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=model,
            temperature=0.3
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    prompt = ChatPromptTemplate.from_template(
        "You are a trading assistant. {prompt}")
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"prompt": prompt_text})
    return response

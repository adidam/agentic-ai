import unittest
from dotenv import load_dotenv
import os

load_dotenv(override=True)

LANGSMITH_TRACING = True
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = "adidam-agentic-trader"


if __name__ == "__main__":
    unittest.main(module=None, defaultTest='discover')

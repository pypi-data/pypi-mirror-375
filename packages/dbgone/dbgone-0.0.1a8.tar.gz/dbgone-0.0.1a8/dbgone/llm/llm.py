import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-2024-11-20")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

if not OPENAI_API_KEY:
    UserWarning("OPENAI_API_KEY not found in environment variables.")
if not OPENAI_API_BASE:
    UserWarning("OPENAI_API_BASE not found in environment variables.")


def get_llm(
    model_name: str = MODEL_NAME,
    *,
    temperature: float = 0.7,
    max_completion_tokens: int = 8000,
    **kwargs
) -> ChatOpenAI:
    """
    获取大语言模型实例
    Args:
        - model_name: 模型名称，默认为 gpt-4o-2024-11-20
        - temperature: 生成的文本的随机性，默认为 0.7
        - max_completion_tokens: 生成的文本的最大长度，默认为 8000
        - **kwargs: 其他参数，将传递给 ChatOpenAI 实例

    Returns:
        - llm: 大语言模型实例
    """

    llm = ChatOpenAI(
        model=model_name,
        max_completion_tokens=max_completion_tokens,
        temperature=temperature,
        **kwargs,
    )

    return llm


__all__ = ["get_llm"]

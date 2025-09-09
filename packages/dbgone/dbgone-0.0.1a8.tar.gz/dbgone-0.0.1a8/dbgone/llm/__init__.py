from .llm import get_llm
from .prompts import AnalysisPromptCreator

def generate_analysis_content(content: str):
    prompt = AnalysisPromptCreator.create_prompt()
    llm = get_llm(temperature=0.3) # temperature = 0.3 严谨， temperature = 0.7 自由发挥
    chain = prompt | llm
    output = chain.invoke({'content': content})
    if str(output).startswith("<think></think>\n"):
        output = str(output).replace("<think></think>\n", "")
    return output

__all__ = ["generate_analysis_content"]
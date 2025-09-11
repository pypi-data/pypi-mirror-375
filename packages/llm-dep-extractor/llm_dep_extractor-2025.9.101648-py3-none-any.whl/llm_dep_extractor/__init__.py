# __init__.py
# Minimal Python package: llm_dep_extractor
from typing import List

from llmatch_messages import llmatch
from langchain_llm7 import ChatLLM7
from langchain_core.messages import SystemMessage, HumanMessage

__all__ = ["extract_required_pip_packages"]

def extract_required_pip_packages(code_text: str, llm: ChatLLM7, max_packages: int = 10) -> List[str]:
    """
    Extract 10 required pip package names from a code snippet using an injected ChatLLM7 model
    and llmatch. Returns a list of exactly max_packages unique, lowercase, underscore-delimited
    package names, in the order they appear.

    Parameters:
    - code_text: The source code to analyze (str).
    - llm: An instance of ChatLLM7 to be used by the llm-based extraction routine (dependency injection).
    - max_packages: Number of package names to extract (default 10).

    Returns:
    - List[str]: Exactly max_packages package names.

    Raises:
    - RuntimeError: If the extraction or subsequent sanitization steps fail to produce
      the required number of valid names.
    """
    if not isinstance(code_text, str):
        raise TypeError("code_text must be a string.")
    if llm is None:
        raise TypeError("llm (ChatLLM7 instance) must be provided.")

    # Regex to extract names like <name>pkg_name</name>
    pattern = r"<name>\s*([a-z0-9_]+)\s*</name>"

    system = SystemMessage(
        content=(
            "you are a dependency-extraction assistant. "
            "output ONLY an xml fragment containing exactly 10 <name> elements, "
            "each with a lowercase, underscore-separated package name (no spaces or special chars). "
            "format: <names> <name>pkg_name</name> ... </names>"
        )
    )

    human_content = (
        "Source code (for dependency extraction):\n"
        f"{code_text}\n\n"
        "Metadata:\n"
        "Return ONLY the 10 <name> elements in the XML as described. No additional text."
    )
    human = HumanMessage(content=human_content)

    response = llmatch(
        llm=llm,
        messages=[system, human],
        pattern=pattern,
        verbose=False,
    )

    if not (isinstance(response, dict) and response.get("success")):
        raise RuntimeError("Name generation failed via llmatch/ChatLLM7.")

    extracted: List[str] = response.get("extracted_data") or []
    if len(extracted) < max_packages:
        raise RuntimeError("Insufficient <name> elements extracted from LLM response.")

    # deduplicate while preserving order
    seen = set()
    result: List[str] = []
    for raw in extracted:
        if raw and raw not in seen:
            seen.add(raw)
            result.append(raw)

    if len(result) < max_packages:
        raise RuntimeError("Not enough unique, valid package names extracted.")

    return result[:max_packages]
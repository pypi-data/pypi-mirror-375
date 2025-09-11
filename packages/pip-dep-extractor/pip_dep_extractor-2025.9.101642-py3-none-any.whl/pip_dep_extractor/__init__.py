# __init__.py
from typing import List
import re

from llmatch_messages import llmatch
from langchain_llm7 import ChatLLM7
from langchain_core.messages import SystemMessage, HumanMessage


def extract_pip_dependencies(llm: ChatLLM7, custom_text: str) -> List[str]:
    """
    Extract 10 Python package names from an LLM response via llmatch.

    Dependency injection: accepts a ChatLLM7 instance as `llm`.
    Uses llmatch with a regex to extract exactly 10 <name> elements from the LLM's XML response.
    Names must be lowercase alphanumeric with underscores only.
    Returns a deduplicated list of 10 names, preserving order.
    Raises RuntimeError on failure conditions.
    """
    system = SystemMessage(
        content=(
            "You are a helper that generates Python package names. "
            "Rules: lowercase only; underscores instead of spaces; no special characters. "
            "Output MUST be exactly 10 <name> elements within this XML wrapper. "
            "<names>\n"
            "  <name>example_one</name>\n"
            "  <name>example_two</name>\n"
            "  ...\n"
            "  <name>example_ten</name>\n"
            "</names>"
        )
    )

    human_content = (
        "Source/package description (custom_text):\n"
        f"{custom_text}\n\n"
        "Metadata:\n"
        "Return ONLY XML as specified. No comments or additional text."
    )
    human = HumanMessage(content=human_content)

    pattern = r"<name>\s*([a-z0-9_]+)\s*</name>"

    response = llmatch(
        llm=llm,
        messages=[system, human],
        pattern=pattern,
        verbose=False,
    )

    if not (isinstance(response, dict) and response.get("success")):
        raise RuntimeError("Name generation failed via llmatch/ChatLLM7.")

    extracted: List[str] = response.get("extracted_data") or []
    if not extracted:
        raise RuntimeError("No <name> elements extracted from LLM response.")

    seen = set()
    result: List[str] = []
    for raw in extracted:
        if raw and raw not in seen and re.match(r"^[a-z0-9_]+$", raw):
            seen.add(raw)
            result.append(raw)

    if len(result) == 0:
        raise RuntimeError("All extracted names were invalid after sanitization.")

    if len(result) < 10:
        raise RuntimeError("Fewer than 10 valid names extracted from LLM response.")

    return result[:10]
from typing import TYPE_CHECKING

import tiktoken

from zero_sum.config import config

if TYPE_CHECKING:
    from zero_sum.models import Document


def count_tokens(doc: "Document") -> int:
    """Count the number of tokens in a document."""
    try:
        enc = tiktoken.encoding_for_model(config.LLM_MODEL)
    except KeyError:
        enc = tiktoken.encoding_for_model("cl100k_base")
    return len(enc.encode(doc.text))

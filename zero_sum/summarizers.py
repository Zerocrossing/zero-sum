from typing import List

from zero_sum.agents import SummarizeAgent
from zero_sum.config import config
from zero_sum.logging import logger
from zero_sum.models import Document

# sublogger name of summarizer
logger = logger.getChild("summarizer")

# TODO add some kind of progress tracker. Maybe a queue or a progress callback
class Summarizer:
    def __init__(self, document: Document):
        self.document = document
        self.summarized_document: Document | None = None
        logger.info(f"Summarizer initialized with document of {len(document)} tokens")

    def _get_agent(self):
        return SummarizeAgent(self.document)

    def summarize(self, doc: Document | None = None) -> Document:
        """Summarize
        Summarize a document using an LLM.
        The output will be a single document, summarizing the contents
        of the original while being smaller.
        """
        if doc is None:
            doc = self.document
        split_docs = self._split_document(doc)
        logger.info(f"Split document into {len(split_docs)} parts. Summarizing each...")
        summarized_docs = []
        for n, split_doc in enumerate(split_docs):
            original_length = len(split_doc)
            agent = self._get_agent()
            split_doc.text = agent.send_message(split_doc.text)
            summarized_docs.append(split_doc)
            logger.info(f"\t Part {n + 1}: {original_length} -> {len(split_doc)} tokens")
        self.summarized_document = self._merge_split_documents(summarized_docs)
        logger.info(f"Summarized document to {len(self.summarized_document)} tokens")
        return self.summarized_document

    def summarize_to_token_limit(
        self,
        token_limit: int | None = None,
        max_iters: int = 10,
    ) -> Document:
        """Summarize to Token Limit

        Summarizes the document continually until it reaches the token limit.
        """
        if token_limit is None:
            token_limit = config.FINAL_TOKEN_LIMIT
        logger.info(f"Summarizing to token limit of {token_limit} tokens")
        doc = self.document.model_copy(deep=True)
        prev_token_count = len(doc)
        for i in range(max_iters):
            doc = self.summarize(doc)
            logger.info(f"Iteration {i}: Summarized to {len(doc)} tokens")
            if len(doc) < token_limit:
                logger.info("Summarized to token limit. Stopping.")
                break
            diff = abs(prev_token_count - len(doc))
            logger.debug(f"Tokens reduced by: {diff}")
            if diff < prev_token_count * 0.1:
                logger.info("Difference is less than 10%. Stopping.")
                break
            prev_token_count = len(doc)
        return doc

    def _agent_message_hook(self, agent: SummarizeAgent, doc: Document | None) -> None:
        """Agent Message Hook

        Called on each split document to potentially add context
        to the summarize agent. This can be accomplished by prepending a
        message to the message history using `add_message()` function on the agent
        or modifying the agent's prompt directly setting `agent.prompt`.

        May be overridden by subclasses.
        """
        ...

    def _merge_split_documents(self, documents: List[Document]) -> Document:
        """Merge Documents
        Merge a list of documents into a single document.
        It assumes the documents were split from a single document.
        As such their metadata and tags are assumed to be the same.
        """
        first_doc = documents[0]
        text = " ".join([doc.text for doc in documents])
        first_doc.text = text
        return first_doc

    def _split_document(self, doc: Document) -> List[Document]:
        """Split Document
        Split a document into a list of documents recursively
        """
        if len(doc) < config.DOCUMENT_CHUK_TOKENS:
            return [doc]

        # Split the document roughly in two with some padding
        words = doc.text.split()
        half = len(words) // 2

        doc1 = doc.model_copy()
        doc2 = doc.model_copy()

        doc1.text = " ".join(words[:half])
        doc2.text = " ".join(words[half:])

        split_docs = []

        if len(doc1) > config.DOCUMENT_CHUK_TOKENS:
            split_docs.extend(self._split_document(doc1))
        else:
            split_docs.append(doc1)

        if len(doc2) > config.DOCUMENT_CHUK_TOKENS:
            split_docs.extend(self._split_document(doc2))
        else:
            split_docs.append(doc2)

        return split_docs

    def _calculate_number_of_splits(self):
        """Calculate Number of Splits
        Calculate the number of splits required to summarize the document
        """
        doc_tokens = len(self.document)
        return doc_tokens // config.DOCUMENT_CHUK_TOKENS + 1

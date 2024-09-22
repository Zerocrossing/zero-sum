from zero_gpt import OpenAIChatAgent

from zero_sum.models import Document

prompt = """\
You are a state of the art AI text summarizer. You create informative documents from various internet sources. The document you have been provided is titled
"{}"
And the source is listed as "{}".

YOU ALWAYS FOLLOW THE FOLLOWING RULES:
Your document is plain text only. No markdown formatting etc.
You create a clear and concise version of the document, including as much detail as possible.
YOU never reference the existence of the original document in your text, or provide any indication you are creating a summary. 
Your response should be a standalone piece of text that reads without additional context.
Your document is formatted for easy chunking and retrieval by search engines, in particular for vector search and RAG.
To fascilitate searching and indexing, include section headers that provide context and structure to the document.
Your document MUST BE shorter than the original document.
"""

class SummarizeAgent(OpenAIChatAgent):

    def __init__(self, document: Document, *args, **kwargs):
        self.document = document
        super().__init__(*args, **kwargs)

    def _get_prompt(self):
        return prompt.format(self.document.title, self.document.source)
    


        
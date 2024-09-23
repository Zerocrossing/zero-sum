import re
from pathlib import Path
from typing import List, Optional
from uuid import UUID, uuid4

from goose3 import Goose
from pydantic import BaseModel, Field
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from zero_sum.helpers import youtube_id_from_url
from zero_sum.tokenizers import count_tokens


class Document(BaseModel):
    uuid: UUID = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the document",
    )
    title: str = Field(default=..., description="Title of the document")
    text: str = Field(default=..., description="Text content of the document")
    url: Optional[str] = Field(
        default=None,
        description="URL where the document was retrieved from",
    )
    source: Optional[str] = Field(
        default=None, description="Source of the document, youtube, text file etc."
    )
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Vector embedding of the document",
    )
    collection: Optional[str] = Field(
        default=None,
        description="Collection the document belongs to. Also known as Namespace depending on the vector Database",
    )
    tags: List[str] = Field(
        default=[],
        description="List of tags associated with the document",
    )
    metadata: dict = Field(
        default={},
        description="Additional metadata associated with the document",
    )

    @classmethod
    def from_text(cls, text: str, title: str, **kwargs) -> "Document":
        """From Text
        Create a document from text.
        """
        doc = cls(title=title, text=text, **kwargs)
        doc.source = "text"
        return doc

    @classmethod
    def from_file(cls, path: Path, **kwargs) -> "Document":
        """From File
        Create a document from a file.
        """
        with open(path, "r") as file:
            text = file.read()
        if "title" not in kwargs:
            kwargs["title"] = path.stem
        doc = cls(text=text, **kwargs)
        doc.source = "file"

    @classmethod
    def from_files(cls, paths: list[Path]) -> List["Document"]:
        """From Files
        Create documents from a list of files.
        """
        return [cls.from_file(path) for path in paths]

    @classmethod
    def from_website(cls, url: str, **kwargs) -> "Document":
        """From URL
        Create a document from a URL using Goose
        """
        g = Goose()
        article = g.extract(url=url)

        if "title" not in kwargs:
            kwargs["title"] = article.title

        doc = cls(title=article.title, text=article.cleaned_text, url=url, **kwargs)
        doc.source = "website"
        doc.url = url

    @classmethod
    def from_youtube(cls, url: str, **kwargs) -> "Document":
        """From Youtube
        Create a document from a youtube video
        """
        youtube_id = youtube_id_from_url(url)
        # transcript api is better at getting transcript
        transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript)
        # pytube gets the title. This is somewhat redundant. Look into a single library that gets both reliably
        yt = YouTube(url)
        doc = cls(title=yt.title, text=text, url=url, source="youtube", **kwargs)
        return doc

    @property
    def is_embedded(self) -> bool:
        return self.embedding is not None

    def __len__(self):
        return count_tokens(self)

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __str__(self):
        return f"Document: {self.title} ({len(self)} tokens)"

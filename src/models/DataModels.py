from dataclasses import dataclass
from datetime import datetime


@dataclass
class AIResponse:
    text: str
    link: str
    hashtags: list[str]


@dataclass
class DocumentCreate:
    """Input for creating a document"""

    text: str
    link: str
    hashtags: list[str]


@dataclass
class Document:
    """Stored document"""

    id: int
    text: str
    link: str
    hashtags: list[str]
    embedding: list[float]
    created_at: datetime
    modified_at: datetime


@dataclass
class DocumentSearchResult:
    """Document with similarity score"""

    id: int
    text: str
    link: str
    hashtags: list[str]
    created_at: datetime
    modified_at: datetime
    similarity: float = 0.0

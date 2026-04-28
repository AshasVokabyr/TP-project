from dataclasses import dataclass
from typing import List


@dataclass
class Article:
    url: str
    title: str
    content: str

@dataclass
class DigestPost:
    text: str
    article_urls: List[str]
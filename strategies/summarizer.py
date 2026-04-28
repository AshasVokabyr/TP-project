from abc import ABC, abstractmethod
from typing import List

from models import Article


class SummarizerStrategy(ABC):
    @abstractmethod
    def summarize(self, articles: List[Article]) -> str:
        pass

class SimpleListSummarizer(SummarizerStrategy):
    def summarize(self, articles: List[Article]) -> str:
        if not articles:
            return "Нет новых статей за последние 20 часов."

        lines = ["**Технологические новости**\n"]
        for i, article in enumerate(articles[:5], 1):
            title = article.title.replace('_', '\\_').replace('*', '\\*')
            lines.append(f"{i}. [{title}]({article.url})")

        return "\n".join(lines)
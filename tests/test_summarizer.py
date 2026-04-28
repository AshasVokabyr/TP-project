import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from strategies.summarizer import SimpleListSummarizer
from models.article import Article

def test_summarizer_empty():
    summarizer = SimpleListSummarizer()
    result = summarizer.summarize([])
    assert result == "Нет новых статей за последние 20 часов."

def test_summarizer_single_article():
    summarizer = SimpleListSummarizer()
    article = Article(
        url="https://example.com",
        title="Test News",
        content=""
    )
    result = summarizer.summarize([article])
    expected = "**Технологические новости**\n\n1. [Test News](https://example.com)"
    assert result == expected

def test_summarizer_escapes_markdown():
    summarizer = SimpleListSummarizer()
    article = Article(
        url="https://example.com",
        title="AI_*_News",
        content=""
    )
    result = summarizer.summarize([article])
    # Должно экранировать * и _
    assert "\\_" in result
    assert "\\*" in result
    assert "AI\\_\\*\\_News" in result

def test_summarizer_limits_to_5():
    summarizer = SimpleListSummarizer()
    articles = [
        Article(url=f"https://{i}.com", title=f"News {i}", content="")
        for i in range(10)
    ]
    result = summarizer.summarize(articles)
    # Должно быть ровно 5 пунктов
    lines = result.strip().split('\n')
    content_lines = [line for line in lines if line.startswith(('1.', '2.', '3.', '4.', '5.'))]
    assert len(content_lines) == 5
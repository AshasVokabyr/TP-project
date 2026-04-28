import logging
from typing import Optional

from models import DigestPost
from repositories import SQLitePostRepository
from strategies import IngestionStrategy, SummarizerStrategy


class DigestGenerator:
    def __init__(
        self,
        ingestion_strategy: IngestionStrategy,
        summarizer: SummarizerStrategy,
        repository: SQLitePostRepository
    ):
        self.ingestion = ingestion_strategy
        self.summarizer = summarizer
        self.repo = repository

    async def run(self) -> Optional[int]:
        logging.info("Starting digest generation...")
        articles = await self.ingestion.fetch_articles(hours_back=20)
        if not articles:
            logging.warning("No articles found. Skipping.")
            return None

        digest_text = self.summarizer.summarize(articles)
        post = DigestPost(
            text=digest_text,
            article_urls=[a.url for a in articles]
        )
        post_id = await self.repo.save_digest(post)
        logging.info(f"Digest saved with ID: {post_id}")
        return post_id
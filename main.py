import asyncio
import logging
import aiosqlite

from core.digest_generator import DigestGenerator
from repositories import SQLitePostRepository
from strategies import TechCrunchIngestionStrategy, SimpleListSummarizer


async def main():
    logging.basicConfig(level=logging.INFO)
    ingestion = TechCrunchIngestionStrategy("https://techcrunch.com/")
    summarizer = SimpleListSummarizer()
    repo = SQLitePostRepository("digests.db")
    await repo.init_db()

    generator = DigestGenerator(ingestion, summarizer, repo)
    post_id = await generator.run()

    if post_id:
        print(f"Digest saved locally with ID: {post_id}")
        async with aiosqlite.connect("digests.db") as db:
            cursor = await db.execute("SELECT text FROM digest_posts WHERE id = ?", (post_id,))
            row = await cursor.fetchone()
            if row:
                print("\nGenerated digest:\n")
                print(row[0])
    else:
        print("No digest generated")

if __name__ == "__main__":
    asyncio.run(main())
import aiosqlite

from models import DigestPost


class SQLitePostRepository:
    def __init__(self, db_path: str = "digests.db"):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS digest_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    article_urls TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

    async def save_digest(self, post: DigestPost) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO digest_posts (text, article_urls) VALUES (?, ?)",
                (post.text, ",".join(post.article_urls))
            )
            await db.commit()
            return cursor.lastrowid
import asyncio
from datetime import datetime, timedelta
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
import aiohttp
import pytz
from bs4 import BeautifulSoup

from models import Article


class IngestionStrategy(ABC):
    @abstractmethod
    async def fetch_articles(self, hours_back: int = 20) -> List[Article]:
        pass

class TechCrunchIngestionStrategy(IngestionStrategy):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.moscow_tz = pytz.timezone('Europe/Moscow')
        self.http_timeout = 10
        self.max_retries = 2

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        for attempt in range(1, self.max_retries + 1):
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.http_timeout)) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    logging.warning(f"HTTP {resp.status} for {url}")
                    return None
            except asyncio.TimeoutError:
                if attempt == self.max_retries:
                    logging.error(f"Timeout after {self.max_retries} attempts: {url}")
                    return None
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error fetching {url}: {e}")
                return None
        return None

    async def fetch_articles(self, hours_back: int = 20) -> List[Article]:
        cutoff = datetime.now(self.moscow_tz) - timedelta(hours=hours_back)
        articles = []

        async with aiohttp.ClientSession() as session:
            main_html = await self._fetch(session, self.base_url)
            if not main_html:
                return []

            soup = BeautifulSoup(main_html, 'html.parser')
            for card in soup.find_all('div', class_='loop-card__content'):
                try:
                    title_link = card.find('h3', class_='loop-card__title').find('a')
                    time_elem = card.find('time')
                    if not title_link or not time_elem:
                        continue

                    url = title_link['href']
                    dt = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                    dt = dt.astimezone(self.moscow_tz)

                    if dt < cutoff:
                        continue

                    articles.append(Article(
                        url=url,
                        title=title_link.get_text().strip(),
                        content=""
                    ))
                except Exception as e:
                    logging.error(f"Error parsing article card: {e}")
                    continue

        logging.info(f"Fetched {len(articles)} articles from TechCrunch")
        return articles

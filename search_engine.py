import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from text_processor import TextProcessor
import os
from dotenv import load_dotenv

load_dotenv('.env')

class SearchEngine:
    def __init__(self, textProcessor: TextProcessor):
        self.api_key = os.getenv("GOOGLEAPI")
        self.search_engine_id = os.getenv("SEARCHKEY")
        self.textProcessor = textProcessor
        self.semaphore = None  # будет создана при запуске

        # Словарь источников по языкам
        self.language_sources = {
            "en": [
                "bbc.com", "cnn.com", "reuters.com", 
                "financialpost.com", "foxnews.com"
            ],
            "uk": [
                "pravda.com.ua", "unian.ua", "tsn.ua", 
                "suspilne.media", "zn.ua"
            ]
        }

    async def fetch(self, session, url):
        async with self.semaphore:
            async with session.get(url) as response:
                return await response.json()

    async def __search(self, query, date, lang):


        self.semaphore = asyncio.Semaphore(5)

        sources = self.language_sources.get(lang, self.language_sources["en"])  

        found_news = []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for source in sources:
                url = (
                    f"https://www.googleapis.com/customsearch/v1?q={query}"
                    f"&key={self.api_key}&cx={self.search_engine_id}"
                    f"&siteSearch={source}&num=5"
                )
                if date:
                    url += f"&dateRestrict={date}"
                tasks.append(self.fetch(session, url))

            responses = await asyncio.gather(*tasks)
            urls_to_parse = []
            for results in responses:
                if "items" in results:
                    for item in results["items"]:
                        news_url = item.get("link", "")
                        urls_to_parse.append(news_url)

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                parsed_results = await loop.run_in_executor(
                    executor, self.parse_multiple_urls, urls_to_parse, lang
                )

            found_news.extend(parsed_results)
        return found_news

    def parse_multiple_urls(self, urls, lang):
        parsed_news = []
        for url in urls:
            news_title, news_text, news_date = self.textProcessor.parse(url)
            if news_text:
                news_text = self.textProcessor.preprocess_text(news_text, lang)
                parsed_news.append(news_text)
        return parsed_news

    def search(self, query, date=None, lang="en"):
        return asyncio.run(self.__search(query, date, lang))

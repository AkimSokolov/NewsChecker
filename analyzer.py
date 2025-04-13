import numpy as np
import os
from dotenv import load_dotenv
import requests
import joblib
from urllib.parse import urlparse
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from db import Database
from text_processor import TextProcessor
from message_processor import MessageProcessor
from search_engine import SearchEngine
from langdetect import detect

import time

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Функция {func.__name__} выполнялась {end_time - start_time:.6f} секунд")
        return result
    return wrapper

class Analyzer:

    def __init__(self, textProcessor, dataBase, searchEngine):
        load_dotenv(".env")

        np.random.seed(42)
        self.model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        self.stop_words = set(stopwords.words("english"))

        self.db = dataBase
        self.textProcessor = textProcessor
        self.search_engine = searchEngine
        
        self.provokingModel = joblib.load("./models/fake_news_model.pkl")
        self.vectorizer = joblib.load("./models/tfidf_vectorizer.pkl")

    @timer
    def verify_news_by_link(self, url):
        news_analysis_check = self.db.get_news_analysis(url)
        if news_analysis_check:
            news_reliability_score = news_analysis_check[0]
            source_reliability_score = news_analysis_check[1]
            provoking_rate = news_analysis_check[2]
            return news_reliability_score, source_reliability_score, provoking_rate

        title, text, date = self.textProcessor.parse(url)
        language = detect(text)

        title = self.textProcessor.preprocess_text(title, language)
        text = self.textProcessor.preprocess_text(text, language)

      

        news_reliability_score, is_reliable = self.__get_news_reliability(title, text, date)
        source_reliability_score = self.__get_source_reliability(url, is_reliable)
        provoking_rate = self.__get_provoking_rate(text)

        self.db.add_news_analysis(url, news_reliability_score, source_reliability_score, provoking_rate)
        return news_reliability_score, source_reliability_score, provoking_rate

    def verify_news_by_text(self, text):
        date = self.textProcessor.extract_date_from_text(text)
        text = self.textProcessor.preprocess_text(text)

        news_reliability_score = self.__get_news_reliability(text, text, date)
        provoking_rate = self.__get_provoking_rate(text)

        return news_reliability_score, provoking_rate

    def process_source(self, domain, isKnown, news_reliability_score):
        if isKnown and self.db.check_in_other_sources(domain):
            if news_reliability_score > 0.7:
                pass

    def __get_source_reliability(self, url, is_reliable):
        parsed_url = urlparse(url).netloc
        domain = parsed_url.replace("www.", "")
        is_known = False

        if self.db.check_in_reliable_sources(domain):
            is_known = True
            return 1.0

        if self.db.check_in_satirical_sources(domain):
            is_known = True
            return 2.0

        if self.db.check_in_unreliable_sources(domain):
            is_known = True
            return 0.0

        if self.db.check_in_other_sources(domain):
            is_known = True
            self.db.add_to_other_sources(domain, is_reliable)
            score = self.db.get_reliability_score(domain)
            if score:
                return score
            return 0

        if not is_known:
            self.db.add_to_other_sources(domain, is_reliable)

        return 0.5

    def __get_news_reliability(self, title, text, date):
        related_news = self.search_engine.search(title, date)
        if related_news:
            reliability_score = self.__compare(text, related_news)
            return reliability_score, reliability_score >= 0.7
        return 0, False

    def __compare(self, text, news):
        text_embeddings = self.model.encode([text])
        news_embeddings = self.model.encode(news)

        similarities = cosine_similarity(text_embeddings, news_embeddings).flatten()
        best_match_index = int(np.argmax(similarities))
        best_match_score = similarities[best_match_index]

        return best_match_score

    def __get_provoking_rate(self, text):
        text_vectorized = self.vectorizer.transform([text])
        prediction = self.provokingModel.predict_proba(text_vectorized)[0][1]
        return prediction

    @timer
    def __search_fact_on_google(self, query, date):
        api_key = os.getenv("GOOGLEAPI")
        search_engine_id = os.getenv("SEARCHKEY")
        sources = ["bbc.com", "cnn.com", "reuters.com"]
        found_news = []

        for source in sources:
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={search_engine_id}&siteSearch={source}"
            if date:
                url += f"&dateRestrict={date}"

            response = requests.get(url)
            results = response.json()

            if "items" in results:
                for item in results["items"]:
                    news_url = item.get("link", "")
                    news_title, news_text, news_date = self.textProcessor.parse(news_url)

                    if news_text:
                        news_text = self.textProcessor.preprocess_text(news_text)
                        found_news.append(news_text)

        return found_news

if __name__ == "__main__":
    url = "https://www.bbc.com/news/articles/clyjv8e49deo"
    analyzer = Analyzer()
    analyzer.verify_news_by_link(url)

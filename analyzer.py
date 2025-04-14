import numpy as np
from dotenv import load_dotenv
import joblib
from urllib.parse import urlparse
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from db import Database
from text_processor import TextProcessor
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
    def __init__(self, textProcessor: TextProcessor, dataBase: Database, searchEngine: SearchEngine):
        load_dotenv(".env")
        np.random.seed(42)

        self.model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        self.db = dataBase
        self.textProcessor = textProcessor
        self.search_engine = searchEngine
        self.language_models = {
            "en": {
                "model": joblib.load("./models/fake_news_model_en.pkl"),
                "vectorizer": joblib.load("./models/tfidf_vectorizer_en.pkl"),
            },
            "uk": {
                "model": joblib.load("./models/fake_news_model_uk.pkl"),
                "vectorizer": joblib.load("./models/tfidf_vectorizer_uk.pkl"),
            },
        }

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
        text = self.textProcessor.preprocess_text(text, language)

        news_reliability_score, is_reliable = self.__get_news_reliability(title, text, date, language)
        source_reliability_score = self.__get_source_reliability(url, is_reliable)
        provoking_rate = self.__get_provoking_rate(text, language)

        self.db.add_news_analysis(url, news_reliability_score, source_reliability_score, provoking_rate)
        return news_reliability_score, source_reliability_score, provoking_rate

    def verify_news_by_text(self, text):
        language = detect(text)
        date = self.textProcessor.extract_date_from_text(text)
        text = self.textProcessor.preprocess_text(text, language)

        news_reliability_score, _ = self.__get_news_reliability(text, text, date, language)
        provoking_rate = self.__get_provoking_rate(text, language)

        return news_reliability_score, provoking_rate

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
            return score if score else 0

        if not is_known:
            self.db.add_to_other_sources(domain, is_reliable)

        return 0.5

    def __get_news_reliability(self, title, text, date, lang):
        related_news = self.search_engine.search(title, date, lang)
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

    def __get_provoking_rate(self, text, lang):
        model_data = self.language_models.get(lang, self.language_models["en"])
        vectorizer = model_data["vectorizer"]
        model = model_data["model"]

        text_vectorized = vectorizer.transform([text])
        prediction = model.predict_proba(text_vectorized)[0][1]
        return prediction


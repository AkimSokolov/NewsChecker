import os
from dotenv import load_dotenv
import json

load_dotenv()

DEFAULT_LANG = os.getenv("DEFAULT_LANGUAGE", "en")
LOCALES_DIR = os.path.join(os.path.dirname(__file__), "messages")


class MessageProcessor:
    _loaded_messages = {}

    def __init__(self, lang: str = None):
        self.lang = lang or DEFAULT_LANG
        self.messages = self.load_messages_for_user(self.lang)

    def set_language(self, lang):
        self.lang = lang
        self.messages = self.load_messages_for_user(self.lang)
    @classmethod
    def load_messages_for_user(cls, lang: str = None) -> dict:
        lang = lang or DEFAULT_LANG

        if lang in cls._loaded_messages:
            return cls._loaded_messages[lang]

        file_path = os.path.join(LOCALES_DIR, f"{lang}.json")
        if not os.path.isfile(file_path):
            file_path = os.path.join(LOCALES_DIR, f"{DEFAULT_LANG}.json")

        try:
            with open(file_path, encoding="utf-8") as f:
                cls._loaded_messages[lang] = json.load(f)
        except Exception as e:
            print(f"Failed to load language file '{file_path}': {e}")
            cls._loaded_messages[lang] = {}

        return cls._loaded_messages[lang]

    def link_analysis(self, news_reliability_score, source_reliability_score, provoking_rate):
        if source_reliability_score == 2:
            return self.satirical()
        news_reliability_message = self.news_reliability(news_reliability_score)
        source_reliability_message = self.source_reliability(source_reliability_score)
        provoking_rate_message = self.provoking_rate(provoking_rate)

        fake_probability_message = self.fake_probability_message(news_reliability_score, source_reliability_score, provoking_rate)

        message_to_user = news_reliability_message + "\n" + source_reliability_message + "\n" + provoking_rate_message + "\n\n" + fake_probability_message
        return message_to_user

    def text_analysis(self, news_reliability_score, provoking_rate):
        news_reliability_message = self.news_reliability(news_reliability_score)
        provoking_rate_message = self.provoking_rate(provoking_rate)
        fake_probability_message = self.fake_probability_message(news_reliability_score, 0.5, provoking_rate)

        message_to_user = news_reliability_message + "\n" + provoking_rate_message + "\n\n" + fake_probability_message
        return message_to_user

    def satirical(self):
        return self.messages["COMPLETE_ANALYSIS_SATIRICAL"]

    def news_reliability(self, score):
        text_score = str(round(score * 100, 1)) + "%"
        if score > 0.7:
            return self.messages["COMPLETE_ANALYSIS_NEWS_RELIABILITY_GOOD"].format(news_score=text_score)
        return self.messages["COMPLETE_ANALYSIS_NEWS_RELIABILITY_BAD"].format(news_score=text_score)

    def source_reliability(self, score):
        text_score = str(round(score * 100, 1)) + "%"
        if score < 0.7:
            return self.messages["COMPLETE_ANALYSIS_SOURCE_RELIABILITY_BAD"].format(source_score=text_score)
        if score < 0.95:
            return self.messages["COMPLETE_ANALYSIS_SOURCE_RELIABILITY_MODERATE"].format(source_score=text_score)
        return self.messages["COMPLETE_ANALYSIS_SOURCE_RELIABILITY_GOOD"].format(source_score=text_score)

    def provoking_rate(self, score):
        text_score = str(round(score * 100, 1)) + "%"
        if score < 0.2:
            return self.messages["COMPLETE_ANALYSIS_PROVOKING_GOOD"].format(provoking_score=text_score)
        if score < 0.6:
            return self.messages["COMPLETE_ANALYSIS_PROVOKING_MODERATE"].format(provoking_score=text_score)
        return self.messages["COMPLETE_ANALYSIS_PROVOKING_BAD"].format(provoking_score=text_score)

    def fake_probability_message(self, reliability_score, source_score, provoking_rate):
        if reliability_score < 0.7:
            if source_score >= 0.9:
                return self.messages["COMPLETE_ANALYSIS_FINAL_MODERATE"]
            return self.messages["COMPLETE_ANALYSIS_FINAL_BAD"]
        if provoking_rate > 0.8:
            return self.messages["COMPLETE_ANALYSIS_FINAL_HIGH_PROVOKING"]
        return self.messages["COMPLETE_ANALYSIS_FINAL_GOOD"]
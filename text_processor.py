import requests
import re
from newspaper import Article
from bs4 import BeautifulSoup
from datetime import datetime
import os
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import stanza



load_dotenv('.env')

lemmatizer = WordNetLemmatizer()

class TextProcessor:
    
    def __init__(self):
        self._stanza_models = {}
        for lang in ["en", "uk"]:
            self._stanza_models[lang] = stanza.Pipeline(lang=lang, processors='tokenize,lemma', use_gpu=True, dir="./stanza_resources")

    @staticmethod
    def format_date_for_google(date_str):
        try:
            date_obj = datetime.strptime(date_str, "%d %B %Y")
        except ValueError:
            try:
                date_obj = datetime.strptime(date_str, "%B %d, %Y")
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    return None

        if date_obj.month == 1:
            adjusted_date = date_obj.replace(year=date_obj.year - 1, month=12)
        else:
            adjusted_date = date_obj.replace(month=date_obj.month - 1)

        today = datetime.today()
        delta = today - adjusted_date

        if delta.days < 30:
            return f"d{delta.days}"
        elif delta.days < 365:
            return f"m{delta.days // 30}"
        else:
            return f"y{delta.days // 365}"
    @staticmethod
    def extract_date_from_text(text):
        date_patterns = [
            r"\b(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b",
            r"\b((January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})\b",
            r"\b(\d{4}-\d{2}-\d{2})\b"
        ]

        lines = text.split("\n")
        for line in lines[:5]:
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    return TextProcessor.format_date_for_google(match.group(1))
        return None
    @staticmethod
    def parse(url):
        try:
            article = Article(url)
            article.download()
            article.parse()

            title = article.title if article.title else "Без заголовка"
            publish_date = TextProcessor.extract_date_from_text(article.text)

            if title and article.text:
                return title, article.text, publish_date
        except Exception:
            pass

        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                return None, None, None

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find("h1")
            title = title.get_text(strip=True) if title else "Без заголовка"

            date = None
            meta_date = soup.find("meta", {"property": "article:published_time"})
            if meta_date and "content" in meta_date.attrs:
                date = meta_date["content"]

            time_tag = soup.find("time")
            if time_tag and "datetime" in time_tag.attrs:
                date = time_tag["datetime"]

            paragraphs = soup.find_all("p")
            full_text = " ".join(p.get_text() for p in paragraphs)

            if not date:
                date = TextProcessor.extract_date_from_text(full_text)

            return title, full_text, date
        except Exception:
            pass

        return None, None, None, os.getenv("ERROR_MESSAGE_PARSE")
    

    def preprocess_text(self, text, lang="en"):
        text = re.sub(r"http\\S+", "", text)
        text = re.sub(r"[^\\w\\s]", " ", text, flags=re.UNICODE)
        text = text.lower()
        try:
            stop_words = set(stopwords.words(lang))
        except OSError:
            stop_words = set()
        text = " ".join([word for word in text.split() if word not in stop_words])


        nlp = self._stanza_models.get(lang)
        doc = nlp(text)
        lemmas = [
            word.lemma for sentence in doc.sentences for word in sentence.words
            if word.upos != "PUNCT" and word.lemma is not None
        ]
        return " ".join(lemmas)


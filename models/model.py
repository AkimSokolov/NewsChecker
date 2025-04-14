import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import re
import nltk
import joblib
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from text_processor import TextProcessor

df = pd.read_csv("data sets/ukrainian_provocative_dataset_v2.csv")  # Укажи корректный путь
textProcessor = TextProcessor()

# 🔹 Загружаем стоп-слова


# 🔹 Функция очистки текста


# 🔹 Очищаем текст
df["text"] = df["text"].apply(lambda t: textProcessor.preprocess_text(t, lang="uk"))

# 🔹 Разделяем на обучающую и тестовую выборку
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.2, random_state=42)

# 🔹 TF-IDF векторизация текста
vectorizer = TfidfVectorizer(max_features=5000)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 🔹 Обучаем модель (логистическая регрессия)
model = LogisticRegression()


model.fit(X_train_tfidf, y_train)

# 🔹 Делаем предсказание на тестовых данных
y_pred = model.predict(X_test_tfidf)

# 🔹 Оцениваем точность
accuracy = accuracy_score(y_test, y_pred)


# 🔹 Выводим подробный отчет
print(accuracy)

# 🔹 Сохраняем обученную модель и TF-IDF векторизатор
joblib.dump(model, "models/fake_news_model_uk.pkl")
joblib.dump(vectorizer, "models/tfidf_vectorizer_uk.pkl")


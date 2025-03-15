import pandas as pd
import numpy as np
import re
import nltk
import joblib
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


df = pd.read_csv("../data sets/full_news_dataset_final_v2.csv")  # Укажи корректный путь


# 🔹 Загружаем стоп-слова
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

# 🔹 Функция очистки текста
def clean_text(text):
    text = re.sub(r"http\S+", "", text)  # Удаляем ссылки
    text = re.sub(r"[^a-zA-Z]", " ", text)  # Убираем знаки препинания
    text = text.lower()  # Переводим в нижний регистр
    text = " ".join([word for word in text.split() if word not in stop_words])  # Убираем стоп-слова
    return text

# 🔹 Очищаем текст
df["text"] = df["text"].apply(clean_text)

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
joblib.dump(model, "fake_news_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")


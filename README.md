### 🇺🇸 **English Version**

## Bot Functionality

The bot can evaluate a news article either by providing a **URL** or by **sending the raw text** of the news.  
> ⚠️ When using raw text, **source credibility is not evaluated**.

The bot analyzes the news and determines three key indicators: **news reliability**, **source credibility**, and **provocativeness**.

- **News reliability** is evaluated using the `all-mpnet-base-v2` model, which compares the news with similar articles from trusted sources.
- **Source credibility** is determined using a database that tracks the fake/non-fake statistics for each source. Satirical sources are also taken into account.
- **Provocativeness** is assessed using a trained **Logistic Regression** model combined with **TF-IDF** text processing.

---

## Project Structure

- `analyzer.py` – core logic of the bot, performs news evaluation  
- `db.py` – handles interaction with the database  
- `main.py` – initializes the bot and manages user interaction  
- `message_processor.py` – generates final response messages for users  
- `requirements.txt` – list of all required dependencies  
- `search_engine.py` – integrates with the Google Search API to find similar news articles from trusted sources  
- `text_processor.py` – handles text processing and web page parsing  
- `schema.sql` – contains the database schema  

---

### 🇺🇦 **Українська Версія**

## Функціонал бота

Бот може оцінювати новину як за **URL-адресою**, так і за **текстом**, який надсилає користувач.  
> ⚠️ У разі надсилання лише тексту, **оцінка достовірності джерела не виконується**.

Бот аналізує новину та визначає три ключові показники: **достовірність новини**, **надійність джерела** та **провокативність**.

- **Достовірність новини** оцінюється за допомогою моделі `all-mpnet-base-v2`, яка порівнює новину зі схожими матеріалами з надійних джерел.
- **Надійність джерела** визначається на основі бази даних, що містить статистику фейкових/нефейкових новин для кожного джерела. Також враховуються сатиричні сайти.
- **Провокативність** оцінюється за допомогою натренованої моделі на основі **Logistic Regression** та обробки тексту методом **TF-IDF**.

---

## Структура проєкту

- `analyzer.py` – основна логіка бота, оцінка новин  
- `db.py` – взаємодія з базою даних  
- `main.py` – ініціалізація бота та обробка взаємодії з користувачем  
- `message_processor.py` – генерація фінальних повідомлень для користувача  
- `requirements.txt` – список необхідних залежностей  
- `search_engine.py` – взаємодія з Google Search API для пошуку схожих новин з перевірених джерел  
- `text_processor.py` – обробка тексту та парсинг веб-сторінок  
- `schema.sql` – містить структуру бази даних  

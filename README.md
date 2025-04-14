
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
- `messages\` – contains json files with all message templates  
- `models\` – contains trained provocativeness classification models for different languages  

### Installation Note:

To run the bot, you must download and prepare `stanza_resources` in your project directory.  
Use the following code in a separate file to download models:

```python
import stanza
stanza.download('uk') 
stanza.download("en")
```

After downloading, locate the created `stanza_resources` folder (usually in your user directory) and move it to the root of your project.

Create the following keys and store them in a `.env` file:
- `BOT_TOKEN` – Telegram Bot token  
- `GOOGLEAPI` – Google Search Console API key  
- `SEARCHKEY` – Custom Search Engine ID  

Also, add database credentials to the `.env`:
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`

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
- `messages\` – містить json файли з усіма шаблонами повідомлень для користувачів  
- `models\` – містить навчальні моделі для оцінки провокативності для різних мов  

### Інструкція з установки:

Для запуску необхідно завантажити `stanza_resources` у директорію проєкту.  
Скористайтесь наступним кодом у окремому файлі:

```python
import stanza
stanza.download('uk') 
stanza.download("en")
```

Після завантаження знайдіть папку `stanza_resources` у директорії користувача та перемістіть її в корінь проєкту.

Створіть `.env` файл з такими параметрами:
- `BOT_TOKEN`, `GOOGLEAPI`, `SEARCHKEY` – ключі доступу до Telegram та Google  
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` – доступ до PostgreSQL

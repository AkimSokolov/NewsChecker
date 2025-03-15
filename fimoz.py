import psycopg2
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Env:
    def __getattr__(self, name):
        return os.getenv(name)

# Создаём объект env
env = Env()

class Database:
    RELIABLE_TABLE = "reliable_sources"
    UNRELIABLE_TABLE = "unreliable_sources"
    SATIRICAL_TABLE = "satirical_sources"
    OTHER_TABLE = "other_sources"

    DB_NAME = env.DB_NAME
    DB_USER = env.DB_USER
    DB_PASSWORD = env.DB_PASSWORD
    DB_HOST = env.DB_HOST
    DB_PORT = env.DB_PORT

    def __init__(self):
        self.dbname = self.DB_NAME
        self.user = self.DB_USER
        self.password = self.DB_PASSWORD
        self.host = self.DB_HOST
        self.port = self.DB_PORT
    
    def connect_db(self):
        return psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )
    
    def recreate_other_sources_table(self):
        """Пересоздает таблицу other_sources с новыми полями и автоматическим вычислением надёжности."""
        conn = self.connect_db()
        cur = conn.cursor()
        
        cur.execute("""
            DROP TABLE IF EXISTS other_sources;
            CREATE TABLE other_sources (
                source_name VARCHAR(255) UNIQUE NOT NULL,
                true_news INT DEFAULT 0,
                fake_news INT DEFAULT 0,
                reliability_score NUMERIC(5,2) GENERATED ALWAYS AS ((true_news + fake_news) / NULLIF(true_news, 0)) STORED
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return "Таблица other_sources успешно пересоздана с новыми требованиями."
db = Database()
print(db.recreate_other_sources_table())
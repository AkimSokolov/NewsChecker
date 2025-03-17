import psycopg2
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Database:
    RELIABLE_TABLE = "reliable_sources"
    UNRELIABLE_TABLE = "unreliable_sources"
    SATIRICAL_TABLE = "satirical_sources"
    OTHER_TABLE = "other_sources"
    COMPLETED_ANALYSIS = "news_analysis"

    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

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
    
    def check_in_reliable_sources(self, source_name):
        return self.check_source_in_table(source_name, self.RELIABLE_TABLE)

    def check_in_unreliable_sources(self, source_name):
        return self.check_source_in_table(source_name, self.UNRELIABLE_TABLE)

    def check_in_satirical_sources(self, source_name):
        return self.check_source_in_table(source_name, self.SATIRICAL_TABLE)

    def check_in_other_sources(self, source_name):
        return self.check_source_in_table(source_name, self.OTHER_TABLE)
    
    def check_source_in_table(self, source_name, table_name):
        """Проверяет, находится ли ресурс в указанной таблице."""
        conn = self.connect_db()
        cur = conn.cursor()
        query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE source_name = %s)"
        cur.execute(query, (source_name,))
        exists = cur.fetchone()[0]
        cur.close()
        conn.close()
        return exists
    def get_news_analysis(self, news_url):
        """Ищет новость в таблице news_analysis и возвращает её оценки, если найдена."""
        conn = self.connect_db()
        cur = conn.cursor()
        
        query = "SELECT reliability_score, source_score,  provocation_score FROM news_analysis WHERE news_url = %s"
        cur.execute(query, (news_url,))
        result = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if result:
            return [result[0],result[1],result[2]]
        else:
            return None

    def get_reliability_score(self, source_name):
        """Получает показатель надежности ресурса из таблицы other_sources."""
        conn = self.connect_db()
        cur = conn.cursor()
        query = "SELECT reliability_score FROM other_sources WHERE source_name = %s"
        cur.execute(query, (source_name,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else None
    
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
                reliability_score NUMERIC(5,2) GENERATED ALWAYS AS ( true_news::NUMERIC / (true_news + fake_news) ) STORED

            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return "Таблица other_sources успешно пересоздана с новыми требованиями."
    def create_news_analysis_table(self):
        """Создаёт таблицу для хранения результатов анализа новостей."""
        conn = self.connect_db()
        cur = conn.cursor()
        
        cur.execute("""
            DROP TABLE IF EXISTS news_analysis;
            CREATE TABLE news_analysis (
                news_url TEXT UNIQUE NOT NULL,
                reliability_score NUMERIC(5,2) NOT NULL,
                source_score NUMERIC(5,2) NOT NULL,
                provocation_score NUMERIC(5,2) NOT NULL
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        return "Таблица news_analysis успешно создана."
    def add_to_other_sources(self, source_name, is_reliable):
        """Добавляет или обновляет запись в таблице other_sources, увеличивая счетчики true_news или fake_news."""
        conn = self.connect_db()
        cur = conn.cursor()
        
        # Проверяем, есть ли запись
        cur.execute("SELECT true_news, fake_news FROM other_sources WHERE source_name = %s", (source_name,))
        result = cur.fetchone()
        
        if result:
            true_news, fake_news = result
            if not is_reliable:
                fake_news += 1
            else:
                true_news += 1
            
            query = """
                UPDATE other_sources 
                SET true_news = %s, fake_news = %s
                WHERE source_name = %s
            """
            cur.execute(query, (true_news, fake_news, source_name))
        else:
            query = """
                INSERT INTO other_sources (source_name, true_news, fake_news) 
                VALUES (%s, %s, %s)
            """
            cur.execute(query, (source_name, 0 if not is_reliable else 1, 1 if not is_reliable else 0))
        
        conn.commit()
        cur.close()
        conn.close()
        return "Ресурс успешно добавлен или обновлён в other_sources."
    def add_news_analysis(self, news_url, reliability_score,source_score, provocation_score):
        """Добавляет новый анализ новости в таблицу news_analysis или обновляет, если уже существует."""
        conn = self.connect_db()
        cur = conn.cursor()
        reliability_score = float(reliability_score)
        source_score = float(source_score)
        provocation_score = float(provocation_score)
        query = """
            INSERT INTO news_analysis (news_url, reliability_score, source_score, provocation_score) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (news_url) 
            DO UPDATE SET reliability_score = EXCLUDED.reliability_score, source_score = EXCLUDED.source_score, provocation_score = EXCLUDED.provocation_score;
        """
        cur.execute(query, (news_url, reliability_score, source_score, provocation_score))
        
        conn.commit()
        cur.close()
        conn.close()
        return "Анализ новости успешно добавлен или обновлён в news_analysis."


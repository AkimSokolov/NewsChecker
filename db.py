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
    
    def add_to_other_sources(self, source_name, reliability_score):
        """Добавляет ресурс в таблицу other_sources, если он не найден ни в одной таблице."""
        if any([
            self.check_in_reliable_sources(source_name),
            self.check_in_unreliable_sources(source_name),
            self.check_in_satirical_sources(source_name),
            self.check_in_other_sources(source_name)
        ]):
            return "Ресурс уже находится в одной из таблиц."
        
        conn = self.connect_db()
        cur = conn.cursor()
        query = "INSERT INTO other_sources (source_name, reliability_score) VALUES (%s, %s)"
        cur.execute(query, (source_name, reliability_score))
        conn.commit()
        cur.close()
        conn.close()
        return "Ресурс успешно добавлен в other_sources."
    
    def increase_source_score(self, source_name)

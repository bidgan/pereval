import psycopg2
from psycopg2 import sql
import sys
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

host = os.getenv('FSTR_DB_HOST')
port = os.getenv('FSTR_DB_PORT')
user = os.getenv('FSTR_DB_LOGIN')
password = os.getenv('FSTR_DB_PASS')
dbname = os.getenv('FSTR_DB_NAME')


class DatabaseHandler:
    def __init__(self, host, port, user, password, dbname):
        self.conn = None
        self.cur = None
        try:
            self.conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            self.cur = self.conn.cursor()
            print("Connected to PostgreSQL.")
        except Exception as e:
            print("Error connecting to PostgreSQL:", e)
            sys.exit(1)

    def add_pereval_data(self, beautyTitle, title, other_titles, connect, date_added, user_id, coord_id, level_id):
        status = 'new'
        try:
            self.cur.execute("""
                INSERT INTO pereval_added (beautytitle, title, other_titles, connect, date_added, user_id, coord_id, level_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (beautyTitle, title, other_titles, connect, date_added, user_id, coord_id, level_id, status))
            self.conn.commit()
            print("Data added successfully.")
        except psycopg2.IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e):
                print("Error: Duplicate key value.")
            else:
                print("Error executing SQL query:", e)
            sys.exit(1)

    def close_connection(self):
        self.cur.close()
        self.conn.close()

try:
    # Пример использования
    db_handler = DatabaseHandler('localhost', port, user, password, dbname)
    db_handler.add_pereval_data("Beautiful Title", "Main Title", "Other Titles", "Connection Info", "2022-01-01 12:00:00", 3,3 ,3 )
    db_handler.close_connection()
except Exception as e:
    print("An error occurred:", e)

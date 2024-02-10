# Module db.py
import psycopg2
import os


class Database:
    def __init__(self):
        db_user = os.getenv('DATABASE_USER')
        db_pass = os.getenv('DATABASE_PASS')
        db_name = os.getenv('DATABASE_NAME')
        db_host = os.getenv('DATABASE_HOST')
        db_port = os.getenv('DATABASE_PORT', '5432')

        self.db = db_name
        self.username = db_user
        self.password = db_pass
        self.port = int(db_port)
        self.host = db_host
        self.cur = None
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            database=self.db, user=self.username, password=self.password, host=self.host, port=self.port)
        self.cur = self.conn.cursor()

    def execute_query(self, query, values=()):
        if self.conn is not None and self.cur is not None:
            self.cur.execute(query, values)
            self.conn.commit()

    def fetch_one(self):
        if self.cur is not None:
            return self.cur.fetchone()

    def fetch_all(self):
        if self.cur is not None:
            return self.cur.fetchall()

    def close(self):
        if self.conn is not None and self.cur is not None:
            self.cur.close()
            self.conn.close()

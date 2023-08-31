# Module db.py
import psycopg2
import os


class Database:
    def __init__(self):
        # db_user = os.getenv('DATABASE_USER')
        # db_pass = os.getenv('DATABASE_PASS')
        # db_name = os.getenv('DATABASE_NAME')
        # db_host = os.getenv('DATABASE_HOST')
        # db_port = os.getenv('DATABASE_PORT', '5433')
        db_user = 'teslamate'
        db_pass = 'Passw0rd115'
        db_name = 'teslamate'
        db_host = '192.168.1.10'
        db_port = '5432'

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
        self.cur.execute(query, values)
        self.conn.commit()

    def fetch_one(self):
        return self.cur.fetchone()

    def fetch_all(self):
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()


# db = Database(db=db_name, username=db_user, password=db_pass,
#               host=db_host, port=int(db_port))

# db.connect()

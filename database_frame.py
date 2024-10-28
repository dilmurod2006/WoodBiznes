import sqlite3
from datetime import datetime

from database_crud import get_connection

def setup_database():
    conn = sqlite3.connect('DATABASE.db')
    cur = conn.cursor()
    
    # Admin table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS Admin (
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        tg_id TEXT,
        created TEXT
    )
''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Workers (
            id INTEGER PRIMARY KEY,
            full_name TEXT,
            is_deleted BOOLEAN,
            created TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Daily_Work_Data (
            worker_id INTEGER,
            thickness REAL,
            width REAL,
            length REAL,
            quantity INTEGER,
            volume_wood REAL,
            description TEXT,
            date TEXT,
            FOREIGN KEY(worker_id) REFERENCES Workers(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS WoodsData (
            id INTEGER PRIMARY KEY,
            token TEXT,
            author INTEGER,
            name_wood TEXT,
            truck_number TEXT,
            description TEXT,
            volume_wood REAL,
            created TEXT,
            FOREIGN KEY(author) REFERENCES Admin(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Woodsresize (
            token_id INTEGER,
            thickness REAL,
            width REAL,
            length REAL,
            quantity INTEGER,
            volume REAL,
            FOREIGN KEY(token_id) REFERENCES WoodsData(id)
        )
    ''')

    conn.commit()
    conn.close()

setup_database()
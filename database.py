import sqlite3

DB_NAME = "can_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS can_signals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp REAL,
                  message_id INTEGER,
                  signal_name TEXT,
                  value REAL)''')
    conn.commit()
    conn.close()

def insert_signal(timestamp, msg_id, name, value):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO can_signals (timestamp, message_id, signal_name, value) VALUES (?,?,?,?)",
              (timestamp, msg_id, name, value))
    conn.commit()
    conn.close()
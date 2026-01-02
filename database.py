import sqlite3
from datetime import date

DB_NAME = "goals.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                target_date TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        """)
        conn.commit()

def add_goal(title: str, target_date: str = None):
    if target_date is None:
        target_date = date.today().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO goals (title, target_date, completed) VALUES (?, ?, 0)", (title, target_date))
        conn.commit()

def get_goals_by_date(target_date: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals WHERE target_date = ?", (target_date,))
        return cursor.fetchall()

def toggle_goal_status(goal_id: int, current_status: int):
    new_status = 0 if current_status else 1
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE goals SET completed = ? WHERE id = ?", (new_status, goal_id))
        conn.commit()

def delete_goal(goal_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()

def get_all_goals():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals ORDER BY target_date ASC")
        return cursor.fetchall()

def clear_all_data():
    """Wipes all data from the database."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals")
        # Reset the ID counter (optional, but cleaner)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='goals'")
        conn.commit()
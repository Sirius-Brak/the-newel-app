# database/init_db.py
import sqlite3
import os

# Calculate the path to the database file directly
basedir = os.path.abspath(os.path.dirname(__file__))  # This gets the /database folder path
DATABASE_PATH = os.path.join(basedir, '..', 'instance', 'the_newel.db')  # Go up one level, then into instance

def init_database():
    # Create the instance directory if it doesn't exist
    instance_dir = os.path.dirname(DATABASE_PATH)
    os.makedirs(instance_dir, exist_ok=True)
    
    print(f"Creating database at: {DATABASE_PATH}")
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Drop tables if they exist (useful for testing)
    c.executescript('''
        DROP TABLE IF EXISTS submissions;
        DROP TABLE IF EXISTS prompts;
        DROP TABLE IF EXISTS users;
    ''')

    # Create the users table
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'teacher')),
            class TEXT
        )
    ''')

    # Create the prompts table
    c.execute('''
        CREATE TABLE prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            subject TEXT NOT NULL CHECK(subject IN ('physics', 'biology', 'general')),
            class_year TEXT NOT NULL,
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')

    # Create the submissions table
    c.execute('''
        CREATE TABLE submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            response_text TEXT,
            grade INTEGER,
            feedback TEXT,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            graded_at DATETIME,
            FOREIGN KEY (prompt_id) REFERENCES prompts (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("[SUCCESS] Database tables created successfully!")

if __name__ == '__main__':
    init_database()
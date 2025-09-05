# init_db.py
import sqlite3
import os

# Get the absolute path to the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Create the instance folder if it doesn't exist
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)

# Define the database path
DATABASE_PATH = os.path.join(instance_path, 'the_newel.db')

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# SQL to create the users table
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
    class TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

# SQL to create the prompts table
create_prompts_table = """
CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    subject TEXT DEFAULT 'physics',
    class_year TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (id)
);
"""

# SQL to create the submissions table
create_submissions_table = """
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    score INTEGER,
    submitted_at DATETIME,
    FOREIGN KEY (prompt_id) REFERENCES prompts (id),
    FOREIGN KEY (student_id) REFERENCES users (id)
);
"""

# Execute the SQL commands
try:
    cursor.execute(create_users_table)
    cursor.execute(create_prompts_table)
    cursor.execute(create_submissions_table)
    conn.commit()
    print("✅ SUCCESS: Database 'the_newel.db' created successfully in the 'instance' folder.")
    print(f"✅ Database location: {DATABASE_PATH}")
except sqlite3.Error as e:
    print(f"❌ ERROR: {e}")
finally:
    conn.close()
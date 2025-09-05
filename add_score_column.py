# add_score_column.py
# RUN THIS SCRIPT ONE TIME ONLY TO UPDATE YOUR DATABASE

import sqlite3
import os

basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(basedir, 'instance', 'the_newel.db')

# Connect to the database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # Execute the ALTER TABLE command
    cursor.execute("ALTER TABLE submissions ADD COLUMN score INTEGER;")
    conn.commit()
    print("✅ SUCCESS: Added 'score' column to 'submissions' table.")
except sqlite3.Error as e:
    print(f"❌ ERROR: {e}")
finally:
    conn.close()
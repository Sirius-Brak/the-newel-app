from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from dotenv import load_dotenv
import random
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

# Science facts list (22 non-trivial facts)
SCIENCE_FACTS = [
    "Quantum particles can be in multiple states simultaneously until observed (superposition).",
    "The human brain contains approximately 86 billion neurons connected by trillions of synapses.",
    "DNA from a single human cell would be about 2 meters long if stretched end-to-end.",
    "The Earth's inner core is as hot as the surface of the sun (about 5700 K).", 
    "There are more trees on Earth than stars in the Milky Way galaxy (3 trillion vs 100-400 billion).",
    "The Great Red Spot on Jupiter has been raging for at least 400 years.",
    "A teaspoon of neutron star material would weigh about 6 billion tons.",
    "Plants can communicate with each other through underground fungal networks.",
    "The human body contains about 0.2 milligrams of gold, mostly in the blood.",
    "Light takes approximately 8 minutes and 20 seconds to travel from the Sun to Earth.",
    "There are more possible iterations of a game of chess than atoms in the observable universe.",
    "The smell of fresh rain (petrichor) comes from bacteria in the soil.",
    "A single lightning bolt contains enough energy to toast 100,000 slices of bread.",
    "The Moon is slowly moving away from Earth at about 3.8 cm per year.",
    "Water can exist in at least 18 different solid phases (types of ice).",
    "The average cloud weighs about 1.1 million pounds (500,000 kg).",
    "Your stomach produces a new lining every 3-4 days to prevent digesting itself.",
    "A day on Venus is longer than a year on Venus (243 vs 225 Earth days).",
    "The deepest part of the ocean (Mariana Trench) is deeper than Mount Everest is tall.",
    "The placebo effect can trigger real physiological healing responses in the body.",
    "A single human chromosome may contain over 500 million base pairs of DNA.",
    "The universe has no center - every point is expanding away from every other point."
]

# Get the absolute path to the current directory
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(basedir, 'instance', 'the_newel.db')
TEMPLATES_PATH = os.path.join(basedir, 'templates')

app = Flask(__name__, template_folder=TEMPLATES_PATH)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Database initialization
if not os.path.exists(DATABASE_PATH):
    print("Initializing database...")
    instance_path = os.path.join(basedir, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    schema_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
        class_name TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

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

    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        response_text TEXT NOT NULL,
        score INTEGER,
        submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (prompt_id) REFERENCES prompts (id),
        FOREIGN KEY (student_id) REFERENCES users (id)
    );
    """
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

@app.route('/')
def index():
    random_fact = random.choice(SCIENCE_FACTS)
    return render_template('index.html', random_fact=random_fact)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'teacher')
        student_class = request.form.get('class_name')

        if not all([full_name, username, password, confirm_password]):
            flash('All fields are required.', 'error')
            return render_template('auth/register.html', role=role)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html', role=role)

        hashed_password = generate_password_hash(password)

        conn = None
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                flash('Username already exists.', 'error')
                return render_template('auth/register.html', role=role)
            
            cursor.execute(
                "INSERT INTO users (full_name, username, password_hash, role, class_name) VALUES (?, ?, ?, ?, ?)",
                (full_name, username, hashed_password, role, student_class if role == 'student' else None)
            )
            
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
            
        except sqlite3.Error as e:
            flash('An error occurred during registration.', 'error')
            return render_template('auth/register.html', role=role)
        finally:
            if conn:
                conn.close()

    role = request.args.get('role', 'teacher')
    return render_template('auth/register.html', role=role)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([username, password]):
            flash('Please enter both username and password.', 'error')
            return render_template('auth/login.html')

        conn = None
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = user['role']
                session['class_name'] = user['class_name']
                
                flash('Login successful!', 'success')
                if user['role'] == 'teacher':
                    return redirect(url_for('teacher_dashboard'))
                else:
                    return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid username or password.', 'error')
                return render_template('auth/login.html')
            
        except sqlite3.Error:
            flash('An error occurred during login.', 'error')
            return render_template('auth/login.html')
        finally:
            if conn:
                conn.close()

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/teacher-dashboard')
@login_required
def teacher_dashboard():
    if session.get('role') != 'teacher':
        flash('Access denied. Teacher authorization required.', 'error')
        return redirect(url_for('index'))
    return render_template('teacher/dashboard.html')

@app.route('/student-dashboard')
@login_required
def student_dashboard():
    if session.get('role') != 'student':
        flash('Access denied. Student authorization required.', 'error')
        return redirect(url_for('index'))
    return render_template('student/dashboard.html')

# Add your other routes here (physics, biology, general prompts, etc.)
# Ensure they use session['class_name'] instead of session['class']

if __name__ == '__main__':
    print("Starting The Newel app server...")
    print(f"Database path: {DATABASE_PATH}")
    print(f"Templates path: {TEMPLATES_PATH}")
    app.run(debug=True)
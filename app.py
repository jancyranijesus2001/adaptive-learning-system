from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database initialization
def init_db():
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        level TEXT DEFAULT 'beginner',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Pre-test results
    c.execute('''CREATE TABLE IF NOT EXISTS pre_test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        total_questions INTEGER,
        level_assigned TEXT,
        test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Learning progress
    c.execute('''CREATE TABLE IF NOT EXISTS learning_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        topic TEXT,
        difficulty TEXT,
        correct_answers INTEGER DEFAULT 0,
        total_attempts INTEGER DEFAULT 0,
        last_practiced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Vocabulary learned
    c.execute('''CREATE TABLE IF NOT EXISTS vocabulary_learned (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        word TEXT,
        definition TEXT,
        difficulty TEXT,
        mastery_level INTEGER DEFAULT 0,
        learned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Gamification points
    c.execute('''CREATE TABLE IF NOT EXISTS user_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total_points INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        badges TEXT,
        streak_days INTEGER DEFAULT 0,
        last_activity_date DATE,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Chat history
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        response TEXT,
        is_correct BOOLEAN,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Post-test results
    c.execute('''CREATE TABLE IF NOT EXISTS post_test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        total_questions INTEGER,
        improvement_percentage REAL,
        test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Admin table
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insert default admin
    c.execute("INSERT OR IGNORE INTO admins (username, password) VALUES ('admin', 'admin123')")
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')
        age = data.get('age')
        
        conn = sqlite3.connect('database/learning_system.db')
        c = conn.cursor()
        
        try:
            c.execute("INSERT INTO users (username, password, full_name, age) VALUES (?, ?, ?, ?)",
                     (username, password, full_name, age))
            user_id = c.lastrowid
            
            # Initialize gamification points
            c.execute("INSERT INTO user_points (user_id) VALUES (?)", (user_id,))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Registration successful!'})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Username already exists!'})
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect('database/learning_system.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['full_name'] = user[3]
            session.permanent = True
            
            return jsonify({'success': True, 'redirect': '/dashboard'})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials!'})
    
    return render_template('login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect('database/learning_system.db')
        c = conn.cursor()
        
        c.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
        admin = c.fetchone()
        conn.close()
        
        if admin:
            session['admin_id'] = admin[0]
            session['admin_username'] = admin[1]
            session.permanent = True
            
            return jsonify({'success': True, 'redirect': '/admin-dashboard'})
        else:
            return jsonify({'success': False, 'message': 'Invalid admin credentials!'})
    
    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    # Get user info
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    
    # Get points and badges
    c.execute("SELECT * FROM user_points WHERE user_id=?", (user_id,))
    points_data = c.fetchone()
    
    # Check if pre-test is completed
    c.execute("SELECT * FROM pre_test_results WHERE user_id=?", (user_id,))
    pre_test = c.fetchone()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         user=user, 
                         points=points_data,
                         pre_test_completed=pre_test is not None)

@app.route('/pre-test')
def pre_test():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('pre_test.html')

@app.route('/submit-pre-test', methods=['POST'])
def submit_pre_test():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.json
    user_id = session['user_id']
    score = data.get('score')
    total = data.get('total')
    
    # Determine level based on score
    percentage = (score / total) * 100
    if percentage >= 80:
        level = 'advanced'
    elif percentage >= 50:
        level = 'intermediate'
    else:
        level = 'beginner'
    
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    c.execute("INSERT INTO pre_test_results (user_id, score, total_questions, level_assigned) VALUES (?, ?, ?, ?)",
             (user_id, score, total, level))
    
    c.execute("UPDATE users SET level=? WHERE id=?", (level, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'level': level, 'score': score, 'total': total})

@app.route('/learning')
def learning():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    c.execute("SELECT level FROM users WHERE id=?", (user_id,))
    user_level = c.fetchone()[0]
    
    conn.close()
    
    return render_template('learning.html', level=user_level)

@app.route('/get-learning-content', methods=['POST'])
def get_learning_content():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    data = request.json
    topic = data.get('topic')
    difficulty = data.get('difficulty', 'beginner')
    
    # Get adaptive content based on user's performance
    content = get_adaptive_content(session['user_id'], topic, difficulty)
    
    return jsonify({'success': True, 'content': content})

@app.route('/practice')
def practice():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('practice.html')

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('chat.html')

@app.route('/chat-message', methods=['POST'])
def chat_message():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    data = request.json
    user_message = data.get('message')
    user_id = session['user_id']
    
    # Simple AI response logic
    response, is_correct = process_chat_message(user_message, user_id)
    
    # Save to database
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id, message, response, is_correct) VALUES (?, ?, ?, ?)",
             (user_id, user_message, response, is_correct))
    conn.commit()
    conn.close()
    
    # Award points if correct
    if is_correct:
        update_points(user_id, 10)
    
    return jsonify({'success': True, 'response': response, 'is_correct': is_correct})

@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    # Get all progress data
    c.execute("SELECT * FROM learning_progress WHERE user_id=?", (user_id,))
    progress_data = c.fetchall()
    
    c.execute("SELECT * FROM vocabulary_learned WHERE user_id=?", (user_id,))
    vocab_data = c.fetchall()
    
    c.execute("SELECT * FROM user_points WHERE user_id=?", (user_id,))
    points_data = c.fetchone()
    
    conn.close()
    
    return render_template('progress.html', 
                         progress=progress_data,
                         vocabulary=vocab_data,
                         points=points_data)

@app.route('/post-test')
def post_test():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('post_test.html')

@app.route('/submit-post-test', methods=['POST'])
def submit_post_test():
    if 'user_id' not in session:
        return jsonify({'success': False})
    
    data = request.json
    user_id = session['user_id']
    score = data.get('score')
    total = data.get('total')
    
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    # Get pre-test score
    c.execute("SELECT score, total_questions FROM pre_test_results WHERE user_id=? ORDER BY test_date DESC LIMIT 1", 
             (user_id,))
    pre_test_data = c.fetchone()
    
    if pre_test_data:
        pre_score = pre_test_data[0]
        pre_total = pre_test_data[1]
        pre_percentage = (pre_score / pre_total) * 100
        post_percentage = (score / total) * 100
        improvement = post_percentage - pre_percentage
    else:
        improvement = 0
    
    c.execute("INSERT INTO post_test_results (user_id, score, total_questions, improvement_percentage) VALUES (?, ?, ?, ?)",
             (user_id, score, total, improvement))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'improvement': improvement, 'score': score, 'total': total})

@app.route('/feedback')
def feedback():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    feedback_data = generate_feedback(user_id)
    
    return render_template('feedback.html', feedback=feedback_data)

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    # Get all users
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    
    # Get statistics
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    c.execute("SELECT AVG(score) FROM pre_test_results")
    avg_pre_score = c.fetchone()[0] or 0
    
    c.execute("SELECT AVG(score) FROM post_test_results")
    avg_post_score = c.fetchone()[0] or 0
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         users=users,
                         total_users=total_users,
                         avg_pre_score=avg_pre_score,
                         avg_post_score=avg_post_score)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Helper functions
def get_adaptive_content(user_id, topic, difficulty):
    """Generate adaptive learning content based on user performance"""
    
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    # Check user's performance on this topic
    c.execute("SELECT correct_answers, total_attempts FROM learning_progress WHERE user_id=? AND topic=?",
             (user_id, topic))
    progress = c.fetchone()
    conn.close()
    
    # Vocabulary content by difficulty
    vocabulary_content = {
        'beginner': {
            'vocabulary': [
                {'word': 'cat', 'definition': 'A small furry animal that says meow', 'example': 'The cat is sleeping.'},
                {'word': 'dog', 'definition': 'A friendly animal that barks', 'example': 'I have a dog.'},
                {'word': 'house', 'definition': 'A building where people live', 'example': 'This is my house.'},
                {'word': 'book', 'definition': 'Something you read', 'example': 'I read a book.'},
                {'word': 'happy', 'definition': 'Feeling good and smiling', 'example': 'I am happy today.'}
            ],
            'grammar': [
                {'rule': 'Simple Present Tense', 'explanation': 'Use for habits and facts', 'example': 'I eat breakfast every day.'},
                {'rule': 'Articles (a, an, the)', 'explanation': 'Use "a" before consonants, "an" before vowels', 'example': 'I have a cat. I saw an elephant.'}
            ]
        },
        'intermediate': {
            'vocabulary': [
                {'word': 'achieve', 'definition': 'To successfully complete something', 'example': 'I will achieve my goals.'},
                {'word': 'beautiful', 'definition': 'Very pretty or attractive', 'example': 'The sunset is beautiful.'},
                {'word': 'continue', 'definition': 'To keep doing something', 'example': 'Please continue reading.'},
                {'word': 'important', 'definition': 'Something that matters a lot', 'example': 'Education is important.'},
                {'word': 'necessary', 'definition': 'Something you need', 'example': 'Water is necessary for life.'}
            ],
            'grammar': [
                {'rule': 'Past Tense', 'explanation': 'Use -ed for regular verbs', 'example': 'I walked to school yesterday.'},
                {'rule': 'Comparative Adjectives', 'explanation': 'Use -er or more to compare', 'example': 'This book is bigger than that one.'}
            ]
        },
        'advanced': {
            'vocabulary': [
                {'word': 'accommodate', 'definition': 'To provide space or make adjustments', 'example': 'The hotel can accommodate 200 guests.'},
                {'word': 'comprehensive', 'definition': 'Complete and including everything', 'example': 'She wrote a comprehensive report.'},
                {'word': 'enthusiastic', 'definition': 'Very interested and excited', 'example': 'He is enthusiastic about learning.'},
                {'word': 'magnificent', 'definition': 'Extremely beautiful or impressive', 'example': 'The palace is magnificent.'},
                {'word': 'persuade', 'definition': 'To convince someone', 'example': 'I will persuade him to join us.'}
            ],
            'grammar': [
                {'rule': 'Present Perfect Tense', 'explanation': 'Use have/has + past participle', 'example': 'I have finished my homework.'},
                {'rule': 'Conditional Sentences', 'explanation': 'If + present, will + verb', 'example': 'If it rains, I will stay home.'}
            ]
        }
    }
    
    # Adjust difficulty based on performance
    if progress:
        correct = progress[0]
        total = progress[1]
        if total > 0:
            accuracy = correct / total
            if accuracy >= 0.8 and difficulty != 'advanced':
                # Upgrade difficulty
                if difficulty == 'beginner':
                    difficulty = 'intermediate'
                elif difficulty == 'intermediate':
                    difficulty = 'advanced'
            elif accuracy < 0.5 and difficulty != 'beginner':
                # Downgrade difficulty
                if difficulty == 'advanced':
                    difficulty = 'intermediate'
                elif difficulty == 'intermediate':
                    difficulty = 'beginner'
    
    return vocabulary_content.get(difficulty, vocabulary_content['beginner'])

def process_chat_message(message, user_id):
    """Process chat message and provide intelligent response"""
    
    message = message.lower().strip()
    
    # Simple grammar checking patterns
    grammar_patterns = {
        'i am': ['i am happy', 'i am learning', 'i am student'],
        'i have': ['i have a book', 'i have friends'],
        'subject-verb agreement': True
    }
    
    # Check for common errors
    is_correct = True
    response = ""
    
    # Check if it's a simple sentence
    if len(message.split()) < 3:
        is_correct = False
        response = "Try to make a complete sentence with at least 3 words! For example: 'I like cats.'"
    
    # Check for capital letter at start
    elif not message[0].isupper():
        is_correct = False
        response = "Remember to start your sentence with a capital letter! Try again: " + message.capitalize()
    
    # Check for ending punctuation
    elif not message.endswith('.') and not message.endswith('!') and not message.endswith('?'):
        is_correct = False
        response = "Don't forget to end your sentence with a period (.), question mark (?), or exclamation mark (!)"
    
    # Common grammar checks
    elif ' i ' in message and message != message.capitalize():
        is_correct = False
        response = "The word 'I' should always be capital! Example: 'I am happy.'"
    
    else:
        # Sentence looks good
        is_correct = True
        responses = [
            f"Great sentence! You wrote: '{message}' - Keep practicing!",
            f"Excellent! That's a proper sentence. Well done!",
            f"Perfect! You're learning well. Try another sentence!",
            f"Very good! Your English is improving!"
        ]
        response = random.choice(responses)
    
    return response, is_correct

def update_points(user_id, points_to_add):
    """Update user points and check for level up"""
    
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    c.execute("SELECT total_points, level FROM user_points WHERE user_id=?", (user_id,))
    current = c.fetchone()
    
    if current:
        new_points = current[0] + points_to_add
        current_level = current[1]
        
        # Level up every 100 points
        new_level = (new_points // 100) + 1
        
        c.execute("UPDATE user_points SET total_points=?, level=? WHERE user_id=?",
                 (new_points, new_level, user_id))
    
    conn.commit()
    conn.close()

def generate_feedback(user_id):
    """Generate personalized feedback for user"""
    
    conn = sqlite3.connect('database/learning_system.db')
    c = conn.cursor()
    
    # Get user progress
    c.execute("SELECT * FROM learning_progress WHERE user_id=?", (user_id,))
    progress = c.fetchall()
    
    # Get vocabulary
    c.execute("SELECT COUNT(*) FROM vocabulary_learned WHERE user_id=?", (user_id,))
    vocab_count = c.fetchone()[0]
    
    # Get chat accuracy
    c.execute("SELECT COUNT(*) FROM chat_history WHERE user_id=? AND is_correct=1", (user_id,))
    correct_chats = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM chat_history WHERE user_id=?", (user_id,))
    total_chats = c.fetchone()[0]
    
    conn.close()
    
    feedback = {
        'vocabulary_learned': vocab_count,
        'chat_accuracy': (correct_chats / total_chats * 100) if total_chats > 0 else 0,
        'strengths': [],
        'weaknesses': [],
        'recommendations': []
    }
    
    # Determine strengths and weaknesses
    if feedback['chat_accuracy'] >= 80:
        feedback['strengths'].append('Excellent grammar and sentence formation')
    elif feedback['chat_accuracy'] >= 60:
        feedback['strengths'].append('Good progress in grammar')
    else:
        feedback['weaknesses'].append('Grammar needs more practice')
        feedback['recommendations'].append('Practice more in the chat module')
    
    if vocab_count >= 50:
        feedback['strengths'].append('Great vocabulary knowledge')
    elif vocab_count >= 20:
        feedback['strengths'].append('Building good vocabulary')
    else:
        feedback['weaknesses'].append('Need to learn more words')
        feedback['recommendations'].append('Spend more time in vocabulary learning')
    
    # General recommendations
    if not feedback['recommendations']:
        feedback['recommendations'].append('Keep up the great work!')
        feedback['recommendations'].append('Try advanced topics for challenge')
    
    return feedback

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
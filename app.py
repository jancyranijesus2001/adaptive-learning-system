from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import certifi

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# ---------------------------------------------------------------------------
# MongoDB Atlas connection
# ---------------------------------------------------------------------------
# tlsCAFile=certifi.where() fixes the common
# "[SSL: TLSV1_ALERT_INTERNAL_ERROR]" handshake failure seen on some
# Python/OpenSSL builds (and in many serverless environments) when the
# system's default CA bundle doesn't satisfy Atlas's TLS handshake.
client = MongoClient(os.getenv("MONGODB_URI"), tlsCAFile=certifi.where())
db = client["learning_system"]

# Collections (replacing the old SQLite tables)
users_col = db["users"]
admins_col = db["admins"]
pre_test_results_col = db["pre_test_results"]
learning_progress_col = db["learning_progress"]
vocabulary_learned_col = db["vocabulary_learned"]
user_points_col = db["user_points"]
chat_history_col = db["chat_history"]
post_test_results_col = db["post_test_results"]


def ensure_default_admin():
    """Create the default admin account once, if it doesn't already exist.

    This replaces the old SQLite `INSERT OR IGNORE INTO admins ...` seed.
    Safe to call on every cold start: it's a no-op if the admin already exists.
    """
    try:
        existing = admins_col.find_one({"username": "admin"})
        if not existing:
            admins_col.insert_one({
                "username": "admin",
                "password": generate_password_hash("admin123"),
                "created_at": datetime.utcnow()
            })
    except PyMongoError as e:
        # Don't crash app startup/import if Mongo is briefly unreachable;
        # log it so it's visible in Vercel function logs.
        print(f"[startup] Could not ensure default admin: {e}")


# NOTE: This runs at import time, but it performs a MongoDB read/insert,
# not a local filesystem write or SQL DDL statement, so it is safe under
# Vercel's read-only filesystem and serverless cold-start model.
ensure_default_admin()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
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

        try:
            hashed_password = generate_password_hash(password)
            user_doc = {
                "username": username,
                "password": hashed_password,
                "full_name": full_name,
                "age": age,
                "level": "beginner",
                "created_at": datetime.utcnow()
            }
            result = users_col.insert_one(user_doc)
            user_id = result.inserted_id

            # Initialize gamification points
            user_points_col.insert_one({
                "user_id": user_id,
                "total_points": 0,
                "level": 1,
                "badges": "",
                "streak_days": 0,
                "last_activity_date": None
            })

            return jsonify({'success': True, 'message': 'Registration successful!'})

        except DuplicateKeyError:
            return jsonify({'success': False, 'message': 'Username already exists!'})
        except PyMongoError as e:
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'})

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        try:
            user = users_col.find_one({"username": username})

            if user and check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session.permanent = True

                return jsonify({'success': True, 'redirect': '/dashboard'})
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials!'})
        except PyMongoError as e:
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'})

    return render_template('login.html')


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')

        try:
            admin = admins_col.find_one({"username": username})

            if admin and check_password_hash(admin['password'], password):
                session['admin_id'] = str(admin['_id'])
                session['admin_username'] = admin['username']
                session.permanent = True

                return jsonify({'success': True, 'redirect': '/admin-dashboard'})
            else:
                return jsonify({'success': False, 'message': 'Invalid admin credentials!'})
        except PyMongoError as e:
            return jsonify({'success': False, 'message': f'Database error: {str(e)}'})

    return render_template('admin_login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        user = users_col.find_one({"_id": ObjectId(user_id)})
        points_data = user_points_col.find_one({"user_id": ObjectId(user_id)})
        pre_test = pre_test_results_col.find_one({"user_id": ObjectId(user_id)})
    except PyMongoError as e:
        return f"Database error: {str(e)}", 500

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

    try:
        pre_test_results_col.insert_one({
            "user_id": ObjectId(user_id),
            "score": score,
            "total_questions": total,
            "level_assigned": level,
            "test_date": datetime.utcnow()
        })

        users_col.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"level": level}}
        )
    except PyMongoError as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})

    return jsonify({'success': True, 'level': level, 'score': score, 'total': total})


@app.route('/learning')
def learning():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        user = users_col.find_one({"_id": ObjectId(user_id)})
        user_level = user['level'] if user else 'beginner'
    except PyMongoError as e:
        return f"Database error: {str(e)}", 500

    return render_template('learning.html', level=user_level)


@app.route('/get-learning-content', methods=['POST'])
def get_learning_content():
    if 'user_id' not in session:
        return jsonify({'success': False})

    data = request.json
    topic = data.get('topic')
    difficulty = data.get('difficulty', 'beginner')

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

    try:
        chat_history_col.insert_one({
            "user_id": ObjectId(user_id),
            "message": user_message,
            "response": response,
            "is_correct": is_correct,
            "timestamp": datetime.utcnow()
        })
    except PyMongoError as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})

    # Award points if correct
    if is_correct:
        update_points(user_id, 10)

    return jsonify({'success': True, 'response': response, 'is_correct': is_correct})


@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        progress_data = list(learning_progress_col.find({"user_id": ObjectId(user_id)}))
        vocab_data = list(vocabulary_learned_col.find({"user_id": ObjectId(user_id)}))
        points_data = user_points_col.find_one({"user_id": ObjectId(user_id)})
    except PyMongoError as e:
        return f"Database error: {str(e)}", 500

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

    try:
        # Get most recent pre-test score
        pre_test_data = pre_test_results_col.find_one(
            {"user_id": ObjectId(user_id)},
            sort=[("test_date", -1)]
        )

        if pre_test_data:
            pre_score = pre_test_data['score']
            pre_total = pre_test_data['total_questions']
            pre_percentage = (pre_score / pre_total) * 100
            post_percentage = (score / total) * 100
            improvement = post_percentage - pre_percentage
        else:
            improvement = 0

        post_test_results_col.insert_one({
            "user_id": ObjectId(user_id),
            "score": score,
            "total_questions": total,
            "improvement_percentage": improvement,
            "test_date": datetime.utcnow()
        })
    except PyMongoError as e:
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'})

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

    try:
        users = list(users_col.find({}))

        total_users = users_col.count_documents({})

        pre_scores = [doc['score'] for doc in pre_test_results_col.find({}, {"score": 1})]
        avg_pre_score = sum(pre_scores) / len(pre_scores) if pre_scores else 0

        post_scores = [doc['score'] for doc in post_test_results_col.find({}, {"score": 1})]
        avg_post_score = sum(post_scores) / len(post_scores) if post_scores else 0
    except PyMongoError as e:
        return f"Database error: {str(e)}", 500

    return render_template('admin_dashboard.html',
                            users=users,
                            total_users=total_users,
                            avg_pre_score=avg_pre_score,
                            avg_post_score=avg_post_score)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def get_adaptive_content(user_id, topic, difficulty):
    """Generate adaptive learning content based on user performance"""

    try:
        progress = learning_progress_col.find_one(
            {"user_id": ObjectId(user_id), "topic": topic}
        )
    except PyMongoError:
        progress = None

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
        correct = progress.get('correct_answers', 0)
        total = progress.get('total_attempts', 0)
        if total > 0:
            accuracy = correct / total
            if accuracy >= 0.8 and difficulty != 'advanced':
                if difficulty == 'beginner':
                    difficulty = 'intermediate'
                elif difficulty == 'intermediate':
                    difficulty = 'advanced'
            elif accuracy < 0.5 and difficulty != 'beginner':
                if difficulty == 'advanced':
                    difficulty = 'intermediate'
                elif difficulty == 'intermediate':
                    difficulty = 'beginner'

    return vocabulary_content.get(difficulty, vocabulary_content['beginner'])


def process_chat_message(message, user_id):
    """Process chat message and provide intelligent response"""

    message = message.lower().strip()

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

    try:
        current = user_points_col.find_one({"user_id": ObjectId(user_id)})

        if current:
            new_points = current.get('total_points', 0) + points_to_add
            new_level = (new_points // 100) + 1

            user_points_col.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": {"total_points": new_points, "level": new_level}}
            )
    except PyMongoError as e:
        print(f"[update_points] Database error: {e}")


def generate_feedback(user_id):
    """Generate personalized feedback for user"""

    try:
        vocab_count = vocabulary_learned_col.count_documents({"user_id": ObjectId(user_id)})
        correct_chats = chat_history_col.count_documents({"user_id": ObjectId(user_id), "is_correct": True})
        total_chats = chat_history_col.count_documents({"user_id": ObjectId(user_id)})
    except PyMongoError:
        vocab_count, correct_chats, total_chats = 0, 0, 0

    feedback = {
        'vocabulary_learned': vocab_count,
        'chat_accuracy': (correct_chats / total_chats * 100) if total_chats > 0 else 0,
        'strengths': [],
        'weaknesses': [],
        'recommendations': []
    }

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

    if not feedback['recommendations']:
        feedback['recommendations'].append('Keep up the great work!')
        feedback['recommendations'].append('Try advanced topics for challenge')

    return feedback


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

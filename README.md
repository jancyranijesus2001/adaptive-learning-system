# Adaptive AI-Based Personalized Learning System

## 🎓 Project Overview

An intelligent, AI-powered English learning platform designed for young learners. The system adapts to each student's learning pace, providing personalized content, interactive exercises, conversational practice, and gamification to enhance vocabulary and grammar skills.

## ✨ Key Features

### Core Modules (10 in total):

1. **User Management Module**
   - Student registration and secure login
   - Profile creation based on age and learning level
   - Secure session management

2. **Pre-Assessment (Pre-Test) Module**
   - Initial assessment to determine student's English proficiency
   - Vocabulary and grammar-based questions
   - Automatic level assignment (Beginner, Intermediate, Advanced)

3. **Personalized Learning Module**
   - Adaptive content delivery based on student performance
   - Dynamic difficulty adjustment
   - Self-paced learning experience

4. **Interactive Learning & Practice Module**
   - Vocabulary learning with definitions and examples
   - Grammar rules with contextual examples
   - Text-to-speech functionality for pronunciation

5. **Conversational Learning (Chat Module)**
   - AI-powered conversational practice
   - Real-time grammar checking and corrections
   - Instant feedback on sentence formation

6. **Gamification Module**
   - Points system for correct answers
   - Achievement badges and levels
   - Daily learning streaks
   - Progress-based rewards

7. **Progress Tracking & Performance Analysis**
   - Detailed learning analytics
   - Vocabulary mastery tracking
   - Grammar accuracy monitoring
   - Visual progress charts

8. **Post-Assessment (Post-Test) Module**
   - Final assessment to measure improvement
   - Comparison with pre-test results
   - Performance analytics

9. **Feedback & Recommendation Module**
   - Personalized strengths and weaknesses analysis
   - Tailored learning recommendations
   - Custom learning path suggestions

10. **Admin/Teacher Monitoring Module**
    - Student progress monitoring
    - System analytics and insights
    - Performance comparisons
    - Engagement tracking

## 🚀 Technology Stack

- **Backend**: Python 3.x with Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Charts**: Chart.js for data visualization
- **Additional**: Web Speech API for text-to-speech

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 🛠️ Installation & Setup

### 1. Clone/Download the Project

```bash
# If you have the project folder
cd adaptive-learning-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

### 4. Access the Application

Open your web browser and navigate to:
```
http://localhost:5000
```

## 👥 Default Login Credentials

### Admin Access:
- **Username**: admin
- **Password**: admin123

### Student Access:
- Students need to register first
- Use the "Register" button on the homepage

## 📖 How to Use

### For Students:

1. **Register**: Create an account with your name, age, and credentials
2. **Login**: Access your personalized dashboard
3. **Take Pre-Test**: Complete the initial assessment (10 questions)
4. **Start Learning**: 
   - Learn new vocabulary and grammar rules
   - Practice with interactive exercises
   - Chat with AI tutor for conversational practice
5. **Track Progress**: Monitor your improvement and achievements
6. **Take Post-Test**: Measure your learning improvement
7. **Get Feedback**: Receive personalized recommendations

### For Administrators:

1. **Login**: Use admin credentials
2. **Monitor**: View all student progress and system analytics
3. **Analyze**: Check average scores and improvement rates
4. **Insights**: Review system effectiveness metrics

## 📊 System Architecture

```
adaptive-learning-system/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── database/
│   └── learning_system.db # SQLite database (auto-created)
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── admin_login.html
│   ├── dashboard.html
│   ├── pre_test.html
│   ├── learning.html
│   ├── practice.html
│   ├── chat.html
│   ├── progress.html
│   ├── post_test.html
│   ├── feedback.html
│   └── admin_dashboard.html
│
└── static/
    ├── css/
    │   └── style.css      # Main stylesheet
    └── js/
        └── main.js        # JavaScript utilities
```

## 🗄️ Database Schema

The system uses 8 main tables:

1. **users** - Student information and credentials
2. **pre_test_results** - Pre-test scores and assigned levels
3. **learning_progress** - Topic-wise learning progress
4. **vocabulary_learned** - Words learned by students
5. **user_points** - Gamification data (points, levels, badges)
6. **chat_history** - Conversational practice records
7. **post_test_results** - Post-test scores and improvements
8. **admins** - Administrator credentials

## 🎮 Gamification Features

- **Points System**: Earn 10 points for correct practice answers
- **Level Up**: Advance levels every 100 points
- **Achievements**: Unlock badges for milestones
  - First Steps (50 points)
  - Rising Star (100 points)
  - On Fire (3-day streak)
  - Dedicated (7-day streak)
  - Word Master (20 words)
  - Scholar (50 words)

## 🤖 AI Features

### Adaptive Learning
- Content difficulty adjusts based on performance
- If accuracy >= 80%: Upgrade to next level
- If accuracy < 50%: Downgrade to easier content

### Grammar Checking
- Capital letter validation
- Punctuation checking
- Subject-verb agreement
- Sentence completeness verification

## 📈 Progress Tracking

Students can view:
- Total points earned
- Current level
- Learning streak days
- Vocabulary words learned
- Grammar accuracy percentage
- Pre-test vs Post-test comparison
- Achievement unlocks

## 🎯 Learning Levels

### Beginner
- Basic vocabulary (cat, dog, house, book)
- Simple present tense
- Basic articles (a, an, the)

### Intermediate
- Advanced vocabulary (achieve, beautiful, continue)
- Past tense
- Comparative adjectives

### Advanced
- Complex vocabulary (accommodate, comprehensive, persuade)
- Present perfect tense
- Conditional sentences

## 🔒 Security Features

- Password-protected accounts
- Session management
- Secure database storage
- User authentication for all protected routes

## 🎨 UI/UX Features

- Responsive design for all devices
- Modern gradient backgrounds
- Smooth animations and transitions
- Interactive cards and buttons
- Real-time feedback
- Progress indicators
- Visual charts and graphs

## 🐛 Troubleshooting

### Common Issues:

1. **Port already in use**
   ```bash
   # Change port in app.py
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Database not found**
   - Database is auto-created on first run
   - Check `database/` folder exists

3. **Module not found**
   ```bash
   pip install -r requirements.txt
   ```

## 📝 Future Enhancements

- [ ] Voice recognition for speaking practice
- [ ] Mobile application
- [ ] More languages support
- [ ] Advanced AI models integration
- [ ] Social learning features
- [ ] Parent dashboard
- [ ] Certificate generation
- [ ] Offline mode

## 🤝 Contributing

This is an educational project. Feel free to:
- Report bugs
- Suggest features
- Improve documentation
- Enhance UI/UX

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with default credentials first

## 🎓 Educational Value

This system demonstrates:
- Full-stack web development
- Database design and management
- Adaptive algorithms
- User authentication
- Data visualization
- Responsive web design
- AI-powered education technology

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Built with**: ❤️ and Python
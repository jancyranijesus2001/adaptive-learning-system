# 🚀 Quick Start Guide

## Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

Or use the startup script:
```bash
./start.sh
```

### Step 3: Open Browser
Navigate to: `http://localhost:5000`

---

## First Time User Guide

### For Students:

1. Click "Register" on the homepage
2. Fill in:
   - Full Name
   - Age (5-18)
   - Username
   - Password
3. Click "Register"
4. Login with your credentials
5. Take the Pre-Test (10 questions)
6. Start learning!

### For Admin:

1. Click "Admin Login"
2. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
3. View student analytics

---

## Testing the System

### Sample Student Journey:

1. **Register** → Create account "John Doe", age 10
2. **Pre-Test** → Answer 5/10 correctly → Assigned "Beginner"
3. **Learning** → Learn 5 vocabulary words
4. **Practice** → Complete 10 exercises
5. **Chat** → Write 5 sentences
6. **Progress** → Check achievements
7. **Post-Test** → Answer 8/10 correctly → 30% improvement!
8. **Feedback** → View recommendations

### Expected Outcomes:

- **Points**: 50-100 points
- **Level**: Level 1-2
- **Achievements**: "First Steps" unlocked
- **Vocabulary**: 5 words learned
- **Improvement**: 20-40%

---

## Key URLs

- Homepage: `http://localhost:5000/`
- Student Login: `http://localhost:5000/login`
- Admin Login: `http://localhost:5000/admin-login`
- Dashboard: `http://localhost:5000/dashboard`

---

## Common Tasks

### Stop the Server:
Press `Ctrl + C` in terminal

### Clear Database (Reset):
Delete `database/learning_system.db` and restart

### Change Port:
Edit `app.py`, line: `app.run(debug=True, host='0.0.0.0', port=5000)`

---

## Troubleshooting

**Can't connect?**
- Check if port 5000 is free
- Try `http://127.0.0.1:5000` instead

**Database error?**
- Ensure `database/` folder exists
- Database auto-creates on first run

**Module not found?**
- Run: `pip install -r requirements.txt`

---

## Need Help?

Check:
1. README.md - Full documentation
2. Terminal output - Error messages
3. Browser console - JavaScript errors

---

**Happy Learning! 🎓**
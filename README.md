# UrbanMatch-PythonTask
# Heartbeat - AI Dating Match

A modern dating web application powered by AI matching algorithms. Heartbeat helps users find compatible matches based on shared interests, age compatibility, and location.



## Features

- 🔐 Secure user authentication
- 👤 Detailed user profiles
- 💝 AI-powered match recommendations
- 🎯 Interest-based matching
- 📍 Location-based matching
- 💫 Modern, responsive UI

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: JWT tokens
- **Security**: Bcrypt encryption


## File Descriptions

### Backend Files
- `main.py` - Core FastAPI application with all routes and endpoints
- `database.py` - SQLAlchemy models and database configuration
- `ai_matcher.py` - AI-powered matching algorithm implementation
- `reset_db.py` - Database initialization and reset script
- `requirements.txt` - List of Python package dependencies

### Frontend Templates
- `login.html` - User authentication interface
- `profile.html` - User profile creation and editing
- `index.html` - Main application interface showing matches



## Features

- **User Authentication**: Login and Signup functionality.
- **Profile Setup**: Users can create and update their profiles.
- **AI-Powered Matching**: Advanced AI algorithms to suggest the best matches for users.
- **Database Management**: Efficient storage and retrieval of user data.
- **Dynamic Web Pages**: Responsive HTML templates for user interactions.

---

## Directory Structure

```plaintext
heartbeat-dating/
├── main.py               # FastAPI application
├── database.py           # Database models and connections
├── ai_matcher.py         # AI-powered matching algorithm
├── reset_db.py           # Script to initialize/reset the database
├── requirements.txt      # Python dependencies
└── templates/            # HTML templates for the application
    ├── login.html        # Login/Signup page
    ├── profile.html      # Profile setup page
    └── index.html        # Main matches page
```



## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/heartbeat-dating.git
   cd heartbeat-dating
   ```

2. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python reset_db.py
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

5. Open the application in your browser at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---




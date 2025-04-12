import pymysql
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'db': os.environ.get('DB_NAME', 'quizbox'),
    'port': 3307,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_admin_id():
    """Get the admin user ID"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE is_admin = TRUE LIMIT 1")
            result = cursor.fetchone()
            if not result:
                raise Exception("No admin user found. Please create an admin user first.")
            return result['id']
    finally:
        conn.close()

def get_theme_id(theme_name):
    """Get theme ID by name, create if not exists"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # Check if theme exists
            cursor.execute("SELECT id FROM themes WHERE name = %s", (theme_name,))
            result = cursor.fetchone()
            if result:
                return result['id']
            
            # Create new theme
            cursor.execute(
                "INSERT INTO themes (name, description) VALUES (%s, %s)",
                (theme_name, f"Default theme for {theme_name}")
            )
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

def populate_default_quizzes():
    """Populate default quizzes for the admin user"""
    admin_id = get_admin_id()
    
    # Define default quizzes
    default_quizzes = [
        # Text answer quizzes
        {
            'quiz_type': 'text',
            'question_text': 'What is the capital of France?',
            'answer_text': 'Paris',
            'theme_name': 'Geography'
        },
        {
            'quiz_type': 'text',
            'question_text': 'What is the largest planet in our solar system?',
            'answer_text': 'Jupiter',
            'theme_name': 'Science'
        },
        
        # Multiple choice quizzes
        {
            'quiz_type': 'multiple_choice',
            'question_text': 'Which of these are programming languages?',
            'answer_text': {
                'options': ['Python', 'Java', 'HTML', 'CSS'],
                'correct': ['Python', 'Java']
            },
            'theme_name': 'Programming'
        },
        {
            'quiz_type': 'multiple_choice',
            'question_text': 'Which of these are data structures?',
            'answer_text': {
                'options': ['List', 'Dictionary', 'Function', 'Class'],
                'correct': ['List', 'Dictionary']
            },
            'theme_name': 'Programming'
        }
    ]
    
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            for quiz in default_quizzes:
                theme_id = get_theme_id(quiz['theme_name'])
                
                # For multiple choice quizzes, convert answer_text to JSON string
                answer_text = quiz['answer_text']
                if quiz['quiz_type'] == 'multiple_choice':
                    answer_text = json.dumps(answer_text)
                
                # Insert quiz
                cursor.execute(
                    """INSERT INTO quizzes 
                       (user_id, quiz_type, question_text, answer_text, theme_id)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (admin_id, quiz['quiz_type'], quiz['question_text'], 
                     answer_text, theme_id)
                )
            
            conn.commit()
            print("Successfully populated default quizzes!")
            
    except Exception as e:
        print(f"Error populating default quizzes: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    populate_default_quizzes() 
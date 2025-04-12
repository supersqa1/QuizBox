import pymysql
import os

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def init_db():
    """Initialize the database with required tables"""
    # First create the database if it doesn't exist
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS quizbox")
            cursor.execute("USE quizbox")
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create api_keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    api_key VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create themes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS themes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create quizzes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    question_text TEXT NOT NULL,
                    answer_text TEXT NOT NULL,
                    structure JSON,
                    theme_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (theme_id) REFERENCES themes(id)
                )
            """)
            
            # Insert default themes
            cursor.execute("SELECT COUNT(*) FROM themes")
            if cursor.fetchone()['COUNT(*)'] == 0:
                default_themes = [
                    ('Python Basics', 'Basic Python concepts and syntax'),
                    ('Data Structures', 'Python data structures and their usage'),
                    ('Functions', 'Function definitions and usage'),
                    ('Object-Oriented Programming', 'Classes and objects in Python'),
                    ('Error Handling', 'Exception handling and debugging'),
                    ('File Operations', 'Working with files in Python'),
                    ('Modules and Packages', 'Importing and using Python modules'),
                    ('Web Development', 'Python web frameworks and concepts')
                ]
                cursor.executemany(
                    "INSERT INTO themes (name, description) VALUES (%s, %s)",
                    default_themes
                )
            
            conn.commit()
            print("Database initialized successfully!")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db() 
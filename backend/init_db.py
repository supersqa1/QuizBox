import pymysql
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def wait_for_mysql(max_retries=30, delay=1):
    """Wait for MySQL to be ready"""
    for i in range(max_retries):
        try:
            conn = pymysql.connect(**DB_CONFIG)
            conn.close()
            print("MySQL is ready!")
            return True
        except pymysql.err.OperationalError as e:
            if i == max_retries - 1:
                print(f"Failed to connect to MySQL after {max_retries} attempts")
                raise e
            print(f"Waiting for MySQL... (attempt {i+1}/{max_retries})")
            time.sleep(delay)
    return False

def init_db():
    """Initialize the database"""
    # Wait for MySQL to be ready
    wait_for_mysql()
    
    # Connect to MySQL server
    conn = pymysql.connect(**DB_CONFIG)
    
    try:
        with conn.cursor() as cursor:
            # Create database if it doesn't exist
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_email (email)
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
                    quiz_type VARCHAR(50) NOT NULL,
                    question_text TEXT NOT NULL,
                    answer_text TEXT,
                    theme_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (theme_id) REFERENCES themes(id)
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
            
            conn.commit()
            print("Database initialized successfully!")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    init_db() 
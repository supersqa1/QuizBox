import pytest
from flask import Flask
import pymysql
import os
from dotenv import load_dotenv
from app import app as flask_app
from werkzeug.security import generate_password_hash

# Load test environment variables
load_dotenv('.env.test')

# Test database configuration
TEST_DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

@pytest.fixture
def app():
    """Create a Flask app for testing"""
    # Update app's DB_CONFIG with test configuration
    from app import DB_CONFIG
    DB_CONFIG.update({
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', 'password'),
        'db': os.environ.get('DB_NAME', 'quizbox_test'),
        'port': int(os.environ.get('DB_PORT', 3307))
    })
    
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": os.environ.get('SECRET_KEY', 'test-secret-key')
    })
    yield flask_app

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def test_db():
    """Create a test database connection"""
    test_config = TEST_DB_CONFIG.copy()
    test_config['db'] = os.environ.get('DB_NAME', 'quizbox_test')
    
    # Create test database
    conn = pymysql.connect(**{k: v for k, v in TEST_DB_CONFIG.items() if k != 'db'})
    try:
        with conn.cursor() as cursor:
            cursor.execute("DROP DATABASE IF EXISTS quizbox_test")
            cursor.execute("CREATE DATABASE quizbox_test")
            cursor.execute("USE quizbox_test")
            
            # Create tables
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
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    api_key VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS themes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quizzes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    quiz_type VARCHAR(20) NOT NULL,
                    question_text TEXT NOT NULL,
                    answer_text TEXT NOT NULL,
                    theme_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (theme_id) REFERENCES themes(id)
                )
            """)
            
            conn.commit()
    finally:
        conn.close()
    
    # Return test database connection
    return pymysql.connect(**test_config)

@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    with test_db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            ('Test User', 'test@example.com', generate_password_hash('password123'))
        )
        user_id = cursor.lastrowid
        
        # Create API key
        api_key = 'test-api-key'
        cursor.execute(
            "INSERT INTO api_keys (user_id, api_key) VALUES (%s, %s)",
            (user_id, api_key)
        )
        test_db.commit()
        
        return {
            'id': user_id,
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'api_key': api_key
        }

@pytest.fixture
def test_admin(test_db):
    """Create a test admin user"""
    password = "admin123"  # Use a known password for admin tests
    password_hash = generate_password_hash(password)
    
    with test_db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
            ("Admin User", "admin@example.com", password_hash, True)
        )
        user_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO api_keys (user_id, api_key) VALUES (%s, %s)",
            (user_id, "admin-api-key")
        )
        
        test_db.commit()
    
    return {
        "id": user_id,
        "name": "Admin User",
        "email": "admin@example.com",
        "api_key": "admin-api-key"
    }

@pytest.fixture
def test_theme(test_db):
    """Create a test theme"""
    with test_db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO themes (name, description) VALUES (%s, %s)",
            ("Test Theme", "Test Description")
        )
        theme_id = cursor.lastrowid
        test_db.commit()
    
    return {
        "id": theme_id,
        "name": "Test Theme",
        "description": "Test Description"
    } 
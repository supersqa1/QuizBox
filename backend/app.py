from flask import Flask, request, jsonify, session
import pymysql
import os
import secrets
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('quizbox-backend')

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'mysql'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'db': os.environ.get('DB_NAME', 'quizbox'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    """Get database connection"""
    return pymysql.connect(**DB_CONFIG)

def require_api_key(f):
    """Decorator to require API key for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute("SELECT user_id FROM api_keys WHERE api_key = %s", (api_key,))
                result = cursor.fetchone()
                if not result:
                    return jsonify({'error': 'Invalid API key'}), 401
                request.user_id = result['user_id']
        finally:
            db.close()
        
        return f(*args, **kwargs)
    return decorated_function

def require_login(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for API key first
        api_key = request.headers.get('x-api-key')
        if api_key:
            db = get_db()
            try:
                with db.cursor() as cursor:
                    cursor.execute("SELECT user_id FROM api_keys WHERE api_key = %s", (api_key,))
                    result = cursor.fetchone()
                    if result:
                        request.user_id = result['user_id']
                        return f(*args, **kwargs)
            finally:
                db.close()
        
        # If no valid API key, check for session
        if 'user_id' not in session:
            return jsonify({'error': 'Login required'}), 401
        
        request.user_id = session['user_id']
        return f(*args, **kwargs)
    return decorated_function

def check_admin_exists():
    """Check if admin user exists"""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE is_admin = TRUE")
            return cursor.fetchone() is not None
    finally:
        db.close()

@app.route('/setup/status', methods=['GET'])
def setup_status():
    """Check if setup is needed"""
    return jsonify({'needs_setup': not check_admin_exists()})

@app.route('/setup', methods=['POST'])
def setup_admin():
    """Create admin user"""
    if check_admin_exists():
        logger.warning("Attempt to create admin when one already exists")
        return jsonify({'error': 'Admin already exists'}), 400
    
    data = request.get_json()
    logger.debug(f"Setup data received: {data}")
    
    if not all(k in data for k in ('name', 'email', 'password')):
        logger.error("Missing required fields in setup data")
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            # Create admin user
            password_hash = generate_password_hash(data['password'])
            logger.debug(f"Creating admin user: {data['name']}, {data['email']}")
            
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
                (data['name'], data['email'], password_hash, True)
            )
            user_id = cursor.lastrowid
            logger.debug(f"Created admin user with ID: {user_id}")
            
            # Generate API key
            api_key = secrets.token_urlsafe(32)
            cursor.execute(
                "INSERT INTO api_keys (user_id, api_key) VALUES (%s, %s)",
                (user_id, api_key)
            )
            
            db.commit()
            logger.info("Admin user created successfully")
            
            # Set session for the new admin
            session['user_id'] = user_id
            
            return jsonify({
                'message': 'Admin user created successfully',
                'api_key': api_key
            }), 201
    except Exception as e:
        logger.error("Error during admin setup", exc_info=True)
        db.rollback()
        return jsonify({'error': f'Failed to create admin user: {str(e)}'}), 500
    finally:
        db.close()

@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    if not all(k in data for k in ('name', 'email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
            if cursor.fetchone():
                return jsonify({'error': 'Email already registered'}), 400
            
            # Create user
            password_hash = generate_password_hash(data['password'])
            cursor.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
                (data['name'], data['email'], password_hash)
            )
            user_id = cursor.lastrowid
            
            # Generate API key
            api_key = secrets.token_urlsafe(32)
            cursor.execute(
                "INSERT INTO api_keys (user_id, api_key) VALUES (%s, %s)",
                (user_id, api_key)
            )
            
            db.commit()
            return jsonify({
                'message': 'User registered successfully',
                'api_key': api_key
            }), 201
    finally:
        db.close()

@app.route('/login', methods=['POST'])
def login():
    """Login user and start session"""
    data = request.get_json()
    if not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Missing email or password'}), 400
    
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, password_hash FROM users WHERE email = %s",
                (data['email'],)
            )
            user = cursor.fetchone()
            
            if not user or not check_password_hash(user['password_hash'], data['password']):
                return jsonify({'error': 'Invalid email or password'}), 401
            
            session['user_id'] = user['id']
            return jsonify({'message': 'Logged in successfully'})
    finally:
        db.close()

@app.route('/logout', methods=['GET'])
def logout():
    """Logout user and clear session"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/me', methods=['GET'])
@require_login
def get_current_user():
    """Get current user info"""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, email FROM users WHERE id = %s",
                (session['user_id'],)
            )
            user = cursor.fetchone()
            return jsonify(user)
    finally:
        db.close()

@app.route('/me/api-key', methods=['GET'])
@require_login
def get_api_key():
    """Get user's API key"""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT api_key FROM api_keys WHERE user_id = %s",
                (request.user_id,)
            )
            result = cursor.fetchone()
            if not result:
                return jsonify({'error': 'API key not found'}), 404
            return jsonify({'api_key': result['api_key']})
    finally:
        db.close()

@app.route('/me/api-key/refresh', methods=['POST'])
@require_login
def refresh_api_key():
    """Refresh user's API key"""
    db = get_db()
    try:
        with db.cursor() as cursor:
            # Generate new API key
            new_api_key = secrets.token_urlsafe(32)
            
            # Update API key in database
            cursor.execute(
                "UPDATE api_keys SET api_key = %s WHERE user_id = %s",
                (new_api_key, session['user_id'])
            )
            
            if cursor.rowcount == 0:
                # If no existing API key, create one
                cursor.execute(
                    "INSERT INTO api_keys (user_id, api_key) VALUES (%s, %s)",
                    (session['user_id'], new_api_key)
                )
            
            db.commit()
            return jsonify({'api_key': new_api_key})
    except Exception as e:
        logger.error("Error refreshing API key", exc_info=True)
        db.rollback()
        return jsonify({'error': 'Failed to refresh API key'}), 500
    finally:
        db.close()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Try to connect to the database
        db = get_db()
        db.close()
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/themes', methods=['GET'])
def get_themes():
    """Get all available themes"""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT id, name FROM themes")
            themes = cursor.fetchall()
            logger.debug(f"Found {len(themes)} themes: {themes}")
            return jsonify(themes)  # Return themes array directly
    except Exception as e:
        logger.error("Error fetching themes", exc_info=True)
        return jsonify({'error': 'Failed to fetch themes'}), 500
    finally:
        db.close()

@app.route('/quizzes', methods=['POST'])
@require_login
def create_quiz():
    db = get_db()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['quiz_type', 'question_text', 'answer_text', 'theme_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
                
        # Validate quiz type
        if data['quiz_type'] not in ['text', 'multiple_choice']:
            return jsonify({'error': 'Invalid quiz type'}), 400
            
        # For multiple choice quizzes, validate answer_text format
        if data['quiz_type'] == 'multiple_choice':
            try:
                if not isinstance(data['answer_text'], dict):
                    return jsonify({'error': 'Answer text must be a JSON object for multiple choice quizzes'}), 400
                if 'options' not in data['answer_text'] or 'correct' not in data['answer_text']:
                    return jsonify({'error': 'Answer text must contain options and correct fields for multiple choice quizzes'}), 400
                data['answer_text'] = json.dumps(data['answer_text'])
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid JSON format for answer text'}), 400
                
        with db.cursor() as cursor:
            cursor.execute(
                """INSERT INTO quizzes (user_id, quiz_type, question_text, answer_text, theme_id) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (request.user_id, data['quiz_type'], data['question_text'], 
                 data['answer_text'], data['theme_id'])
            )
            quiz_id = cursor.lastrowid
            db.commit()
            
            return jsonify({
                'message': 'Quiz created successfully',
                'id': quiz_id
            }), 201
        
    except Exception as e:
        db.rollback()
        app.logger.error(f"Error creating quiz: {str(e)}")
        return jsonify({'error': 'Failed to create quiz'}), 500
    finally:
        db.close()

@app.route('/quiz/mine', methods=['GET'])
@require_login
def get_my_quizzes():
    """Get all quizzes created by the current user"""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                """SELECT q.id, q.question_text, q.answer_text, q.structure, q.theme_id, t.name as theme_name
                   FROM quizzes q
                   LEFT JOIN themes t ON q.theme_id = t.id
                   WHERE q.user_id = %s""",
                (request.user_id,)
            )
            quizzes = cursor.fetchall()
            return jsonify(quizzes)
    finally:
        db.close()

@app.route('/quizzes/default', methods=['GET'])
def get_default_quizzes():
    """Get all quizzes created by admin users"""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                """SELECT q.id, q.quiz_type, q.question_text, q.answer_text, q.theme_id, t.name as theme_name, u.name as created_by
                   FROM quizzes q
                   LEFT JOIN themes t ON q.theme_id = t.id
                   JOIN users u ON q.user_id = u.id
                   WHERE u.is_admin = TRUE"""
            )
            quizzes = cursor.fetchall()
            
            # For multiple choice quizzes, parse the answer_text as JSON
            for quiz in quizzes:
                if quiz['quiz_type'] == 'multiple_choice':
                    try:
                        quiz['answer_text'] = json.loads(quiz['answer_text'])
                    except (json.JSONDecodeError, TypeError):
                        # If JSON parsing fails, leave as is
                        pass
            
            return jsonify(quizzes)
    finally:
        db.close()

@app.route('/quizzes', methods=['GET'])
@require_login
def get_quizzes():
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                """SELECT q.id, q.user_id, q.quiz_type, q.question_text, q.answer_text, q.theme_id, 
                          t.name as theme_name, q.created_at 
                   FROM quizzes q
                   LEFT JOIN themes t ON q.theme_id = t.id
                   WHERE q.user_id = %s""",
                (request.user_id,)
            )
            quizzes = cursor.fetchall()
            
            # For multiple choice quizzes, parse the answer_text as JSON
            for quiz in quizzes:
                if quiz['quiz_type'] == 'multiple_choice':
                    try:
                        quiz['answer_text'] = json.loads(quiz['answer_text'])
                    except (json.JSONDecodeError, TypeError):
                        # If JSON parsing fails, leave as is
                        pass
                    
            return jsonify(quizzes), 200
            
    except Exception as e:
        app.logger.error(f"Error retrieving quizzes: {str(e)}")
        return jsonify({'error': 'Failed to retrieve quizzes'}), 500
    finally:
        db.close()

@app.route('/themes/<int:theme_id>/quiz', methods=['GET'])
@require_login
def get_theme_quizzes(theme_id):
    """Get all quizzes for a theme"""
    db = get_db()
    try:
        with db.cursor() as cursor:
            # First check if theme exists
            cursor.execute("SELECT id FROM themes WHERE id = %s", (theme_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Theme not found'}), 404
            
            # Get quizzes for theme
            cursor.execute(
                """SELECT q.*, t.name as theme_name
                   FROM quizzes q
                   JOIN themes t ON q.theme_id = t.id
                   WHERE t.id = %s""",
                (theme_id,)
            )
            quizzes = cursor.fetchall()
            
            # Parse structure JSON for each quiz
            for quiz in quizzes:
                if quiz['structure']:
                    quiz['structure'] = json.loads(quiz['structure'])
            
            return jsonify(quizzes)
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True) 
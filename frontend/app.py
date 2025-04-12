from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import requests
import os
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('quizbox-frontend')

# Backend API URL - using the container name from docker-compose
BACKEND_URL = 'http://quizbox-backend:5050'

def needs_setup():
    """Check if setup is needed"""
    try:
        response = requests.get(f'{BACKEND_URL}/setup/status')
        if response.status_code == 200:
            return response.json().get('needs_setup', True)
        return True
    except requests.exceptions.RequestException:
        return True

@app.route('/')
def index():
    if needs_setup():
        return redirect(url_for('setup'))
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Initial setup page"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.debug(f"Frontend received setup data: {data}")
            
            response = requests.post(f'{BACKEND_URL}/setup', json=data)
            logger.debug(f"Backend response status: {response.status_code}")
            logger.debug(f"Backend response content: {response.text}")
            
            if response.status_code == 201:
                # Get the session cookie from the backend response
                session_cookie = response.cookies.get('session')
                if session_cookie:
                    session['user_id'] = session_cookie
                return redirect(url_for('dashboard'))
            logger.error(f"Setup failed with response: {response.text}")
            return render_template('setup.html', error=f'Setup failed: {response.text}')
        except Exception as e:
            logger.error("Setup error", exc_info=True)
            return render_template('setup.html', error=f'Setup failed: {str(e)}')
    return render_template('setup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login user"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.debug(f"Login attempt with data: {data}")
            
            response = requests.post(f'{BACKEND_URL}/login', json=data)
            logger.debug(f"Backend login response: {response.status_code}")
            
            if response.status_code == 200:
                # Get the session cookie from the backend response
                session_cookie = response.cookies.get('session')
                if session_cookie:
                    session['user_id'] = session_cookie
                    logger.debug(f"User logged in with session: {session_cookie}")
                    return jsonify({'message': 'Login successful'}), 200
            logger.error(f"Login failed with response: {response.text}")
            return jsonify({'error': 'Invalid credentials'}), 401
        except Exception as e:
            logger.error("Login error", exc_info=True)
            return jsonify({'error': str(e)}), 500
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.debug(f"Registration attempt with data: {data}")
            
            response = requests.post(f'{BACKEND_URL}/register', json=data)
            logger.debug(f"Backend registration response: {response.status_code}")
            
            if response.status_code == 201:
                # Get the session cookie from the backend response
                session_cookie = response.cookies.get('session')
                if session_cookie:
                    session['user_id'] = session_cookie
                    logger.debug(f"User registered with session: {session_cookie}")
                    return jsonify({'message': 'Registration successful'}), 201
            logger.error(f"Registration failed with response: {response.text}")
            return jsonify({'error': 'Registration failed'}), 400
        except Exception as e:
            logger.error("Registration error", exc_info=True)
            return jsonify({'error': str(e)}), 500
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Show user's dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get user's API key
        api_key_response = requests.get(
            f'{BACKEND_URL}/me/api-key',
            cookies={'session': session.get('user_id')}
        )
        if api_key_response.status_code != 200:
            logger.error("Failed to get API key")
            return render_template('dashboard.html', error='Failed to get API key')
        
        api_key = api_key_response.json()['api_key']
        
        # Get user's quizzes
        quizzes_response = requests.get(
            f'{BACKEND_URL}/quizzes',  # Updated endpoint
            headers={'x-api-key': api_key},
            cookies={'session': session.get('user_id')}
        )
        quizzes = quizzes_response.json() if quizzes_response.status_code == 200 else []
        
        # Get default quizzes
        default_response = requests.get(f'{BACKEND_URL}/quizzes/default')
        default_quizzes = default_response.json() if default_response.status_code == 200 else []
        
        return render_template('dashboard.html', quizzes=quizzes, default_quizzes=default_quizzes)
    except Exception as e:
        logger.error("Error loading dashboard", exc_info=True)
        return render_template('dashboard.html', error=str(e))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/quiz/new', methods=['GET', 'POST'])
def new_quiz():
    """Create a new quiz"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Get user's API key
            api_key_response = requests.get(
                f'{BACKEND_URL}/me/api-key',
                cookies={'session': session.get('user_id')}
            )
            if api_key_response.status_code != 200:
                logger.error("Failed to get API key")
                return render_template('new_quiz.html', error='Failed to get API key')
            
            api_key = api_key_response.json()['api_key']
            
            # Create quiz
            quiz_data = request.get_json()  # Get JSON data instead of form data
            
            response = requests.post(
                f'{BACKEND_URL}/quizzes',  # Updated endpoint
                json=quiz_data,
                headers={
                    'x-api-key': api_key,
                    'Content-Type': 'application/json'
                },
                cookies={'session': session.get('user_id')}
            )
            
            if response.status_code == 201:
                return redirect(url_for('dashboard'))
            
            error_msg = response.json().get('error', 'Failed to create quiz')
            logger.error(f"Failed to create quiz: {error_msg}")
            return jsonify({'error': error_msg}), response.status_code
            
        except Exception as e:
            logger.error("Error creating quiz", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    # GET request - show form
    try:
        # Get themes
        logger.info("Fetching themes from backend...")
        themes_response = requests.get(f'{BACKEND_URL}/themes')
        logger.info(f"Themes response status: {themes_response.status_code}")
        logger.info(f"Themes response content: {themes_response.text}")
        
        if themes_response.status_code == 200:
            themes = themes_response.json()  # Themes array is returned directly now
            logger.info(f"Retrieved themes: {themes}")
            return render_template('new_quiz.html', themes=themes)
        else:
            logger.error(f"Failed to get themes: {themes_response.text}")
            return render_template('new_quiz.html', themes=[], error='Failed to load themes')
    except Exception as e:
        logger.error("Error getting themes", exc_info=True)
        return render_template('new_quiz.html', themes=[], error=str(e))

@app.route('/settings')
def settings():
    """Settings page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get user's API key
        api_key_response = requests.get(
            f'{BACKEND_URL}/me/api-key',
            cookies={'session': session.get('user_id')}
        )
        if api_key_response.status_code != 200:
            return render_template('settings.html', error='Failed to get API key')
        
        api_key = api_key_response.json()['api_key']
        return render_template('settings.html', api_key=api_key)
    except Exception as e:
        logger.error("Error in settings", exc_info=True)
        return render_template('settings.html', error=str(e))

@app.route('/settings/refresh-key', methods=['POST'])
def refresh_api_key():
    """Refresh user's API key"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        # Get new API key
        response = requests.post(
            f'{BACKEND_URL}/me/api-key/refresh',
            cookies={'session': session.get('user_id')}
        )
        if response.status_code != 200:
            return jsonify({'error': 'Failed to refresh API key'}), response.status_code
        
        return jsonify(response.json())
    except Exception as e:
        logger.error("Error refreshing API key", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5151, debug=True) 
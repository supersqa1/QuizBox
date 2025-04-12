import pytest
from werkzeug.security import generate_password_hash

def test_setup_status(client, test_db):
    """Test setup status endpoint"""
    # When no admin exists
    response = client.get('/setup/status')
    assert response.status_code == 200
    assert response.json == {'needs_setup': True}
    
    # When admin exists
    with test_db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
            ("Admin", "admin@example.com", "hashed_password", True)
        )
        test_db.commit()
    
    response = client.get('/setup/status')
    assert response.status_code == 200
    assert response.json == {'needs_setup': False}

def test_setup_admin(client, test_db):
    """Test admin setup endpoint"""
    # Test successful setup
    data = {
        'name': 'Admin User',
        'email': 'admin@example.com',
        'password': 'password123'
    }
    response = client.post('/setup', json=data)
    assert response.status_code == 201
    assert 'message' in response.json
    assert 'api_key' in response.json
    
    # Test setup when admin already exists
    response = client.post('/setup', json=data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_register(client, test_db):
    """Test user registration"""
    # Test successful registration
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    }
    response = client.post('/register', json=data)
    assert response.status_code == 201
    assert 'message' in response.json
    assert 'api_key' in response.json
    
    # Test duplicate email
    response = client.post('/register', json=data)
    assert response.status_code == 400
    assert 'error' in response.json
    
    # Test missing fields
    data = {'name': 'Test User'}
    response = client.post('/register', json=data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_login(client, test_db, test_user):
    """Test user login"""
    # Test successful login
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200
    assert 'message' in response.json
    assert 'session' in response.headers.get('Set-Cookie', '')
    
    # Test invalid credentials
    data = {
        'email': test_user['email'],
        'password': 'wrongpassword'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 401
    assert 'error' in response.json
    
    # Test missing fields
    data = {'email': test_user['email']}
    response = client.post('/login', json=data)
    assert response.status_code == 400
    assert 'error' in response.json

def test_logout(client, test_db, test_user):
    """Test user logout"""
    # First login to get session
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200

    # Test logout
    response = client.get('/logout')
    assert response.status_code == 200
    assert 'message' in response.json
    
    # Check that the session cookie is expired (Max-Age=0)
    cookie = response.headers.get('Set-Cookie', '')
    assert 'Max-Age=0' in cookie
    
    # Verify we can't access protected routes after logout
    response = client.get('/me')
    assert response.status_code == 401

def test_get_current_user(client, test_db, test_user):
    """Test getting current user info"""
    # First login to get session
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200
    
    # Test getting user info
    response = client.get('/me')
    assert response.status_code == 200
    assert response.json['id'] == test_user['id']
    assert response.json['name'] == test_user['name']
    assert response.json['email'] == test_user['email']
    
    # Test without session
    client.get('/logout')
    response = client.get('/me')
    assert response.status_code == 401
    assert 'error' in response.json

def test_get_api_key(client, test_db, test_user):
    """Test getting user's API key"""
    # First login to get session
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200
    
    # Test getting API key
    response = client.get('/me/api-key')
    assert response.status_code == 200
    assert 'api_key' in response.json
    assert response.json['api_key'] == test_user['api_key']
    
    # Test without session
    client.get('/logout')
    response = client.get('/me/api-key')
    assert response.status_code == 401
    assert 'error' in response.json 
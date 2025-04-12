import pytest
import json

def test_create_quiz(client, test_db, test_user):
    """Test creating a new quiz"""
    # First login to get session
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200

    # Test creating quiz with API key
    quiz_data = {
        'quiz_type': 'multiple_choice',
        'question_text': 'What is Python?',
        'answer_text': {
            'options': ['A programming language', 'A snake', 'A car'],
            'correct': 'A programming language'
        },
        'theme_id': None
    }
    response = client.post(
        '/quizzes',
        json=quiz_data,
        headers={'x-api-key': test_user['api_key']}
    )
    assert response.status_code == 201

def test_get_user_quizzes(client, test_db, test_user):
    """Test getting user's quizzes"""
    # First login to get session
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200

    # Create a test quiz
    quiz_data = {
        'quiz_type': 'text',
        'question_text': 'Test Question',
        'answer_text': 'Test Answer',
        'theme_id': None
    }
    response = client.post(
        '/quizzes',
        json=quiz_data,
        headers={'x-api-key': test_user['api_key']}
    )
    assert response.status_code == 201

    # Get user's quizzes
    response = client.get('/quizzes', headers={'x-api-key': test_user['api_key']})
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['question_text'] == 'Test Question'

def test_get_default_quizzes(client, test_db, test_admin):
    """Test getting admin's default quizzes"""
    # First login as admin
    data = {
        'email': test_admin['email'],
        'password': 'admin123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200

    # Create a default quiz
    quiz_data = {
        'quiz_type': 'text',
        'question_text': 'Default Question',
        'answer_text': 'Default Answer',
        'theme_id': None
    }
    response = client.post(
        '/quizzes',
        json=quiz_data,
        headers={'x-api-key': test_admin['api_key']}
    )
    assert response.status_code == 201

    # Get default quizzes
    response = client.get('/quizzes/default')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['question_text'] == 'Default Question'

def test_get_specific_quiz(client, test_db, test_user):
    """Test getting a specific quiz"""
    # First login to get session
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200

    # Create a test quiz
    quiz_data = {
        'quiz_type': 'text',
        'question_text': 'Specific Question',
        'answer_text': 'Specific Answer',
        'theme_id': None
    }
    response = client.post(
        '/quizzes',
        json=quiz_data,
        headers={'x-api-key': test_user['api_key']}
    )
    assert response.status_code == 201
    quiz_id = response.get_json()['id']

    # Get the specific quiz
    response = client.get(f'/quizzes/{quiz_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['question_text'] == 'Specific Question'

def test_get_themes(client, test_user):
    """Test getting themes"""
    # First log in
    response = client.post('/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    assert response.status_code == 200

    # Now get themes
    response = client.get('/themes')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)  # Themes are returned as an array 
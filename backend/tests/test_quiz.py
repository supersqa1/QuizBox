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
        'question_text': 'What is Python?',
        'answer_text': 'A programming language',
        'structure': {
            'type': 'multiple_choice',
            'options': ['A programming language', 'A snake', 'A car']
        },
        'theme_id': None
    }
    response = client.post(
        '/quiz',
        json=quiz_data,
        headers={'x-api-key': test_user['api_key']}
    )
    assert response.status_code == 201
    assert 'id' in response.json
    assert response.json['question_text'] == quiz_data['question_text']
    assert response.json['answer_text'] == quiz_data['answer_text']
    assert response.json['structure'] == quiz_data['structure']

    # Test creating quiz without API key
    response = client.post('/quiz', json=quiz_data)
    assert response.status_code == 401

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
        'question_text': 'Test Question',
        'answer_text': 'Test Answer',
        'structure': {'type': 'text'},
        'theme_id': None
    }
    response = client.post(
        '/quiz',
        json=quiz_data,
        headers={'x-api-key': test_user['api_key']}
    )
    assert response.status_code == 201
    quiz_id = response.json['id']

    # Test getting user's quizzes
    response = client.get('/quiz/mine')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['id'] == quiz_id
    assert response.json[0]['question_text'] == quiz_data['question_text']

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
        'question_text': 'Default Question',
        'answer_text': 'Default Answer',
        'structure': {'type': 'text'},
        'theme_id': None
    }
    response = client.post(
        '/quiz',
        json=quiz_data,
        headers={'x-api-key': test_admin['api_key']}
    )
    assert response.status_code == 201
    quiz_id = response.json['id']

    # Test getting default quizzes
    response = client.get('/quiz/default')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['id'] == quiz_id
    assert response.json[0]['question_text'] == quiz_data['question_text']

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
        'question_text': 'Specific Question',
        'answer_text': 'Specific Answer',
        'structure': {'type': 'text'},
        'theme_id': None
    }
    response = client.post(
        '/quiz',
        json=quiz_data,
        headers={'x-api-key': test_user['api_key']}
    )
    assert response.status_code == 201
    quiz_id = response.json['id']

    # Test getting specific quiz
    response = client.get(f'/quiz/{quiz_id}')
    assert response.status_code == 200
    assert response.json['id'] == quiz_id
    assert response.json['question_text'] == quiz_data['question_text']
    assert response.json['answer_text'] == quiz_data['answer_text']

    # Test getting non-existent quiz
    response = client.get('/quiz/999')
    assert response.status_code == 404

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
    assert 'themes' in data
    assert isinstance(data['themes'], list) 
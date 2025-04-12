import pytest

def test_get_themes(client, test_db, test_theme, test_user):
    """Test getting all themes"""
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
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['name'] == test_theme['name']

def test_get_theme_quizzes(client, test_db, test_theme, test_user):
    """Test getting quizzes in a theme"""
    # First login to get session
    data = {
        'email': test_user['email'],
        'password': 'password123'
    }
    response = client.post('/login', json=data)
    assert response.status_code == 200

    # Create a quiz with the theme
    quiz_data = {
        'quiz_type': 'text',
        'question_text': 'Theme Question',
        'answer_text': 'Theme Answer',
        'theme_id': test_theme['id']
    }
    response = client.post(
        '/quizzes',
        json=quiz_data,
        headers={'x-api-key': test_user['api_key']}
    )
    assert response.status_code == 201

    # Get quizzes for the theme
    response = client.get(f'/themes/{test_theme["id"]}/quiz')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]['question_text'] == 'Theme Question'

    # Test getting quizzes for non-existent theme
    response = client.get('/themes/999/quiz')
    assert response.status_code == 404 
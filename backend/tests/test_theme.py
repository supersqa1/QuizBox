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
    data = response.json
    assert 'themes' in data
    assert isinstance(data['themes'], list)
    assert len(data['themes']) > 0
    theme = data['themes'][0]
    assert theme['id'] == test_theme['id']
    assert theme['name'] == test_theme['name']
    assert theme['description'] == test_theme['description']

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
        'question_text': 'Theme Question',
        'answer_text': 'Theme Answer',
        'structure': {'type': 'text'},
        'theme_id': test_theme['id']
    }
    response = client.post(
        '/quiz',
        json=quiz_data,
        headers={'x-api-key': test_user['api_key']}
    )
    assert response.status_code == 201
    quiz_id = response.json['id']

    # Test getting quizzes in theme
    response = client.get(f'/themes/{test_theme["id"]}/quiz')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['id'] == quiz_id
    assert response.json[0]['question_text'] == quiz_data['question_text']
    assert response.json[0]['theme_id'] == test_theme['id']

    # Test getting quizzes for non-existent theme
    response = client.get('/themes/999/quiz')
    assert response.status_code == 404 
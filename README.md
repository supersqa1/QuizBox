# QuizBox

QuizBox is a modern quiz application that allows users to create, manage, and take quizzes. It features a clean, intuitive interface and robust API support.

## Features

- User authentication and authorization
- Quiz creation and management
- API support for integration with other applications
- Interactive Swagger documentation
- Docker-based deployment
- MySQL database backend

## Prerequisites

- Docker and Docker Compose
- Python 3.13 or higher
- MySQL 8.0

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/QuizBox.git
cd QuizBox
```

2. Start the application using Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:5151
- Backend API: http://localhost:5050
- MySQL: localhost:3307

## API Documentation

QuizBox provides comprehensive API documentation through Swagger UI. You can access it in two ways:

1. **Interactive Swagger UI**:
   - Visit http://localhost:5151/api/
   - This provides an interactive interface to explore and test all available endpoints

2. **OpenAPI Specification**:
   - Access the raw OpenAPI specification at http://localhost:5151/api/swagger.json
   - This can be imported into tools like Postman

### Importing to Postman

To import the API specification into Postman:

1. Open Postman
2. Click "Import"
3. Enter the URL: http://localhost:5151/api/swagger.json
4. Click "Import"

### Example API Endpoints

#### Authentication
- **Login**: `POST /api/auth/login`
  ```json
  {
    "email": "user@example.com",
    "password": "yourpassword"
  }
  ```

- **Register**: `POST /api/auth/register`
  ```json
  {
    "email": "newuser@example.com",
    "password": "newpassword",
    "name": "New User"
  }
  ```

#### Quizzes
- **Create Quiz**: `POST /api/quizzes`
  ```json
  {
    "title": "General Knowledge Quiz",
    "description": "Test your general knowledge",
    "theme": "general",
    "questions": [
      {
        "text": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct_answer": 2
      }
    ]
  }
  ```

- **List Quizzes**: `GET /api/quizzes`
- **Get Quiz**: `GET /api/quizzes/{quiz_id}`

#### User Management
- **Get API Key**: `GET /api/users/me/api-key`
- **Refresh API Key**: `POST /api/users/me/api-key`

## Development

### Project Structure

```
QuizBox/
├── backend/           # Backend Flask application
├── frontend/          # Frontend Flask application
├── docker-compose.yml # Docker Compose configuration
└── README.md         # This file
```

### Environment Variables

The application uses the following environment variables:

- `SECRET_KEY`: Secret key for session management
- `DB_HOST`: MySQL host (default: mysql)
- `DB_USER`: MySQL username (default: root)
- `DB_PASSWORD`: MySQL password
- `DB_NAME`: MySQL database name (default: quizbox)

### Running Tests

To run the test suite:

```bash
docker-compose exec backend pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
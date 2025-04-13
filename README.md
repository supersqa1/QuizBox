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

### Accessing Swagger Documentation

Once the application is running, you can access the API documentation in several ways:

1. **Interactive Swagger UI**:
   - Open your web browser
   - Navigate to http://localhost:5151/api/
   - You'll see a complete interactive documentation of all available endpoints
   - You can:
     - Browse all available endpoints
     - See request/response schemas
     - Try out the APIs directly from the browser
     - View example requests and responses

2. **OpenAPI Specification (Swagger JSON)**:
   - Access the raw OpenAPI specification at http://localhost:5151/api/swagger.json
   - This JSON file contains the complete API specification
   - You can use this to:
     - Import into API tools like Postman
     - Generate client libraries
     - Use with other API documentation tools

### Importing to Postman

To import the API specification into Postman:

1. Open Postman
2. Click "Import" in the top-left corner
3. Choose the "Link" tab
4. Enter the URL: http://localhost:5151/api/swagger.json
5. Click "Import"

If you have trouble importing directly from the URL, you can:
1. Open http://localhost:5151/api/swagger.json in your browser
2. Save the JSON file to your computer
3. In Postman, click "Import" and select the saved file

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
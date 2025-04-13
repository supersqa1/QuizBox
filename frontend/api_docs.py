from flask_restx import Api, Resource, fields
from flask import Blueprint

# Create a Blueprint for the API documentation
api_bp = Blueprint('api', __name__)
api = Api(api_bp, version='1.0', title='QuizBox API',
          description='A comprehensive API for QuizBox application')

# Namespaces
auth_ns = api.namespace('auth', description='Authentication operations')
quiz_ns = api.namespace('quizzes', description='Quiz operations')
user_ns = api.namespace('users', description='User operations')

# Models
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

register_model = api.model('Register', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'name': fields.String(required=True, description='User name')
})

quiz_model = api.model('Quiz', {
    'title': fields.String(required=True, description='Quiz title'),
    'description': fields.String(description='Quiz description'),
    'theme': fields.String(description='Quiz theme'),
    'questions': fields.List(fields.Nested(api.model('Question', {
        'text': fields.String(required=True),
        'options': fields.List(fields.String),
        'correct_answer': fields.Integer(required=True)
    })))
})

# Authentication endpoints
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('login')
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Success')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """User login"""
        pass

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.doc('register')
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User created')
    @auth_ns.response(400, 'Invalid input')
    def post(self):
        """Register a new user"""
        pass

# Quiz endpoints
@quiz_ns.route('/')
class QuizList(Resource):
    @quiz_ns.doc('list_quizzes')
    @quiz_ns.response(200, 'Success')
    def get(self):
        """List all quizzes"""
        pass

    @quiz_ns.doc('create_quiz')
    @quiz_ns.expect(quiz_model)
    @quiz_ns.response(201, 'Quiz created')
    def post(self):
        """Create a new quiz"""
        pass

@quiz_ns.route('/<int:quiz_id>')
@quiz_ns.param('quiz_id', 'The quiz identifier')
class Quiz(Resource):
    @quiz_ns.doc('get_quiz')
    @quiz_ns.response(200, 'Success')
    @quiz_ns.response(404, 'Quiz not found')
    def get(self, quiz_id):
        """Get a specific quiz"""
        pass

# User endpoints
@user_ns.route('/me/api-key')
class UserAPIKey(Resource):
    @user_ns.doc('get_api_key')
    @user_ns.response(200, 'Success')
    def get(self):
        """Get user's API key"""
        pass

    @user_ns.doc('refresh_api_key')
    @user_ns.response(200, 'Success')
    def post(self):
        """Refresh user's API key"""
        pass 
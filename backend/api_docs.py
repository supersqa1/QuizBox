from flask_restx import Api, Resource, fields, Namespace
from flask import url_for

# Create API instance
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'x-api-key'
    }
}

api = Api(
    title='QuizBox API',
    version='1.0',
    description='API for managing quizzes and themes',
    authorizations=authorizations,
    security='apikey'
)

# Create namespaces
auth_ns = Namespace('auth', description='Authentication operations')
quiz_ns = Namespace('quizzes', description='Quiz operations')
theme_ns = Namespace('themes', description='Theme operations')
user_ns = Namespace('me', description='User operations')

# Add namespaces to API
api.add_namespace(auth_ns)
api.add_namespace(quiz_ns)
api.add_namespace(theme_ns)
api.add_namespace(user_ns)

# Models
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User identifier'),
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email')
})

theme_model = api.model('Theme', {
    'id': fields.Integer(readonly=True, description='Theme identifier'),
    'name': fields.String(required=True, description='Theme name'),
    'description': fields.String(description='Theme description')
})

quiz_answer_model = api.model('QuizAnswer', {
    'options': fields.List(fields.String, description='Multiple choice options'),
    'correct': fields.String(description='Correct answer')
})

quiz_model = api.model('Quiz', {
    'id': fields.Integer(readonly=True, description='Quiz identifier'),
    'quiz_type': fields.String(required=True, enum=['text', 'multiple_choice', 'true_false'], description='Type of quiz'),
    'question_text': fields.String(required=True, description='Quiz question'),
    'answer_text': fields.Raw(required=True, description='Quiz answer (string or JSON object for multiple choice)'),
    'theme_id': fields.Integer(description='Theme identifier'),
    'theme_name': fields.String(description='Theme name'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

# Request/Response models
register_request = api.model('RegisterRequest', {
    'name': fields.String(required=True, description='User name'),
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

login_request = api.model('LoginRequest', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

api_key_response = api.model('ApiKeyResponse', {
    'api_key': fields.String(description='API key')
})

create_quiz_request = api.model('CreateQuizRequest', {
    'quiz_type': fields.String(required=True, enum=['text', 'multiple_choice', 'true_false'], description='Type of quiz'),
    'question_text': fields.String(required=True, description='Quiz question'),
    'answer_text': fields.Raw(required=True, description='Quiz answer'),
    'theme_id': fields.Integer(description='Theme identifier')
})

# Example decorators for documentation
def auth_required(f):
    """Decorator to mark endpoints that require authentication"""
    f.__apidoc__ = {'security': 'apikey'}
    return f

# Example route documentation
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_request)
    @auth_ns.response(201, 'User registered successfully', api_key_response)
    @auth_ns.response(400, 'Validation Error')
    def post(self):
        """Register a new user"""
        pass

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_request)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(401, 'Authentication failed')
    def post(self):
        """Login user and start session"""
        pass

@quiz_ns.route('/')
class QuizList(Resource):
    @auth_required
    @quiz_ns.doc('list_quizzes')
    @quiz_ns.response(200, 'Success', [quiz_model])
    def get(self):
        """List all quizzes for the current user"""
        pass

    @auth_required
    @quiz_ns.doc('create_quiz')
    @quiz_ns.expect(create_quiz_request)
    @quiz_ns.response(201, 'Quiz created', quiz_model)
    def post(self):
        """Create a new quiz"""
        pass

@quiz_ns.route('/default')
class DefaultQuizList(Resource):
    @quiz_ns.doc('list_default_quizzes')
    @quiz_ns.response(200, 'Success', [quiz_model])
    def get(self):
        """List all default quizzes (created by admins)"""
        pass

@quiz_ns.route('/<int:id>')
class Quiz(Resource):
    @auth_required
    @quiz_ns.doc('get_quiz')
    @quiz_ns.response(200, 'Success', quiz_model)
    @quiz_ns.response(404, 'Quiz not found')
    def get(self, id):
        """Get a specific quiz"""
        pass

@theme_ns.route('/')
class ThemeList(Resource):
    @theme_ns.doc('list_themes')
    @theme_ns.response(200, 'Success', [theme_model])
    def get(self):
        """List all themes"""
        pass

@theme_ns.route('/<int:id>/quiz')
class ThemeQuizList(Resource):
    @auth_required
    @theme_ns.doc('list_theme_quizzes')
    @theme_ns.response(200, 'Success', [quiz_model])
    @theme_ns.response(404, 'Theme not found')
    def get(self, id):
        """List all quizzes for a theme"""
        pass

@user_ns.route('/api-key')
class ApiKey(Resource):
    @auth_required
    @user_ns.doc('get_api_key')
    @user_ns.response(200, 'Success', api_key_response)
    def get(self):
        """Get current user's API key"""
        pass

    @auth_required
    @user_ns.doc('refresh_api_key')
    @user_ns.response(200, 'Success', api_key_response)
    def post(self):
        """Refresh current user's API key"""
        pass 
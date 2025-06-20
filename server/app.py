from flask import Flask, session, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db, User, Recipe
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        try:
            user = User(
                username=data.get('username'),
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            if not data.get('password'):
                return make_response({'errors': ['Password is required']}, 422)
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return make_response(user.to_dict(only=('id', 'username', 'image_url', 'bio')), 201)
        except ValueError as e:
            return make_response({'errors': [str(e)]}, 422)
        except IntegrityError:
            db.session.rollback()
            return make_response({'errors': ['Username already exists']}, 422)

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            return make_response(user.to_dict(only=('id', 'username', 'image_url', 'bio')), 200)
        return make_response({'error': 'Unauthorized'}, 401)

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return make_response(user.to_dict(only=('id', 'username', 'image_url', 'bio')), 200)
        return make_response({'error': 'Unauthorized'}, 401)

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return make_response('', 204)
        return make_response({'error': 'Unauthorized'}, 401)

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
            return make_response(recipes, 200)
        return make_response({'error': 'Unauthorized'}, 401)

    def post(self):
        if session.get('user_id'):
            data = request.get_json()
            try:
                recipe = Recipe(
                    title=data['title'],
                    instructions=data['instructions'],
                    minutes_to_complete=data.get('minutes_to_complete'),
                    user_id=session['user_id']
                )
                db.session.add(recipe)
                db.session.commit()
                return make_response(recipe.to_dict(), 201)
            except ValueError as e:
                return make_response({'errors': [str(e)]}, 422)
        return make_response({'error': 'Unauthorized'}, 401)

api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
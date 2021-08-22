from flask import Blueprint, make_response, jsonify
from flask_restful import Api

from api.resources.user import UsersAPI, TokenAPI

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

api = Api(api_blueprint)

api.add_resource(UsersAPI, '/users', '/users/<int:user_id>', endpoint='users')
api.add_resource(TokenAPI, '/token', endpoint='token')



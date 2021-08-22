import re
from flask import g
from werkzeug import exceptions as http_exc
from flask_restful import Resource, reqparse, marshal_with, fields, abort

from models import auth
from models.user import Users


class FormatDateTime(fields.Raw):
    def format(self, value):
        return value.strftime('%Y年%m月%d日 %H時%M分%S秒')


output_fields = {
    'user_id': fields.String(attribute='id'),
    'username': fields.String,
    'password_hash': fields.String,
    'email': fields.String,
    'create_time': FormatDateTime,
    'url': fields.Url('api.users', absolute=True)
}


def validate_email(email):
    if re.search(r'^[^@ ]+@([^.@][^@]+)$', email, re.IGNORECASE):
        return email
    else:
        raise ValueError('邮件格式有误')


post_parser = reqparse.RequestParser(bundle_errors=True)
post_parser.add_argument('username', type=str, required=True, location='json')
post_parser.add_argument('password', type=Users.hash_password, required=True,
                         dest='password_hash', location='json')
post_parser.add_argument('email', type=validate_email, required=True, location='json')


class UsersAPI(Resource):
    method_decorators = {'get': [auth.login_required]}

    @marshal_with(output_fields)
    def get(self, user_id=None):
        if user_id and Users.query.filter(Users.id == user_id).first() is None:
            raise http_exc.Gone(f'无法找到 user_id {user_id} 指定用户')
        else:
            users = [Users.query.filter(Users.id == user_id).first()] \
                if user_id else list(Users.query.all())
            [setattr(user, 'user_id', user.id) for user in users]
            return users

    @marshal_with(output_fields)
    def post(self):
        args = post_parser.parse_args()
        username = args['username']
        if Users.query.filter(Users.username == username).first() is not None:
            raise http_exc.Conflict('用户名已经被使用')

        user = Users.create_user(username, args['password_hash'], args['email'])
        user.user_id = user.id

        return [user]

    # 这个接口仅作为测试用， 实际使用不该出现这种接口
    def delete(self):
        Users.delete_all_users()
        return {'msg': '删除完成'}


class TokenAPI(Resource):
    method_decorators = {'get': [auth.login_required]}

    def get(self):
        token = g.user.generate_auth_token(600)
        return {'token': token.decode('ascii'),
                'duration': 600}

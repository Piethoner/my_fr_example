from . import db, auth

import jwt
import time
from flask import g, current_app
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from werkzeug.security import generate_password_hash, check_password_hash


class Users(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, doc='用户ID')
    username = Column(String(32), index=True, unique=True, doc='用户名')
    password_hash = Column(String(128), doc='密码哈希')
    email = Column(String(32), doc='邮箱')
    create_time = Column(DateTime, default=datetime.now, index=True, doc='创建时间')

    @classmethod
    def hash_password(cls, password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires=600):
        return jwt.encode({'id': self.id, 'exp': time.time() + expires},
                          current_app.config['SECRET_KEY'],   # 这里需要使用 current_app
                          algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'],
                              algorithms=['HS256'])
            return Users.query.filter(Users.id == data['id']).first()
        except:
            return False


    @classmethod
    def create_user(cls, username, password_hash, email):
        user = cls(username=username, password_hash=password_hash, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def delete_all_users(cls):
        Users.query.delete()
        db.session.commit()


@auth.verify_password
def verify_password(username_or_token, password):
    user = Users.verify_auth_token(username_or_token)
    if not user:
        user = Users.query.filter(Users.username == username_or_token).first()
        if (not user) or (not user.verify_password(password)):
            return False

    g.user = user
    return True

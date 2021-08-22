import os
from flask import Flask

from config import Config
from models import db


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    db.app = app

    # 注册blueprint
    from api import api_blueprint
    app.register_blueprint(api_blueprint)

    return app


if __name__ == '__main__':
    app = create_app()
    if not os.path.exists(app.config['SQLALCHEMY_DATABASE_URI']):
        db.create_all()

    app.run(debug=True)





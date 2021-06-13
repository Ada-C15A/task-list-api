# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# import os
# from dotenv import load_dotenv


# db = SQLAlchemy()
# migrate = Migrate()
# load_dotenv()


# def create_app(test_config=None):
#     app = Flask(__name__)
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#     if test_config is None:
#         app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
#             "SQLALCHEMY_DATABASE_URI")
#     else:
#         app.config["TESTING"] = True
#         app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
#             "SQLALCHEMY_TEST_DATABASE_URI")

#     # Import models here for Alembic setup
#     from app.models.task import Task
#     from app.models.goal import Goal

#     db.init_app(app)
#     migrate.init_app(app, db)

#     # Register Blueprints here
#     from .routes import task_list_api_bp
#     app.register_blueprint(task_list_api_bp)

#     return app


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:postgres@localhost:5432/task_list_api_development'

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models.task import Task

    from .routes import task_list_api_bp
    app.register_blueprint(task_list_api_bp)

    return app

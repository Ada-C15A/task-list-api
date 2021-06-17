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
    from app.models.goal import Goal

    from .routes import task_list_api_bp
    app.register_blueprint(task_list_api_bp)

    from .routes import goals_bp
    app.register_blueprint(goals_bp)

    return app

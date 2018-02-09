from flask import Flask
from website.models import db

def create_app(config):
    """
    Flask application factory, Development, Test, Staging, and Production
    configs may engage / disengage different application features.
    """
    # Create unconfigured flask application
    # app = Flask(config.APP_NAME, template_folder='templates')
    app = Flask(config.APP_NAME)


    # Configure flask application
    app.config.from_object(config)
    app.static_folder = config.STATIC_FOLDER

    db.init_app(app)

    return app

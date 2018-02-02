from flask import Flask, Blueprint
from api.gyresources.endpoints.PlantController import ns as plant_namespace
from api.gyresources.endpoints.TextController import ns as text_namespace
from api.restplus import api


# import settings
app = Flask(__name__)


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = '127.0.0.1:8888'  # settings.SERVER_NAME
    flask_app.config['DBHOST'] = '127.0.0.1'  # settings.DBHOST
    flask_app.config['DBPORT'] = '5432'
    flask_app.config['DBUSER'] = 'capivara'
    flask_app.config['DBPASS'] = 'test'
    flask_app.config['DBNAME'] = 'green_eyes'
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
    flask_app.config['RESTPLUS_VALIDATE'] = True
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = False
    flask_app.config['RESTPLUS_ERROR_404_HELP'] = False


def initialize_app(flask_app):
    configure_app(flask_app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(plant_namespace)
    api.add_namespace(text_namespace)
    flask_app.register_blueprint(blueprint)
    return flask_app


def main():
    initialize_app(app)
    app.run(debug=True)


if __name__ == '__main__':
    main()

from flask import Flask, Blueprint
from api.gyresources.endpoints.PlantController import ns as plant_namespace
from api.gyresources.endpoints.TextController import ns as text_namespace
from api.gyresources.endpoints.TypeController import ns as type_namespace
from api.gyresources.endpoints.ImageController import ns as image_namespace
from api.gyresources.endpoints.UserController import ns as user_namespace
from api.gyresources.endpoints.DiseaseController import ns as disease_namespace
from api.gyresources.endpoints.LoggerController import ns as logger_namespace
from api.gyresources.endpoints.MessageController import ns as message_namespace
from api.gyresources.endpoints.token import ns as token_namespace
from api.gyresources.endpoints.AnalysisController import ns as analysis_namespace
from api.gyresources.endpoints.AnalysisResultController import ns as analysisResult_namespace
from api.restplus import api


# import settings
app = Flask(__name__)


def initialize_app(flask_app):
    flask_app.config.from_object('config.DefaultConfig')
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(plant_namespace)
    api.add_namespace(text_namespace)
    api.add_namespace(type_namespace)
    api.add_namespace(image_namespace)
    api.add_namespace(user_namespace)
    api.add_namespace(disease_namespace)
    api.add_namespace(logger_namespace)
    api.add_namespace(token_namespace)
    api.add_namespace(analysis_namespace)
    api.add_namespace(analysisResult_namespace)
    api.add_namespace(message_namespace)
    flask_app.register_blueprint(blueprint)
    return flask_app


def main():
    initialize_app(app)
    app.run(debug=False)


if __name__ == '__main__':
    main()

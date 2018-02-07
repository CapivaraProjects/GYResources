from api.gyresources.parsers import log_post_args
from api.gyresources.endpoints.BaseController import BaseController
from tools.Logger import Logger
from flask import Flask
from flask import request
from api.restplus import api


flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

ns = api.namespace('gyresources/logs',
                   description='Operations related to logs')

@ns.route('/')
class LoggerController(BaseController):
    """
    This class was created to manage all logs from the api
    """

    @api.expect(log_post_args)
    @api.response(200, 'Logger inicialized.')
    def post(self):
        """
        Method used to create the log from the action
        """
        try:
            Logger.create(url=flask_app.config["ELASTICURL"],
                          type=request.args.get('type'),
                          message=request.args.get('message'),
                          function=request.args.get('function'),
                          obs=request.args.get('message'),
                          config=request.args.get('message'))
            return self.okResponse(
                response='',
                message="OK",
                status=201), 200
        except Exception as err:
            return self.okResponse(
                response=err,
                message="Internal server error " + str(err),
                status=500)






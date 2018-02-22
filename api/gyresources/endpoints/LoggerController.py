from api.gyresources.parsers import log_post_args
from api.gyresources.endpoints.BaseController import BaseController
from collections import namedtuple
from tools.Logger import Logger
from flask import Flask
from flask import request
from api.restplus import api, FLASK_APP
import models.Logger


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
        log = request.json
        log = namedtuple("Log", log.keys())(*log.values())
        try:
            Logger.create(url=FLASK_APP.config["ELASTICURL"],
                          type=log.type,
                          message=log.message,
                          function=log.function,
                          obs=log.obs,
                          config=log.config)
            return self.okResponse(
                response=models.Logger.Logger(log.type, log.message, log.function, log.obs, log.config),
                message="OK",
                status=201), 200
        except Exception as err:
            return self.okResponse(
                response=err,
                message="Internal server error " + str(err),
                status=500)






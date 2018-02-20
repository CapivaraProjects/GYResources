import time
from flask_restplus import Resource
from flask import Flask
from flask import request
import models.BaseResponse as BaseResponse
import models.PagedResponse as PagedResponse
from tools import Logger

flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

class BaseController(Resource):
    """
    This class have the basic things used in controllers
    """

    defaultPageSize = 10
    startTime = 0

    def calculateElapsedTime(self, start):
        """
        (int) -> (int)
        Method used to calculate elapsed time by request
        """
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative.',
                             'Calculated elapsed time by request',
                             'calculateElapsedTime()',
                             'Empty',
                             flask_app.config["TYPE"])
        return time.time() - start

    def okResponse(self, response, message, status, total=0, pageSize=0,
                   offset=0):
        """
        (object, string, int, int, int, int) -> (dict)
        Method used to create a default response for request
        """
        resp = object()

        if (total == 0 and pageSize == 0 and offset == 0):
            resp = BaseResponse.BaseResponse(
                    status_code=status,
                    message=message,
                    elapsed_ms=self.calculateElapsedTime(self.startTime),
                    response=response.__dict__)
        else:
            hell = []
            for res in response:
                hell.append(res.__dict__)
            resp = PagedResponse.PagedResponse(
                    status_code=status,
                    message=message,
                    elapsed_ms=self.calculateElapsedTime(self.startTime),
                    response=hell,
                    total=total,
                    offset=offset,
                    page_size=pageSize)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative',
                             str(resp.__dict__),
                             'okResponse()',
                             message,
                             flask_app.config["TYPE"])
        return resp.__dict__  # json.dumps(resp, indent=4, cls=CustomEncoder)

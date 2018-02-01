import time
from flask_restplus import Resource
import models.BaseResponse as BaseResponse
import models.PagedResponse as PagedResponse


class BaseController(Resource):

    defaultPageSize = 10
    startTime = 0

    def calculateElapsedTime(self, start):
        return time.time() - start

    def okResponse(self, response, message, status, total=0, pageSize=0,
                   offset=0):
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
        return resp.__dict__  # json.dumps(resp, indent=4, cls=CustomEncoder)

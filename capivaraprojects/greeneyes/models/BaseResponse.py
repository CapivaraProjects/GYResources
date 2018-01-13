class BaseResponse:
    def __init__(self, status_code=0, message="", elapsed_ms="", response=""):
        self.status_code = status_code
        self.message = message
        self.elapsed_ms = elapsed_ms
        self.reponse = response

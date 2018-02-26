import time
from flask import g
from api.restplus import api, auth, generate_auth_token, FLASK_APP
from api.gyresources.endpoints.BaseController import BaseController
from tools import Logger


ns = api.namespace('gyresources/token',
                   description='Operations related to diseases')


class Token:
    def __init__(self, token, duration):
        self.token = token
        self.duration = duration


@ns.route('/')
class TokenController(BaseController):
    """
    Class used to generate token
    """

    @auth.login_required
    def post(self):
        """
        Method used to get auth token
        """
        self.startTime = time.time()
        print(FLASK_APP.config["EXPIRATION_TOKEN"])
        token = generate_auth_token(FLASK_APP.config["EXPIRATION_TOKEN"], g.user.id)
        Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                             'Informative',
                             'Token sucessfully created',
                             'post()',
                             token.decode('utf-8'),
                             FLASK_APP.config["TYPE"])
        return self.okResponse(
            response=Token(token.decode('utf-8'), FLASK_APP.config["EXPIRATION_TOKEN"]),
            message='Ok',
            status=200), 200

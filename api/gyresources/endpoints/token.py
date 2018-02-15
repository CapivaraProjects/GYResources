import time
from flask import Flask, g
from api.restplus import api, auth, generate_auth_token
from api.gyresources.endpoints.BaseController import BaseController

flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

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
        token = generate_auth_token(600, g.user.id)

        return self.okResponse(
                    response=Token(token.decode('utf-8'), 600),
                    message='Ok',
                    status=200), 200

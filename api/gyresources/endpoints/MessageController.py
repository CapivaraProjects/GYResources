from flask import Flask
from flask_mail import Mail,  Message
from flask import request
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import message as messageSerializer
from api.restplus import api, FLASK_APP
from tools import Logger
from collections import namedtuple


ns = api.namespace('gyresources/messages',
                   description='Operation to send emails')

@ns.route('/')
class MessageController(BaseController):
    """
    Email service class
    """
    @api.response(200, 'Message successfuly sent.')
    @api.expect(messageSerializer)
    def post(self):
        FLASK_APP.config['MAIL_SERVER']
        FLASK_APP.config['MAIL_PORT']
        FLASK_APP.config['MAIL_USE_TLS']
        FLASK_APP.config['MAIL_USE_SSL']
        FLASK_APP.config['MAIL_USERNAME']
        FLASK_APP.config['MAIL_PASSWORD']

        mail = Mail(FLASK_APP)
        mail.init_app(FLASK_APP)
        message = request.json
        message = namedtuple("Message", message.keys())(*message.values())
        userEmail = message.userEmail
        codeVerification = message.codeVerification
        try:
            msg = Message('Seu codigo de acesso ao App GreenEyes! (Nao responda esse e-mail)',
                sender = 'green.eyescorporate@gmail.com',
                recipients = [userEmail])
            msg.body = 'Seu codigo para cadastro no aplicativo: '+str(codeVerification)
            mail.send(msg)
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                'Informative',
                                'Message Successfuly sent.',
                                'post()',
                                str(userEmail+" - "+codeVerification),
                                FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=userEmail,
                message="Message Successfuly sent.",
                status=201), 200
        except Exception as err:
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Error',
                                 'Internal server Error',
                                 'post()',
                                 str(err),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error "+str(err),
                status=500)
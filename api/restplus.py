import models.User
from flask import Flask, request, g, jsonify
from flask_restplus import Api
from tools import Logger
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from repository.UserRepository import UserRepository
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


api = Api(version='1.0', title='GYResources-API',
          description='Services application used by Green Eyes applications')
flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')
flask_app.config['SECRET_KEY'] = 'my secret'
auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(auth, token_auth)


def generate_auth_token(expiration=600, id=0):
    s = Serializer(flask_app.config['SECRET_KEY'], expires_in=expiration)
    Logger.Logger.create(flask_app.config["ELASTICURL"],
                         'Informative',
                         'Ok',
                         'generate_auth_token()',
                         str(id),
                         flask_app.config["TYPE"])
    return s.dumps({'id': id})


def verify_auth_token(token):
    s = Serializer(flask_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        # valid token but expired
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Error',
                             'Valid token but expired',
                             'verify_auth_token()',
                             str(token),
                             flask_app.config["TYPE"])
        return None
    except BadSignature:
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Error',
                             'Invalid token',
                             'verify_auth_token()',
                             str(token),
                             flask_app.config["TYPE"])
        # invalid token
        return None

    repository = UserRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
    user = repository.searchByID(data['id'])
    Logger.Logger.create(flask_app.config["ELASTICURL"],
                         'Informative',
                         'User logged',
                         'verify_auth_token()',
                         str(user.__dict__),
                         flask_app.config["TYPE"])
    return user


@token_auth.verify_token
def verify_token(token):
    g.user = verify_auth_token(token)
    if g.user is not None:
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                         'Informative',
                         'Token verified',
                         'verify_token()',
                         str(g.user.__dict__),
                         flask_app.config["TYPE"])
    else:
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative',
                             'User not defined',
                             'verify_token()',
                             str(token),
                             flask_app.config["TYPE"])
    return (g.user is not None)


@auth.verify_password
def verify_password(usernameOrToken, password):
    repository = UserRepository(
            flask_app.config["DBUSER"],
            flask_app.config["DBPASS"],
            flask_app.config["DBHOST"],
            flask_app.config["DBPORT"],
            flask_app.config["DBNAME"])
    user = models.User.User(
            username=usernameOrToken,
            password=password,
            salt=request.json['salt'])
    try:
        user = repository.authentication(user)
        if (user.id):
            g.user = user
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Authenticated',
                                 'verify_password()',
                                 str(user.__dict__),
                                 flask_app.config["TYPE"])
            return True
    except Exception as err:
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Error',
                             'Failed to authenticate',
                             'verify_password()',
                             str(err),
                             flask_app.config["TYPE"])
        return False


@auth.error_handler
def unauthorized():
    response = jsonify({
        'status_code': 401,
        'error': 'unauthorized',
        'message': 'Please authenticate to access this API.'})
    Logger.Logger.create(flask_app.config["ELASTICURL"],
                         'Error',
                         'Unauthorized',
                         'unauthorized()',
                         str(response.__dict__),
                         flask_app.config["TYPE"])
    return response


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    Logger.Logger.create(flask_app.config["ELASTICURL"],
                         'Error',
                         'Internal server error',
                         'default_error_handler()',
                         message,
                         flask_app.config["TYPE"])
    return {'message': message}, 500

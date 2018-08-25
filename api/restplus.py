import models.User
from celery import Celery
from flask import Flask, request, g, jsonify
from flask_restplus import Api
from tools import Logger
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from repository.UserRepository import UserRepository
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


api = Api(version='1.0', title='GYResources-API',
          description='Services application used by Green Eyes applications')
FLASK_APP = Flask(__name__)
FLASK_APP.config.from_object('config.TestConfig')
auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(auth, token_auth)


def generate_auth_token(expiration=600, user_id=0):
    """(int, int) -> (token)
    Method used to generate auth token
    """
    serializer = Serializer(
        FLASK_APP.config['SECRET_KEY'],
        expires_in=expiration)
    Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                         'Informative',
                         'Ok',
                         'generate_auth_token()',
                         str(user_id),
                         FLASK_APP.config["TYPE"])
    return serializer.dumps({'id': user_id})


def make_celery(app):
    """Create celery instance
    Returns:
        A celery instance
    """
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


CELERY = make_celery(FLASK_APP)


def verify_auth_token(token):
    """(token) -> (User)
    Method used to verify auth token
    """
    serializer = Serializer(FLASK_APP.config['SECRET_KEY'])
    try:
        data = serializer.loads(token)
    except SignatureExpired:
        # valid token but expired
        Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                             'Error',
                             'Valid token but expired',
                             'verify_auth_token()',
                             str(token),
                             FLASK_APP.config["TYPE"])
        return None
    except BadSignature:
        Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                             'Error',
                             'Invalid token',
                             'verify_auth_token()',
                             str(token),
                             FLASK_APP.config["TYPE"])
        # invalid token
        return None

    repository = UserRepository(
        FLASK_APP.config["DBUSER"],
        FLASK_APP.config["DBPASS"],
        FLASK_APP.config["DBHOST"],
        FLASK_APP.config["DBPORT"],
        FLASK_APP.config["DBNAME"])
    user = repository.searchByID(data['id'])
    Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                         'Informative',
                         'User logged',
                         'verify_auth_token()',
                         str(user.__dict__),
                         FLASK_APP.config["TYPE"])
    return user


@token_auth.verify_token
def verify_token(token):
    """(token) -> (bool)
    Method used to verify token
    """
    g.user = verify_auth_token(token)
    if g.user is not None:
        Logger.Logger.create(
            FLASK_APP.config["ELASTICURL"],
            'Informative',
            'Token verified',
            'verify_token()',
            str(g.user.__dict__),
            FLASK_APP.config["TYPE"])
    else:
        Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                             'Informative',
                             'User not defined',
                             'verify_token()',
                             str(token),
                             FLASK_APP.config["TYPE"])
    return g.user is not None


@auth.verify_password
def verify_password(usernameOrToken, password):
    repository = UserRepository(
            FLASK_APP.config["DBUSER"],
            FLASK_APP.config["DBPASS"],
            FLASK_APP.config["DBHOST"],
            FLASK_APP.config["DBPORT"],
            FLASK_APP.config["DBNAME"])
    user = models.User.User(
            username=usernameOrToken,
            password=password)
    print(user.__dict__)
    try:
        user = repository.authentication(user)
        if (user.id):
            g.user = user
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'Authenticated',
                                 'verify_password()',
                                 str(user.__dict__),
                                 FLASK_APP.config["TYPE"])
            return True
    except Exception as err:
        Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                             'Error',
                             'Failed to authenticate',
                             'verify_password()',
                             str(err),
                             FLASK_APP.config["TYPE"])
        return False


@auth.error_handler
def unauthorized():
    response = jsonify({
        'status_code': 401,
        'error': 'unauthorized',
        'message': 'Please authenticate to access this API.'})
    Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                         'Error',
                         'Unauthorized',
                         'unauthorized()',
                         str(response.__dict__),
                         FLASK_APP.config["TYPE"])
    return response

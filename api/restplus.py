import models.User
from flask import Flask, request, g, jsonify
from flask_restplus import Api
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
    return s.dumps({'id': id})


def verify_auth_token(token):
    s = Serializer(flask_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        # valid token but expired
        return None
    except BadSignature:
        # invalid token
        return None

    repository = UserRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
    user = repository.searchByID(data['id'])
    return user


@token_auth.verify_token
def verify_token(token):
    print("Token: %s\n" % token)
    g.user = verify_auth_token(token)
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
    g.user = repository.authentication(user)
    if (g.user):
        return True
    return False


@auth.error_handler
def unauthorized():
    response = jsonify({
        'status': 401,
        'error': 'unauthorized',
        'message': 'Please authenticate to access this API.'})
    response.status_code = 401
    return response


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    return {'message': message}, 500

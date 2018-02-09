import models.User
from flask import Flask, request, g
from flask_restplus import Api
from flask_httpauth import HTTPBasicAuth
from repository.UserRepository import UserRepository
from tools.Cryptography import Crypto


api = Api(version='1.0', title='GYResources-API',
          description='Services application used by Green Eyes applications')
flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')
flask_app.config['SECRET_KEY'] = 'my secret'
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # if(not username or not password):
    #     username = request.args.get('username')
    #     password = request.args.get('password')
    print("Username: {}\nPassword: {}\nSalt: {}".format(username, password, request.json['salt']))
    repository = UserRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"]) 
    user = models.User.User(
                      username=username,
                      password=password,
                      salt=request.json['salt'])
    g.user = repository.authentication(user)
    if (g.user.id):
        return True 
    return False

@auth.error_handler
def unauthorized():
    response = jsonify({'status': 401, 'error': 'unauthorized', 'message': 'Please authenticate to access this API.'})
    response.status_code = 401
    return response

@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    return {'message': message}, 500

import time
import models.User
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api
from collections import namedtuple
from repository.UserRepository import UserRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import user as userSerializer
from api.gyresources.parsers import user_search_args

flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

ns = api.namespace('gyresources/users',
                   description='Operations related to users')


@ns.route('/')
class UserController(BaseController):
    """
    This class was created with the objective to control functions
        from UserRepository, here, you can insert, update and delete
        data. Searchs are realized in UserSearch.
    """

    @api.expect(user_search_args)
    @api.response(200, 'User searched.')
    def get(self):
        """
        Return a list of users based on action.

        If action=search:
            you can use idType, email, username, password, salt,
            dateInsertion, dateUpdate or description to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.User.User()
        total = 0
        action = request.args.get('action')
        id = request.args.get('id')
        user = models.User.User(
                      idType=request.args.get('idType'),
                      email=request.args.get('email'),
                      username=request.args.get('username'),
                      password=request.args.get('password'),
                      salt=request.args.get('salt'),
                      dateInsertion=request.args.get('dateInsertion'),
                      dateUpdate=request.args.get('dateUpdate'))
        pageSize = request.args.get('pageSize')
        offset = request.args.get('offset')
        repository = UserRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            if (action == 'search'):
                result = repository.search(user, pageSize, offset)
                total = result['total']
                result = result['content']
                return self.okResponse(
                            response=result,
                            message="Ok",
                            status=200,
                            total=total,
                            offset=offset,
                            pageSize=pageSize), 200
        except (exc.SQLAlchemyError, Exception) as sqlerr:
            # log
            return self.okResponse(
                response=sqlerr,
                message="SQL error: "+str(sqlerr),
                status=500)

    @api.response(200, 'User successfuly created.')
    @api.expect(userSerializer)
    def post(self):
        """
        Method used to insert user in database
        receives in body request a user model
        action should be anything
        """
        user = request.json

        user = namedtuple("User", user.keys())(*user.values())
        repository = UserRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            user = repository.create(user)
            return self.okResponse(
                response=user,
                message="User sucessfuly created.",
                status=201), 200
        except exc.SQLAlchemyError as sqlerr:
            # log
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            return self.okResponse(
                response=err,
                message="Internal server error "+str(err),
                status=500)

    @api.response(200, 'User changed successfuly')
    @api.expect(userSerializer)
    def put(self):
        """
        Method used to update user in database
        receives in body request a user model
        action should be anything
        """
        user = request.json

        user = namedtuple("User", user.keys())(*user.values())
        repository = UserRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            user = repository.update(user)
            return self.okResponse(
                response=user,
                message="User sucessfuly updated.",
                status=204), 200
        except exc.SQLAlchemyError as sqlerr:
            # log
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            return self.okResponse(
                response=err,
                message="Internal server error",
                status=500)
        return self.okResponse(
                response=user,
                message="User sucessfuly updated.",
                status=204), 200

    @api.response(200, 'User deleted successfuly')
    @api.expect(userSerializer)
    def delete(self):
        """
        Method used to delete user in database
        receives in body request a user model
        action should be anything
        """
        user = request.json

        user = namedtuple("User", user.keys())(*user.values())
        repository = UserRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            status = repository.delete(user)
            if (status):
                return self.okResponse(
                    response=models.User.User(),
                    message="User deleted sucessfuly.",
                    status=204), 200
            else:
                return self.okResponse(
                    response=user,
                    message="Problem deleting user",
                    status=500), 200
        except exc.SQLAlchemyError as sqlerr:
            # log
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            return self.okResponse(
                response=err,
                message="Internal server error: "+str(err),
                status=500)

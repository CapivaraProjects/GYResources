import time
import models.Type
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api, token_auth
from collections import namedtuple
from repository.TypeRepository import TypeRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import type as typeSerializer
from api.gyresources.parsers import type_search_args
from tools import Logger

flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

ns = api.namespace('gyresources/types',
                   description='Operations related to types')


@ns.route('/')
class TypeController(BaseController):
    """
    This class was created with the objective to control functions
        from TypeRepository, here, you can insert, update and delete
        data. Searchs are realized in TypeSearch.
    """

    @api.expect(type_search_args)
    @api.response(200, 'Type searched.')
    def get(self):
        """
        Return a list of types based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use value or description to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.Type.Type()
        total = 0
        action = request.args.get('action')
        id = request.args.get('id')
        type = models.Type.Type(
                      value=request.args.get('value'),
                      description=request.args.get('description'))
        pageSize = None
        if pageSize:
            pageSize = int(request.args.get('pageSize'))
        else:
            pageSize = 10

        offset = None
        if offset:
            offset = int(request.args.get('offset'))
        else:
            offset = 0
        repository = TypeRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(result.__dict__),
                                     'TEST')
                return self.okResponse(
                            response=result,
                            message="Ok",
                            status=200)
            elif (action == 'search'):
                result = repository.search(type, pageSize, offset)
                total = result['total']
                result = result['content']
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(result),
                                     'TEST')
                return self.okResponse(
                            response=result,
                            message="Ok",
                            status=200,
                            total=total,
                            offset=offset,
                            pageSize=pageSize), 200
        except (exc.SQLAlchemyError, Exception) as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'get()',
                                 str(sqlerr),
                                 'TEST')
            return self.okResponse(
                response=sqlerr,
                message="SQL error: "+str(sqlerr),
                status=500)


    @api.response(200, 'Type successfuly created.')
    @api.expect(typeSerializer)
    @token_auth.login_required
    def post(self):
        """
        Method used to insert type in database
        receives in body request a type model
        action should be anything
        """
        type = request.json

        type = namedtuple("Type", type.keys())(*type.values())
        type = models.Type.Type(
            id=None,
            value=type.value,
            description=type.description)

        repository = TypeRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            type = repository.create(type)
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Type sucessfuly created',
                                 'post()',
                                 str(type.__dict__),
                                 'TEST')
            return self.okResponse(
                response=type,
                message="Type sucessfuly created.",
                status=201), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'post()',
                                 str(sqlerr),
                                 'TEST')
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error',
                                 'post()',
                                 str(err),
                                 'TEST')
            return self.okResponse(
                response=err,
                message="Internal server error "+str(err),
                status=500)


    @api.response(200, 'Type changed successfuly')
    @api.expect(typeSerializer)
    @token_auth.login_required
    def put(self):
        """
        Method used to update type in database
        receives in body request a type model
        action should be anything
        """
        type = request.json

        type = namedtuple("Type", type.keys())(*type.values())
        repository = TypeRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            type = repository.update(type)
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Type sucessfuly updated',
                                 'post()',
                                 str(type.__dict__),
                                 'TEST')
            return self.okResponse(
                response=type,
                message="Type sucessfuly updated.",
                status=204), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'put()',
                                 str(sqlerr),
                                 'TEST')
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error',
                                 'put()',
                                 str(err),
                                 'TEST')
            return self.okResponse(
                response=err,
                message="Internal server error",
                status=500)

    @api.response(200, 'Type deleted successfuly')
    @api.expect(typeSerializer)
    @token_auth.login_required
    def delete(self):
        """
        Method used to delete type in database
        receives in body request a type model
        action should be anything
        """
        type = request.json

        type = namedtuple("Type", type.keys())(*type.values())
        repository = TypeRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            status = repository.delete(type)
            if (status):
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Type deleted sucessfuly',
                                     'post()',
                                     str(status),
                                     'TEST')
                return self.okResponse(
                    response=models.Type.Type(),
                    message="Type deleted sucessfuly.",
                    status=204), 200
            else:
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Error',
                                     'Problem deleting type',
                                     'post()',
                                     str(type.__dict__),
                                     'TEST')
                return self.okResponse(
                    response=type,
                    message="Problem deleting type",
                    status=500), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'delete()',
                                 str(sqlerr),
                                 'TEST')
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error',
                                 'delete()',
                                 str(err),
                                 'TEST')
            return self.okResponse(
                response=err,
                message="Internal server error: "+str(err),
                status=500)

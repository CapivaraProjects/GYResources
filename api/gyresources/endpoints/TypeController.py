import time
import models.Type
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api
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

        If action=search:
            you can use language, tag, value or description to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.Type.Type()
        total = 0
        message = 'empty var'
        action = request.args.get('action')
        id = request.args.get('id')
        type = models.Type.Type(
                      value=request.args.get('value'),
                      description=request.args.get('description'))
        pageSize = request.args.get('pageSize')
        offset = request.args.get('offset')
        repository = TypeRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            if (action == 'search'):
                result = repository.search(type, pageSize, offset)
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
        str(message.dict)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Get a Type',
                             message,
                             'get()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Type successfuly created.')
    @api.expect(typeSerializer)
    def post(self):
        """
        Method used to insert type in database
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
            type = repository.create(type)
            return self.okResponse(
                response=type,
                message="Type sucessfuly created.",
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
        str(message.dict)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Insert a Type',
                             message,
                             'post()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Type changed successfuly')
    @api.expect(typeSerializer)
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
            return self.okResponse(
                response=type,
                message="Type sucessfuly updated.",
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
                response=type,
                message="Type sucessfuly updated.",
                status=204), 200
        str(message.dict)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Update a Type',
                             message,
                             'put()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Type deleted successfuly')
    @api.expect(typeSerializer)
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
                return self.okResponse(
                    response=models.Type.Type(),
                    message="Type deleted sucessfuly.",
                    status=204), 200
            else:
                return self.okResponse(
                    response=type,
                    message="Problem deleting type",
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
        str(message.dict)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Delete a Type',
                             message,
                             'delete()',
                             'Empty',
                             'TEST')

import time
import models.Type
from sqlalchemy import exc
from flask import request
from api.restplus import api, token_auth, FLASK_APP
from collections import namedtuple
from repository.TypeRepository import TypeRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import type as typeSerializer
from api.gyresources.parsers import type_search_args
from tools import Logger


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
            please define page_size and offset parameters
        """
        self.startTime = time.time()
        result = models.Type.Type()
        total = 0
        action = request.args.get('action')
        id_type = request.args.get('id')
        type_model = models.Type.Type(
            value=request.args.get('value'),
            description=request.args.get('description'))
        page_size = None
        if request.args.get('pageSize'):
            page_size = int(request.args.get('pageSize'))
        else:
            page_size = 10

        offset = None
        if request.args.get('offset'):
            offset = int(request.args.get('offset'))
        else:
            offset = 0
        repository = TypeRepository(
            FLASK_APP.config["DBUSER"],
            FLASK_APP.config["DBPASS"],
            FLASK_APP.config["DBHOST"],
            FLASK_APP.config["DBPORT"],
            FLASK_APP.config["DBNAME"])
        try:
            if action == 'searchByID':
                result = repository.searchByID(id_type)
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(result.__dict__),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                    response=result,
                    message="Ok",
                    status=200)
            elif action == 'search':
                result = repository.search(type_model, page_size, offset)
                total = result['total']
                result = result['content']
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(result),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                    response=result,
                    message="Ok",
                    status=200,
                    total=total,
                    offset=offset,
                    pageSize=page_size), 200
        except (exc.SQLAlchemyError, Exception) as sqlerr:
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'get()',
                                 str(sqlerr),
                                 FLASK_APP.config["TYPE"])
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
        type_model = request.json

        type_model = namedtuple("Type", type_model.keys())(*type_model.values())
        type_model = models.Type.Type(
            id=None,
            value=type_model.value,
            description=type_model.description)

        repository = TypeRepository(
            FLASK_APP.config["DBUSER"],
            FLASK_APP.config["DBPASS"],
            FLASK_APP.config["DBHOST"],
            FLASK_APP.config["DBPORT"],
            FLASK_APP.config["DBNAME"])

        try:
            if not type_model.value:
                raise Exception('value field from type model not defined')
            type_model = repository.create(type_model)
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'Type sucessfuly created',
                                 'post()',
                                 str(type.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=type_model,
                message="Type sucessfuly created.",
                status=201), 200
        except Exception as err:
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error',
                                 'post()',
                                 str(err),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error: "+str(err),
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
        type_model = request.json

        type_model = namedtuple("Type", type_model.keys())(*type_model.values())
        repository = TypeRepository(
            FLASK_APP.config["DBUSER"],
            FLASK_APP.config["DBPASS"],
            FLASK_APP.config["DBHOST"],
            FLASK_APP.config["DBPORT"],
            FLASK_APP.config["DBNAME"])
        try:
            type_model = repository.update(type_model)
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'Type sucessfuly updated',
                                 'put()',
                                 str(type.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=type_model,
                message="Type sucessfuly updated.",
                status=204), 200
        except Exception as err:
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error',
                                 'put()',
                                 str(err),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error: " + str(err),
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
        type_model = request.json

        type_model = namedtuple("Type", type_model.keys())(*type_model.values())
        repository = TypeRepository(
            FLASK_APP.config["DBUSER"],
            FLASK_APP.config["DBPASS"],
            FLASK_APP.config["DBHOST"],
            FLASK_APP.config["DBPORT"],
            FLASK_APP.config["DBNAME"])

        try:
            status = repository.delete(type_model)
            if status:
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'Type deleted sucessfuly',
                                     'delete()',
                                     str(status),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                    response=models.Type.Type(),
                    message="Type deleted sucessfuly.",
                    status=204), 200
        except Exception as err:
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error',
                                 'delete()',
                                 str(err),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error: "+str(err),
                status=500)

import time
import models.Text
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api, token_auth
from collections import namedtuple
from repository.TextRepository import TextRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import text as textSerializer
from api.gyresources.parsers import text_search_args
from tools import Logger

flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

ns = api.namespace('gyresources/texts',
                   description='Operations related to texts')


@ns.route('/')
class TextController(BaseController):
    """
    This class was created with the objective to control functions
        from TextRepository, here, you can insert, update and delete
        data. Searchs are realized in TextSearch.
    """

    @api.expect(text_search_args)
    @api.response(200, 'Text searched.')
    def get(self):
        """
        Return a list of texts based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use language, tag, value or description to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.Text.Text()
        total = 0
        action = request.args.get('action')
        id = request.args.get('id')
        text = models.Text.Text(
                      language=request.args.get('language'),
                      tag=request.args.get('tag'),
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
        repository = TextRepository(
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
                                     flask_app.config["TYPE"])
                return self.okResponse(
                            response=result,
                            message="Ok",
                            status=200)
            elif (action == 'search'):
                result = repository.search(text, pageSize, offset)
                total = result['total']
                result = result['content']
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(result),
                                     flask_app.config["TYPE"])
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
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=sqlerr,
                message="SQL error: "+str(sqlerr),
                status=500)

    @api.response(200, 'Text successfuly created.')
    @api.expect(textSerializer)
    @token_auth.login_required
    def post(self):
        """
        Method used to insert text in database
        receives in body request a text model
        action should be anything
        """
        text = request.json

        text = namedtuple("Text", text.keys())(*text.values())
        text = models.Text.Text(
            id=None,
            language=text.language,
            tag=text.tag,
            value=text.value,
            description=text.description)

        repository = TextRepository(
            flask_app.config["DBUSER"],
            flask_app.config["DBPASS"],
            flask_app.config["DBHOST"],
            flask_app.config["DBPORT"],
            flask_app.config["DBNAME"])

        try:
            text = repository.create(text)
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Text sucessfuly created',
                                 'post()',
                                 str(text.__dict__),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=text,
                message="Text sucessfuly created.",
                status=201), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'post()',
                                 str(sqlerr),
                                 flask_app.config["TYPE"])
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server Error',
                                 'post()',
                                 str(err),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error "+str(err),
                status=500)

    @api.response(200, 'Text changed successfuly')
    @api.expect(textSerializer)
    @token_auth.login_required
    def put(self):
        """
        Method used to update text in database
        receives in body request a text model
        action should be anything
        """
        text = request.json

        text = namedtuple("Text", text.keys())(*text.values())
        repository = TextRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            text = repository.update(text)
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Text sucessfuly updated',
                                 'put()',
                                 str(text.__dict__),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=text,
                message="Text sucessfuly updated.",
                status=204), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'put()',
                                 str(sqlerr),
                                 flask_app.config["TYPE"])
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server Error',
                                 'put()',
                                 str(err),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error",
                status=500)


    @api.response(200, 'Text deleted successfuly')
    @api.expect(textSerializer)
    @token_auth.login_required
    def delete(self):
        """
        Method used to delete text in database
        receives in body request a text model
        action should be anything
        """
        text = request.json

        text = namedtuple("Text", text.keys())(*text.values())
        repository = TextRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            status = repository.delete(text)
            if (status):
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Text deleted sucessfuly',
                                     'delete()',
                                     'Empty',
                                     flask_app.config["TYPE"])
                return self.okResponse(
                    response=models.Text.Text(),
                    message="Text deleted sucessfuly.",
                    status=204), 200
            else:
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Problem deleting text',
                                     'delete()',
                                     str(text.__dict__),
                                     flask_app.config["TYPE"])
                return self.okResponse(
                    response=text,
                    message="Problem deleting text",
                    status=500), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'delete()',
                                 str(sqlerr),
                                 flask_app.config["TYPE"])
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server Error',
                                 'delete()',
                                 str(err),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error: "+str(err),
                status=500)

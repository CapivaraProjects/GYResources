import time
import models.Text
from sqlalchemy import exc
from flask import request
from api.restplus import api
from collections import namedtuple
from repository.TextRepository import TextRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import text as textSerializer
from api.gyresources.parsers import text_search_args


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
        pageSize = request.args.get('pageSize')
        offset = request.args.get('offset')
        repository = TextRepository(
                'capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')
        try:
            if (action == 'search'):
                result = repository.search(text, pageSize, offset)
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

    @api.response(200, 'Text successfuly created.')
    @api.expect(textSerializer)
    def post(self):
        """
        Method used to insert text in database
        receives in body request a text model
        action should be anything
        """
        text = request.json

        text = namedtuple("Text", text.keys())(*text.values())
        repository = TextRepository(
                'capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')

        try:
            text = repository.create(text)
            return self.okResponse(
                response=text,
                message="Text sucessfuly created.",
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

    @api.response(200, 'Text changed successfuly')
    @api.expect(textSerializer)
    def put(self):
        """
        Method used to update text in database
        receives in body request a text model
        action should be anything
        """
        text = request.json

        text = namedtuple("Text", text.keys())(*text.values())
        repository = TextRepository(
                'capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')
        try:
            text = repository.update(text)
            return self.okResponse(
                response=text,
                message="Text sucessfuly updated.",
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
                response=text,
                message="Text sucessfuly updated.",
                status=204), 200

    @api.response(200, 'Text deleted successfuly')
    @api.expect(textSerializer)
    def delete(self):
        """
        Method used to delete text in database
        receives in body request a text model
        action should be anything
        """
        text = request.json

        text = namedtuple("Text", text.keys())(*text.values())
        repository = TextRepository(
                'capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')

        try:
            status = repository.delete(text)
            if (status):
                return self.okResponse(
                    response=models.Text.Text(),
                    message="Text deleted sucessfuly.",
                    status=204), 200
            else:
                return self.okResponse(
                    response=text,
                    message="Problem deleting text",
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
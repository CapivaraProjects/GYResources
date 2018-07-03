import time
import models.AnalysisResult
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api, token_auth, FLASK_APP
from collections import namedtuple
from repository.AnalysisResultRepository import AnalysisResultRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import analysisResult as analysisResultSerializer
from api.gyresources.parsers import analysisResult_search_args
from tools import Logger


ns = api.namespace('gyresources/analysisResult',
                   description='Operations related to analysisResult')


@ns.route('/')
class AnalysisResultController(BaseController):
    """
    This class was created with the objective to control functions
        from AnalysisResultRepository, here, you can insert, update and delete
        data. Searchs are realized in AnalysisResultSearch.
    """

    @api.expect(analysisResult_search_args)
    @api.response(200, 'AnalysisResult searched.')
    def get(self):
        """
        Return a list of analyzes based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use idAnalysis|idDisease|score to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.AnalysisResult.AnalysisResult()
        total = 0
        action = request.args.get('action')
        id = request.args.get('id')
        analysisResult = models.AnalysisResult.AnalysisResult(
                        idAnalysis=request.args.get('idAnalysis'),
                        idDisease=request.args.get('idDisease'),
                        score=request.args.get('score'))
        pageSize = None
        if request.args.get('pageSize'):
            pageSize = int(request.args.get('pageSize'))
        else:
            pageSize = 10

        offset = None
        if request.args.get('offset'):
            offset = int(request.args.get('offset'))
        else:
            offset = 0
        repository = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative.',
                                     'Ok',
                                     'get()',
                                     str(result.__dict__),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                            response=result,
                            message="Ok",
                            status=200)
            elif (action == 'search'):
                result = repository.search(analysisResult, pageSize, offset)
                total = result['total']
                response = []
                for content in result['content']:
                    response.append(content)
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(response),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                            response=response,
                            message="Ok",
                            status=200,
                            total=total,
                            offset=offset,
                            pageSize=pageSize), 200
        except (exc.SQLAlchemyError, Exception) as sqlerr:
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Error',
                                 'SQL error',
                                 'get()',
                                 str(sqlerr),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=sqlerr,
                message="SQL error: "+str(sqlerr),
                status=500)


    @api.response(200,'AnalysisResult successfuly created.')
    @api.expect(analysisResultSerializer)
    @token_auth.login_required
    def post(self):
        """
        Method used to insert analysisResult in database
        receives in body request a analysisResult model
        action should be anything
        """
        analysisResult = request.json
        analysisResult = namedtuple("AnalysisResult", analysisResult.keys())(*analysisResult.values())                  
        analysisResult = models.AnalysisResult.AnalysisResult(
                                id=None,
                                idAnalysis=analysisResult.idAnalysis,
                                idDisease=analysisResult.idDisease,
                                score=analysisResult.score)
        repository = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            if (not analysisResult.idAnalysis or not analysisResult.idDisease):
                 # or not analysisResult.score pega o caso de score=0.0
                raise Exception('AnalysisResult fields not defined')
            analysisResult = repository.create(analysisResult)
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'AnalysisResult sucessfuly created',
                                 'post()',
                                 str(analysisResult.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=analysisResult,
                message="AnalysisResult sucessfuly created.",
                status=201), 200
        except Exception as err:
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error ',
                                 'post()',
                                 str(err),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error "+str(err),
                status=500)


    @api.response(200, 'AnalysisResult changed successfuly')
    @api.expect(analysisResultSerializer)
    @token_auth.login_required
    def put(self):
        """
        Method used to update analysisResult in database
        receives in body request a analysisResult model
        action should be anything
        """
        analysisResult = request.json

        analysisResult = namedtuple("AnalysisResult", analysisResult.keys())(*analysisResult.values())
        analysisResult = models.AnalysisResult.AnalysisResult(
                      id=analysisResult.id,
                      idAnalysis=analysisResult.idAnalysis,
                      idDisease=analysisResult.idDisease,
                      score=analysisResult.score)
        repository = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            analysisResult = repository.update(analysisResult)
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'AnalysisResult sucessfuly updated',
                                 'put()',
                                 str(analysisResult.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=analysisResult,
                message="AnalysisResult sucessfuly updated.",
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


    @api.response(200, 'AnalysisResult deleted successfuly')
    @api.expect(analysisResultSerializer)
    @token_auth.login_required
    def delete(self):
        """
        Method used to delete analysisResult from database
        receives in body request a analysisResult model
        action should be anything
        """
        analysisResult = request.json

        analysisResult = namedtuple("AnalysisResult", analysisResult.keys())(*analysisResult.values())
        repository = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            status = repository.delete(analysisResult)
            if (status):
                resp = models.AnalysisResult.AnalysisResult()
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'AnalysisResult deleted sucessfuly',
                                     'delete()',
                                     str(resp),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                    response=resp,
                    message="AnalysisResult deleted sucessfuly.",
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

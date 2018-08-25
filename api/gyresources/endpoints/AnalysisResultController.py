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
        Return a list of analysis based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use idAnalysis|idDisease|score|frame to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.AnalysisResult.AnalysisResult()
        total = 0
        action = request.args.get('action')
        id = request.args.get('id')
        analysisResult = models.AnalysisResult.AnalysisResult(
                        analysis=models.Analysis.Analysis(
                                        id=request.args.get('idAnalysis')),
                        disease=models.Disease.Disease(
                                        id=request.args.get('idDisease')),
                        score=request.args.get('score'),
                        frame=request.args.get('frame'))
        pageSize = 10
        if request.args.get('pageSize'):
            pageSize = int(request.args.get('pageSize'))

        offset = 0
        if request.args.get('offset'):
            offset = int(request.args.get('offset'))

        repository = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)

                result.disease.plant = result.disease.plant.__dict__
                result.disease = result.disease.__dict__
                result.analysis.image.disease.plant = result.analysis.image.disease.plant.__dict__
                result.analysis.image.disease = result.analysis.image.disease.__dict__
                result.analysis.image = result.analysis.image.__dict__
                result.analysis.classifier.plant = result.analysis.classifier.plant.__dict__
                result.analysis.classifier = result.analysis.classifier.__dict__
                result.analysis = result.analysis.__dict__

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
                    content.disease.plant = content.disease.plant.__dict__
                    content.disease = content.disease.__dict__
                    content.analysis.image.disease.plant = content.analysis.image.disease.plant.__dict__
                    content.analysis.image.disease = content.analysis.image.disease.__dict__
                    content.analysis.image = content.analysis.image.__dict__
                    content.analysis.classifier.plant = content.analysis.classifier.plant.__dict__
                    content.analysis.classifier = content.analysis.classifier.__dict__
                    content.analysis = content.analysis.__dict__
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
        analysisResult_request = request.json
        analysisResult_request = namedtuple("AnalysisResult", analysisResult_request.keys())(*analysisResult_request.values())
        analysisResult = models.AnalysisResult.AnalysisResult(
                                id=None,
                                analysis=models.Analysis.Analysis(
                                                id=analysisResult_request.idAnalysis),
                                disease=models.Disease.Disease(
                                                id=analysisResult_request.idDisease),
                                score=analysisResult_request.score,
                                frame=analysisResult_request.frame)
        repository = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            if (not analysisResult.analysis.id or not analysisResult.disease.id):
                raise Exception('AnalysisResult fields not defined')
            result = repository.create(analysisResult)
            result.disease.plant = result.disease.plant.__dict__
            result.disease = result.disease.__dict__
            result.analysis.image.disease.plant = result.analysis.image.disease.plant.__dict__
            result.analysis.image.disease = result.analysis.image.disease.__dict__
            result.analysis.image = result.analysis.image.__dict__
            result.analysis.classifier.plant = result.analysis.classifier.plant.__dict__
            result.analysis.classifier = result.analysis.classifier.__dict__
            result.analysis = result.analysis.__dict__

            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'AnalysisResult sucessfuly created',
                                 'post()',
                                 str(result.__dict__),
                                 FLASK_APP.config["TYPE"])

            return self.okResponse(
                response=result,
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
        analysisResult_request = request.json
        analysisResult_request = namedtuple("AnalysisResult", analysisResult_request.keys())(*analysisResult_request.values())
        analysisResult = models.AnalysisResult.AnalysisResult(
                                id=analysisResult_request.id,
                                analysis=models.Analysis.Analysis(
                                                id=analysisResult_request.idAnalysis),
                                disease=models.Disease.Disease(
                                                id=analysisResult_request.idDisease),
                                score=analysisResult_request.score,
                                frame=analysisResult_request.frame)
        repository = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            result = repository.update(analysisResult)
            result.disease.plant = result.disease.plant.__dict__
            result.disease = result.disease.__dict__
            result.analysis.image.disease.plant = result.analysis.image.disease.plant.__dict__
            result.analysis.image.disease = result.analysis.image.disease.__dict__
            result.analysis.image = result.analysis.image.__dict__
            result.analysis.classifier.plant = result.analysis.classifier.plant.__dict__
            result.analysis.classifier = result.analysis.classifier.__dict__
            result.analysis = result.analysis.__dict__

            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'AnalysisResult sucessfuly updated',
                                 'put()',
                                 str(result.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=result,
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
        analysisResult_request = request.json
        analysisResult_request = namedtuple("AnalysisResult", analysisResult_request.keys())(*analysisResult_request.values())
        analysisResult = models.AnalysisResult.AnalysisResult(
                                id=analysisResult_request.id,
                                analysis=models.Analysis.Analysis(
                                                id=analysisResult_request.idAnalysis),
                                disease=models.Disease.Disease(
                                                id=analysisResult_request.idDisease),
                                score=analysisResult_request.score,
                                frame=analysisResult_request.frame)
        repository = AnalysisResultRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            status = repository.delete(analysisResult)
            if (status):

                result = models.AnalysisResult.AnalysisResult()
                result.disease.plant = result.disease.plant.__dict__
                result.disease = result.disease.__dict__
                result.analysis.image.disease.plant = result.analysis.image.disease.plant.__dict__
                result.analysis.image.disease = result.analysis.image.disease.__dict__
                result.analysis.image = result.analysis.image.__dict__
                result.analysis.classifier.plant = result.analysis.classifier.plant.__dict__
                result.analysis.classifier = result.analysis.classifier.__dict__
                result.analysis = result.analysis.__dict__

                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'AnalysisResult deleted sucessfuly',
                                     'delete()',
                                     str(result),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                    response=result,
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

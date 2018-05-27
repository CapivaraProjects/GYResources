import time
import models.Analysis
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api, token_auth, FLASK_APP
from collections import namedtuple
from repository.AnalysisRepository import AnalysisRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import analysis as analysisSerializer
from api.gyresources.parsers import analysis_search_args
from tools import Logger


ns = api.namespace('gyresources/analysis',
                   description='Operations related to analysis')


@ns.route('/')
class AnalysisController(BaseController):
    """
    This class was created with the objective to control functions
        from AnalysisRepository, here, you can insert, update and delete
        data. Searchs are realized in AnalysisSearch.
    """

    @api.expect(analysis_search_args)
    @api.response(200, 'Analysis searched.')
    def get(self):
        """
        Return a list of analyses based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use idImage to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()

        total = 0
        result = models.Analysis.Analysis()
        action = request.args.get('action')
        id = request.args.get('id')

        analysis = models.Analysis.Analysis(
                            image=models.Image.Image(
                                    id=request.args.get('idImage')),
                            classifier=models.Classifier.Classifier(
                                        id=request.args.get('idClassifier')))

        pageSize = 10
        if request.args.get('pageSize'):
            pageSize = int(request.args.get('pageSize'))

        offset = 0
        if request.args.get('offset'):
            offset = int(request.args.get('offset'))

        repository = AnalysisRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)
                result.image.disease.plant = result.image.disease.plant.__dict__
                result.image.disease = result.image.disease.__dict__
                result.image = result.image.__dict__
                result.classifier.plant = result.classifier.plant.__dict__
                result.classifier = result.classifier.__dict__
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
            elif (action == 'search'):
                result = repository.search(analysis, pageSize, offset)# retorna um dicionario2
                total = result['total']
                response = []
                for content in result['content']:
                    content.image.disease.plant = content.image.disease.plant.__dict__
                    content.image.disease = content.image.disease.__dict__
                    content.image = content.image.__dict__
                    content.classifier.plant = content.classifier.plant.__dict__
                    content.classifier = content.classifier.__dict__
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


    @api.response(200,'Analysis successfuly created.')
    @api.expect(analysisSerializer)
    @token_auth.login_required
    def post(self):
        """
        Method used to insert analysis in database
        receives in body request a analysis model
        action should be anything
        """
        analysis_request = request.json
        analysis_request = namedtuple("Analysis", analysis_request.keys())(*analysis_request.values())
        analysis = models.Analysis.Analysis(
                      id=None,
                      image=models.Image.Image(id=analysis_request.idImage),
                      classifier=models.Classifier.Classifier(id=analysis_request.idClassifier))

        repository = AnalysisRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            if not analysis.image.id or not analysis.classifier.id :
                raise Exception('Analysis fields not defined')
            analysis = repository.create(analysis)
            analysis.image.disease.plant = analysis.image.disease.plant.__dict__
            analysis.image.disease = analysis.image.disease.__dict__
            analysis.image = analysis.image.__dict__
            analysis.classifier.plant = analysis.classifier.plant.__dict__
            analysis.classifier = analysis.classifier.__dict__

            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'Analysis sucessfuly created',
                                 'post()',
                                 str(analysis.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=analysis,
                message="Analysis sucessfuly created.",
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


    @api.response(200, 'Analysis changed successfuly')
    @api.expect(analysisSerializer)
    @token_auth.login_required
    def put(self):
        """
        Method used to update analysis in database
        receives in body request a analysis model
        action should be anything
        """
        analysis_request = request.json

        analysis = models.Analysis.Analysis(
                              id=analysis_request['id'],
                      image=models.Image.Image(
                                      id=analysis_request['idImage']),
                      classifier=models.Classifier.Classifier(
                                            id=analysis_request['idClassifier']))
        repository = AnalysisRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            analysis = repository.update(analysis)
            analysis.image.disease.plant = analysis.image.disease.plant.__dict__
            analysis.image.disease = analysis.image.disease.__dict__
            analysis.image = analysis.image.__dict__
            analysis.classifier.plant = analysis.classifier.plant.__dict__
            analysis.classifier = analysis.classifier.__dict__
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'Analysis sucessfuly updated',
                                 'put()',
                                 str(analysis.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=analysis,
                message="Analysis sucessfuly updated.",
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


    @api.response(200, 'Analysis deleted successfuly')
    @api.expect(analysisSerializer)
    @token_auth.login_required
    def delete(self):
        """
        Method used to delete analysis from database
        receives in body request a analysis model
        action should be anything
        """
        analysis_request = request.json
        analysis = models.Analysis.Analysis(
                              id=analysis_request['id'],
                      image=models.Image.Image(
                                      id=analysis_request['idImage']),
                      classifier=models.Classifier.Classifier(
                                            id=analysis_request['idClassifier']))
        repository = AnalysisRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            status = repository.delete(analysis)
            if (status):
                analysis = models.Analysis.Analysis()
                analysis.image.disease.plant = analysis.image.disease.plant.__dict__
                analysis.image.disease = analysis.image.disease.__dict__
                analysis.image = analysis.image.__dict__
                analysis.classifier.plant = analysis.classifier.plant.__dict__
                analysis.classifier = analysis.classifier.__dict__
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'Analysis deleted sucessfuly',
                                     'delete()',
                                     str(analysis),
                                     FLASK_APP.config["TYPE"])
                print("AnalysisController | {}".format(analysis.__dict__))
                return self.okResponse(
                    response=analysis,
                    message="Analysis deleted sucessfuly.",
                    status=204), 200
        except Exception as err:
            print("AnalysisController | {}".format(err))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
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

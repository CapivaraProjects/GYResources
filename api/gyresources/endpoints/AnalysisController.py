import time
import logging
import models.Analysis
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api, token_auth, FLASK_APP
from collections import namedtuple
from repository.AnalysisRepository import AnalysisRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.logic.tf_serving_client import make_prediction
from api.gyresources.logic.analysisResultParallelThread import ThreadWithReturnValue
from api.gyresources.serializers import analysis as analysisSerializer
from api.gyresources.parsers import analysis_search_args
from tools import Logger

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

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
        Return a list of analyzes based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use idImage to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.Analysis.Analysis()
        total = 0
        action = request.args.get('action')
        id = request.args.get('id')
        analysis = models.Analysis.Analysis(idImage=request.args.get('idImage'))
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
        repository = AnalysisRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)
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
                result = repository.search(analysis, pageSize, offset)
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


    @api.response(200,'Analysis successfuly created.')
    @api.expect(analysisSerializer)
    @token_auth.login_required
    def post(self):
        """
        Method used to insert analysis in database
        receives in body request a analysis model
        action should be anything
        """
        analysis = request.json
        analysis = namedtuple("Analysis", analysis.keys())(*analysis.values())
        analysis = models.Analysis.Analysis(
                      id=None,
                      idImage=analysis.idImage)
        repository = AnalysisRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            if not analysis.idImage:
                raise Exception('Analysis fields not defined')

            analysis = repository.create(analysis)
            analysis.image.disease.plant = analysis.image.disease.plant.__dict__
            analysis.image.disease = analysis.image.disease.__dict__
            analysis.image = analysis.image.__dict__
            analysis.classifier.plant = analysis.classifier.plant.__dict__
            analysis.classifier = analysis.classifier.__dict__
            analysisDict = analysis.__dict__

            try:
                daemon_thread = ThreadWithReturnValue(name='make_prediction',
                                     target=make_prediction,
                                     daemon=True,
                                     args=(analysisDict,
                                           FLASK_APP.config["TFSHOST"],
                                           FLASK_APP.config["TFSPORT"]))
                logging.info("Iniciando threading")
                daemon_thread.start()
            except Exception as exc:
                logging.info("Erro ao tentar make_prediction")
                logging.info("{}".format(str(exc)))
                pass

            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'Analysis sucessfuly created',
                                 'post()',
                                 str(analysisDict),
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
        analysis = request.json

        analysis = namedtuple("Analysis", analysis.keys())(*analysis.values())
        analysis = models.Analysis.Analysis(
                      id=analysis.id,
                      idImage=analysis.idImage)
        repository = AnalysisRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            analysis = repository.update(analysis)
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
        analysis = request.json

        analysis = namedtuple("Analysis", analysis.keys())(*analysis.values())
        repository = AnalysisRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            status = repository.delete(analysis)
            if (status):
                resp = models.Analysis.Analysis()
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'Analysis deleted sucessfuly',
                                     'delete()',
                                     str(resp),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                    response=resp,
                    message="Analysis deleted sucessfuly.",
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

import time
import models.Classifier
import models.Plant
from sqlalchemy import exc
from flask import request
from api.restplus import api, token_auth, FLASK_APP
from collections import namedtuple
from repository.ClassifierRepository import ClassifierRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import classifier as classifierSerializer
from api.gyresources.parsers import classifier_search_args
from tools import Logger


ns = api.namespace('gyresources/classifiers',
                   description='Operations related to classifiers')


@ns.route('/')
class ClassifierController(BaseController):
    """
    This class was created with the objective to control functions
        from ClassifierRepository, here, you can insert, update and delete
        data. Searchs are realized in ClassifierSearch.
    """

    @api.expect(classifier_search_args)
    @api.response(200, 'Classifier searched.')
    def get(self):
        """
        Return a list of classifiers based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use tag or path to search,
            please define pageSize and offset parameters
        """

        self.startTime = time.time()
        result = models.Classifier.Classifier()
        total = 0
        action = request.args.get('action')
        id = request.args.get('id')
        classifier = models.Classifier.Classifier(
                      plant=models.Plant.Plant(id=request.args.get('idPlant')),
                      tag=request.args.get('tag'),
                      path=request.args.get('path'))

        pageSize = 10
        if request.args.get('pageSize'):
            pageSize = int(request.args.get('pageSize'))

        offset = 0
        if request.args.get('offset'):
            offset = int(request.args.get('offset'))

        repository = ClassifierRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)
                result.plant = result.plant.__dict__
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
                result = repository.search(classifier, pageSize, offset)
                total = result['total']
                response = []
                for content in result['content']:
                    content.plant = content.plant.__dict__
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


    @api.response(200, 'Classifier successfuly created.')
    @api.expect(classifierSerializer)
    @token_auth.login_required
    def post(self):
        """
        Method used to insert classifier in database
        receives in body request a classifier model
        action should be anything
        """
        classifier = request.json

        classifier = namedtuple("Classifier", classifier.keys())(*classifier.values())
        classifier = models.Classifier.Classifier(
                      id=None,
                      tag=classifier.tag,
                      path=classifier.path,
                      plant=models.Plant.Plant(id=classifier.idPlant))
        repository = ClassifierRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            if (not classifier.tag or not classifier.path):
                raise Exception('Not defined tag or path field')
            classifier = repository.create(classifier)
            classifier.plant = classifier.plant.__dict__
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'Classifier sucessfuly created',
                                 'post()',
                                 str(classifier.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=classifier,
                message="Classifier sucessfuly created.",
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


    @api.response(200, 'Classifier changed successfuly')
    @api.expect(classifierSerializer)
    @token_auth.login_required
    def put(self):
        """
        Method used to update classifier in database
        receives in body request a classifier model
        action should be anything
        """
        classifier = request.json

        classifier = namedtuple("Classifier", classifier.keys())(*classifier.values())
        classifier = models.Classifier.Classifier(
                      id=classifier.id,
                      tag=classifier.tag,
                      path=classifier.path,
                      plant=models.Plant.Plant(id=classifier.idPlant))
        repository = ClassifierRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])
        try:
            classifier = repository.update(classifier)
            classifier.plant = classifier.plant.__dict__
            Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                 'Informative',
                                 'Classifier sucessfuly updated',
                                 'put()',
                                 str(classifier.__dict__),
                                 FLASK_APP.config["TYPE"])
            return self.okResponse(
                response=classifier,
                message="Classifier sucessfuly updated.",
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


    @api.response(200, 'Classifier deleted successfuly')
    @api.expect(classifierSerializer)
    @token_auth.login_required
    def delete(self):
        """
        Method used to delete classifier in database
        receives in body request a classifier model
        action should be anything
        """
        classifier = request.json

        classifier = namedtuple("Classifier", classifier.keys())(*classifier.values())
        repository = ClassifierRepository(
                FLASK_APP.config["DBUSER"],
                FLASK_APP.config["DBPASS"],
                FLASK_APP.config["DBHOST"],
                FLASK_APP.config["DBPORT"],
                FLASK_APP.config["DBNAME"])

        try:
            status = repository.delete(classifier)
            if (status):
                resp = models.Classifier.Classifier()
                resp.plant = resp.plant.__dict__
                Logger.Logger.create(FLASK_APP.config["ELASTICURL"],
                                     'Informative',
                                     'Classifier deleted sucessfuly',
                                     'delete()',
                                     str(resp),
                                     FLASK_APP.config["TYPE"])
                return self.okResponse(
                    response=resp,
                    message="Classifier deleted sucessfuly.",
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

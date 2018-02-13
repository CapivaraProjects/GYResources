import time
import models.Disease
import models.Plant
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api
from collections import namedtuple
from repository.DiseaseRepository import DiseaseRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import disease as diseaseSerializer
from api.gyresources.parsers import disease_search_args
from tools import Logger

flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

ns = api.namespace('gyresources/diseases',
                   description='Operations related to diseases')


@ns.route('/')
class DiseaseController(BaseController):
    """
    This class was created with the objective to control functions
        from DiseaseRepository, here, you can insert, update and delete
        data. Searchs are realized in DiseaseSearch.
    """

    @api.expect(disease_search_args)
    @api.response(200, 'Disease searched.')
    def get(self):
        """
        Return a list of diseases based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use scientificName or commonName to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.Disease.Disease()
        total = 0
        message = 'empty var'
        action = request.args.get('action')
        id = request.args.get('id')
        disease = models.Disease.Disease(
                      scientificName=request.args.get('scientificName'),
                      commonName=request.args.get('commonName'))
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
        repository = DiseaseRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)
                result.plant = result.plant.__dict__
                return self.okResponse(
                            response=result,
                            message="Ok",
                            status=200)
            elif (action == 'search'):
                result = repository.search(disease, pageSize, offset)
                total = result['total']
                response = []
                for content in result['content']:
                    content.plant = content.plant.__dict__
                    response.append(content)
                return self.okResponse(
                            response=response,
                            message="Ok",
                            status=200,
                            total=total,
                            offset=offset,
                            pageSize=pageSize), 200
        except (exc.SQLAlchemyError) as sqlerr:
            # log
            return self.okResponse(
                response=sqlerr,
                message="SQL error: "+str(sqlerr),
                status=500)
        except Exception as err:
            return self.okResponse(
                response=err,
                message="Internal server error "+str(err),
                status=500)
        str(message.__dict__)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Get disease of plants',
                             message,
                             'get()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Disease successfuly created.')
    @api.expect(diseaseSerializer)
    def post(self):
        """
        Method used to insert disease in database
        receives in body request a disease model
        action should be anything
        """
        disease = request.json

        disease = namedtuple("Disease", disease.keys())(*disease.values())
        disease = models.Disease.Disease(
                      id=None,
                      scientificName=disease.scientificName,
                      commonName=disease.commonName,
                      plant=models.Plant.Plant(id=disease.idPlant))
        repository = DiseaseRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            disease = repository.create(disease)
            disease.plant = disease.plant.__dict__
            return self.okResponse(
                response=disease,
                message="Disease sucessfuly created.",
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
        str(message.__dict__)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Post method of a Disease',
                              message,
                             'post()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Disease changed successfuly')
    @api.expect(diseaseSerializer)
    def put(self):
        """
        Method used to update disease in database
        receives in body request a disease model
        action should be anything
        """
        disease = request.json

        disease = namedtuple("Disease", disease.keys())(*disease.values())
        disease = models.Disease.Disease(
                      id=disease.id,
                      scientificName=disease.scientificName,
                      commonName=disease.commonName,
                      plant=models.Plant.Plant(id=disease.idPlant))
        repository = DiseaseRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            disease = repository.update(disease)
            disease.plant = disease.plant.__dict__
            return self.okResponse(
                response=disease,
                message="Disease sucessfuly updated.",
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
                message="Internal server error: " + str(err),
                status=500)
        return self.okResponse(
                response=disease,
                message="Disease sucessfuly updated.",
                status=204), 200
        str(message.__dict__)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                         'Informative. Update a disease of a plant',
                         message,
                         'put()',
                         'Empty',
                         'TEST')

    @api.response(200, 'Disease deleted successfuly')
    @api.expect(diseaseSerializer)
    def delete(self):
        """
        Method used to delete disease in database
        receives in body request a disease model
        action should be anything
        """
        disease = request.json

        disease = namedtuple("Disease", disease.keys())(*disease.values())
        repository = DiseaseRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            status = repository.delete(disease)
            if (status):
                resp = models.Disease.Disease()
                resp.plant = resp.plant.__dict__
                return self.okResponse(
                    response=resp,
                    message="Disease deleted sucessfuly.",
                    status=204), 200
            else:
                return self.okResponse(
                    response=disease,
                    message="Problem deleting disease",
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
        str(message.__dict__)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Delete a disease',
                             message,
                             'delete()',
                             'Empty',
                             'TEST')

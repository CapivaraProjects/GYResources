import time
import models.Plant
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api, token_auth
from collections import namedtuple
from repository.PlantRepository import PlantRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import plant as plantSerializer
from api.gyresources.parsers import plant_search_args
from tools import Logger

flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

ns = api.namespace('gyresources/plants',
                   description='Operations related to plants')


@ns.route('/')
class PlantController(BaseController):
    """
    This class was created with the objective to control functions
        from PlantRepository, here, you can insert, update and delete
        data. Searchs are realized in PlantSearch.
    """

    @api.expect(plant_search_args)
    @api.response(200, 'Plant searched.')
    def get(self):
        """
        Return a list of plants based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use scientificName or commonName to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.Plant.Plant()
        total = 0
        action = request.args.get('action')
        id = request.args.get('id')
        plant = models.Plant.Plant(
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
        repository = PlantRepository(
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
                                     'OK',
                                     'get()',
                                     str(result.__dict__),
                                     'TEST')
                return self.okResponse(
                            response=result,
                            message="Ok",
                            status=200)
            elif (action == 'search'):
                result = repository.search(plant, pageSize, offset)
                total = result['total']
                result = result['content']
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(result),
                                     'TEST')
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
                                 'TEST')
            return self.okResponse(
                response=sqlerr,
                message="SQL error: "+str(sqlerr),
                status=500)

    @api.response(200, 'Plant successfuly created.')
    @api.expect(plantSerializer)
    @token_auth.login_required
    def post(self):
        """
        Method used to insert plant in database
        receives in body request a plant model
        """
        plant = request.json

        plant = namedtuple("Plant", plant.keys())(*plant.values())
        plant = models.Plant.Plant(
            id=None,
            scientificName=plant.scientificName,
            commonName=plant.commonName)

        repository = PlantRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            plant = repository.create(plant)
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Plant sucessfuly created',
                                 'post()',
                                 str(plant.__dict__),
                                 'TEST')
            return self.okResponse(
                response=plant,
                message="Plant sucessfuly created.",
                status=201), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'post()',
                                 str(sqlerr),
                                 'TEST')
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
                                 'TEST')
            return self.okResponse(
                response=err,
                message="Internal server error "+str(err),
                status=500)


    @api.response(200, 'Plant changed successfuly')
    @api.expect(plantSerializer)
    @token_auth.login_required
    def put(self):
        """
        Method used to update plant in database
        receives in body request a plant model
        action should be anything
        """
        plant = request.json

        plant = namedtuple("Plant", plant.keys())(*plant.values())
        repository = PlantRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            plant = repository.update(plant)
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Plant sucessfuly updated',
                                 'put()',
                                 str(plant.__dict__),
                                 'TEST')
            return self.okResponse(
                response=plant,
                message="Plant sucessfuly updated.",
                status=204), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'put()',
                                 str(sqlerr),
                                 'TEST')
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
                                 'TEST')
            return self.okResponse(
                response=err,
                message="Internal server error",
                status=500)


    @api.response(200, 'Plant deleted successfuly')
    @api.expect(plantSerializer)
    @token_auth.login_required
    def delete(self):
        """
        Method used to delete plant in database
        receives in body request a plant model
        action should be anything
        """
        plant = request.json

        plant = namedtuple("Plant", plant.keys())(*plant.values())
        repository = PlantRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            status = repository.delete(plant)
            if (status):
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Plant deleted sucessfuly',
                                     'delete()',
                                     'Empty',
                                     'TEST')
                return self.okResponse(
                    response=models.Plant.Plant(),
                    message="Plant deleted sucessfuly.",
                    status=204), 200
            else:
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Error',
                                     'Problem deleting plant',
                                     'delete()',
                                     str(plant.__dict__),
                                     'TEST')
                return self.okResponse(
                    response=plant,
                    message="Problem deleting plant",
                    status=500), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL Error',
                                 'delete()',
                                 str(sqlerr),
                                 'TEST')
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
                                 'TEST')
            return self.okResponse(
                response=err,
                message="Internal server error: "+str(err),
                status=500)


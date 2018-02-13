import time
import models.Plant
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api
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
        message = 'empty var'
        action = request.args.get('action')
        id = request.args.get('id')
        plant = models.Plant.Plant(
                      scientificName=request.args.get('scientificName'),
                      commonName=request.args.get('commonName'))
        pageSize = request.args.get('pageSize')
        offset = request.args.get('offset')
        repository = PlantRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)
                return self.okResponse(
                            response=result,
                            message="Ok",
                            status=200)
            elif (action == 'search'):
                result = repository.search(plant, pageSize, offset)
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
        str(message.dict)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Get a plant',
                             message,
                             'get()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Plant successfuly created.')
    @api.expect(plantSerializer)
    def post(self):
        """
        Method used to insert plant in database
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
            plant = repository.create(plant)
            return self.okResponse(
                response=plant,
                message="Plant sucessfuly created.",
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
        str(message.dict)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Insert a plant',
                             message,
                             'post()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Plant changed successfuly')
    @api.expect(plantSerializer)
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
            return self.okResponse(
                response=plant,
                message="Plant sucessfuly updated.",
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
                response=plant,
                message="Plant sucessfuly updated.",
                status=204), 200
        str(message.dict)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Update a plant',
                             message,
                             'put()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Plant deleted successfuly')
    @api.expect(plantSerializer)
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
                return self.okResponse(
                    response=models.Plant.Plant(),
                    message="Plant deleted sucessfuly.",
                    status=204), 200
            else:
                return self.okResponse(
                    response=plant,
                    message="Problem deleting plant",
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
        str(message.dict)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Delete a plant',
                             message,
                             'delete()',
                             'Empty',
                             'TEST')

import time
import models.Plant
from sqlalchemy import exc
from flask import request
from api.restplus import api
from collections import namedtuple
from repository.PlantRepository import PlantRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import plant as plantSerializer


ns = api.namespace('gyresources/plants',
                   description='Operations related to plants')


@ns.route('/<string:action>/<int:id>')
class PlantSearch(BaseController):
    """
    This class was created with the objective to use get function with a
        action parameter, so you will've to use the same function get using
        action to set what you want, and another parameters like
        scientificName, commonName, should be getted from request.args
    """

    @api.response(200, 'Plant searched.')
    def get(self, action, id):
        """
        Return a list of plants based on action.

        If action=searchById:
            please set id parameter.

        If action=search:
            you can use scientificName or commonName to search,
            please define pageSize and offset parameters
        """
        self.startTime = time.time()
        result = models.Plant.Plant()
        total = 0
        plant = models.Plant.Plant(
                      scientificName=request.args.get('scientificName'),
                      commonName=request.args.get('commonName'))
        pageSize = request.args.get('pageSize')
        offset = request.args.get('offset')
        repository = PlantRepository(
                'capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')
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


@ns.route('/')
class PlantController(BaseController):
    """
    This class was created with the objective to control functions
        from PlantRepository, here, you can insert, update and delete
        data. Searchs are realized in PlantSearch.
    """

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
                'capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')

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
                'capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')
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
                'capivara',
                'test',
                '127.0.0.1',
                '5432',
                'green_eyes')

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


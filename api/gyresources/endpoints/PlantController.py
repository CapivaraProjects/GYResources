import time
from flask import request
from api.restplus import api
import models.Plant
from repository.PlantRepository import PlantRepository
from api.gyresources.endpoints.BaseController import BaseController


ns = api.namespace('gyresources/plants',
                   description='Operations related to plants')


@ns.route('/<string:action>')
class PlantController(BaseController):

    def get(self, action):
        """
        Return a list of plants
        """
        self.startTime = time.time()
        result = object()
        total = 0
        id = request.args.get('id')
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
        if (action == 'searchByID'):
            result = repository.searchByID(int(id))
        elif (action == 'search'):
            result = repository.search(plant, int(pageSize), int(offset))
            total = result['total']
            result = result['content']

        if(total == 0):
            return self.okResponse(
                response=result,
                message="Ok",
                status=200)
        else:
            return self.okResponse(
                response=result,
                message="Ok",
                status=200,
                total=total,
                offset=offset,
                pageSize=pageSize)

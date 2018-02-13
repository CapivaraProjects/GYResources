import time
import models.Image
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api
from collections import namedtuple
from repository.ImageRepository import ImageRepository
from repository.DiseaseRepository import DiseaseRepository
from api.gyresources.endpoints.BaseController import BaseController
from api.gyresources.serializers import image as imageSerializer
from api.gyresources.parsers import image_search_args
from tools import Logger

flask_app = Flask(__name__)
flask_app.config.from_object('config.DefaultConfig')

ns = api.namespace(
        'gyresources/images',
        description='Operations related to images')


@ns.route('/')
class ImageController(BaseController):
    """
    This class was created with the objective to control functions
        from ImageRepository, here, you can insert, update, delete
        and search data.
    """

    @api.expect(image_search_args)
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
        result = models.Image.Image()
        total = 0
        message = 'empty var'
        action = request.args.get('action')
        id = request.args.get('id')
        image = models.Image.Image(
                url=request.args.get('url'),
                description=request.args.get('description'),
                source=request.args.get('source'),
                size=request.args.get('size'))
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

        repository = ImageRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            if (action == 'searchByID'):
                result = repository.searchByID(id)
                result.disease.plant = result.disease.plant.__dict__
                result.disease = result.disease.__dict__
                return self.okResponse(
                        response=result,
                        message="Ok",
                        status=200)
            elif (action == 'search'):
                result = repository.search(image, pageSize, offset)
                total = result['total']
                response = []
                for content in result['content']:
                    content.disease.plant = content.disease.plant.__dict__
                    content.disease = content.disease.__dict__
                    response.append(content)
                return self.okResponse(
                        response=response,
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
        str(message.__dict__)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Get a image of a plant',
                             message,
                             'get()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Image successfuly created.')
    @api.expect(imageSerializer)
    def post(self):
        """
        Method used to insert image in database
        receives in body request a image model
        """
        image = request.json
        message = 'empty var'

        image = namedtuple("Image", image.keys())(*image.values())

        action = image.action
        image = models.Image.Image(
                description=image.description,
                disease=models.Disease.Disease(image.idDisease),
                size=image.size,
                source=image.source,
                url=image.url)
        repository = ImageRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            if (action == 'create'):
                image = repository.create(image)
                image.disease.plant = image.disease.plant.__dict__
                image.disease = image.disease.__dict__
                return self.okResponse(
                    response=image,
                    message="Image sucessfuly created.",
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
                             'Informative. Insert a image of a plant',
                             message,
                             'get()',
                             'Empty',
                             'TEST')

    @api.response(200, 'Image changed successfuly')
    @api.expect(imageSerializer)
    def put(self):
        """
        Method used to update image in database
        receives in body request a image model
        action should be anything
        """
        image = request.json

        image = namedtuple("Image", image.keys())(*image.values())

        disease = DiseaseRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        repository = ImageRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        try:
            diesase = disease.searchByID(image.idDisease)
            image = models.Image.Image(
                    id=image.id,
                    description=image.description,
                    disease=diesase,
                    size=image.size,
                    source=image.source,
                    url=image.url)
            image = repository.update(image)
            image.disease.plant = image.disease.plant.__dict__
            image.disease = image.disease.__dict__
            return self.okResponse(
                response=image,
                message="Image sucessfuly updated.",
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
                response=image,
                message="Image sucessfuly updated.",
                status=204), 200
        str(message.__dict__)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Update a image of a plant',
                             message,
                             'get()',
                             'Empty',
                             'TEST')


    @api.response(200, 'Image deleted successfuly')
    @api.expect(imageSerializer)
    def delete(self):
        """
        Method used to delete image in database
        receives in body request a image model
        action should be anything
        """
        image = request.json

        image = namedtuple("Image", image.keys())(*image.values())
        image = models.Image.Image(id=image.id)
        repository = ImageRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            status = repository.delete(image)
            if (status):
                image = models.Image.Image()
                image.disease.plant = image.disease.plant.__dict__
                image.disease = image.disease.__dict__
                return self.okResponse(
                    response=image,
                    message="Image deleted sucessfuly.",
                    status=204), 200
            else:
                image.disease.plant = image.disease.plant.__dict__
                image.disease = image.disease.__dict__
                return self.okResponse(
                    response=image,
                    message="Problem deleting plant",
                    status=500), 200
        except exc.SQLAlchemyError as sqlerr:
            # log
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror" + str(sqlerr),
                status=500)
        except Exception as err:
            return self.okResponse(
                response=err,
                message="Internal server error: " + str(err),
                status=500)
        str(message.__dict__)
        Logger.Logger.create(flask_app.config["ELASTICURL"],
                             'Informative. Delete a image of a plant',
                             message,
                             'get()',
                             'Empty',
                             'TEST')

import time
import models.Image
from sqlalchemy import exc
from flask import request
from flask import Flask
from api.restplus import api, token_auth
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
    @api.response(200, 'Image search.')
    def get(self):
        """
        Return a list of plants based on action.

        If action=searchByID:
            please set id parameter.

        If action=search:
            you can use scientificName or commonName to search,
            please define pageSize and offset parameters

        If action=read:
            please set id parameter
            It will search by ID and return url with Base64 image
        """
        self.startTime = time.time()
        result = models.Image.Image()
        total = 0
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
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(result.__dict__),
                                     flask_app.config["TYPE"])
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
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                        'Informative',
                                        'Ok',
                                        'get()',
                                        str(response),
                                        flask_app.config["TYPE"])
                return self.okResponse(
                        response=response,
                        message="Ok",
                        status=200,
                        total=total,
                        offset=offset,
                        pageSize=pageSize), 200
            elif (action == 'read'):
                image = repository.searchByID(id)
                result = repository.getImageBase64(
                        image,
                        flask_app.config["IMAGESPATH"])
                result.disease.plant = result.disease.plant.__dict__
                result.disease = result.disease.__dict__
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Ok',
                                     'get()',
                                     str(result.__dict__),
                                     flask_app.config["TYPE"])
                return self.okResponse(
                        response=result,
                        message="Ok",
                        status=200)
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL error ',
                                 'get()',
                                 str(sqlerr),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=sqlerr,
                message="SQL error: " + str(sqlerr),
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error ',
                                 'get()',
                                 str(err),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error: " + str(err),
                status=500)

    @api.response(200, 'Image successfuly created.')
    @api.expect(imageSerializer)
    @token_auth.login_required
    def post(self):
        """
        Method used to insert image in database
        receives in body request a image model
        """
        image = request.json
        image = namedtuple("Image", image.keys())(*image.values())
        image = models.Image.Image(
            id=None,
            disease=models.Disease.Disease(id=image.idDisease),
            url=image.url,
            description=image.description,
            source=image.source,
            size=image.size)

        repository = ImageRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])
        diseaseRepository = DiseaseRepository(
                flask_app.config["DBUSER"],
                flask_app.config["DBPASS"],
                flask_app.config["DBHOST"],
                flask_app.config["DBPORT"],
                flask_app.config["DBNAME"])

        try:
            # if image is base 64 encoded save in a file
            if (image.url.strip()[-1] == '='):
                image.disease = diseaseRepository.searchByID(image.disease.id)
                image = repository.saveImage(
                        image,
                        flask_app.config["IMAGESPATH"])
            image = repository.create(image)
            image.disease.plant = image.disease.plant.__dict__
            image.disease = image.disease.__dict__
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Image sucessfuly created',
                                 'post()',
                                 str(image.__dict__),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=image,
                message="Image sucessfuly created.",
                status=201), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL eror ',
                                 'post()',
                                 str(sqlerr),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error ',
                                 'post()',
                                 str(err),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error "+str(err),
                status=500)

    @api.response(200, 'Image changed successfuly')
    @api.expect(imageSerializer)
    @token_auth.login_required
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
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Informative',
                                 'Image sucessfuly updated',
                                 'put()',
                                 str(image.__dict__),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=image,
                message="Image sucessfuly updated.",
                status=204), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL eror',
                                 'put()',
                                 str(sqlerr),
                                 flask_app.config["TYPE"])
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror",
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error',
                                 'put()',
                                 str(err),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error: " + str(err),
                status=500)


    @api.response(200, 'Image deleted successfuly')
    @api.expect(imageSerializer)
    @token_auth.login_required
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
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Informative',
                                     'Image deleted sucessfuly',
                                     'delete()',
                                     str(image.__dict__),
                                     flask_app.config["TYPE"])
                return self.okResponse(
                    response=image,
                    message="Image deleted sucessfuly.",
                    status=204), 200
            else:
                image.disease.plant = image.disease.plant.__dict__
                image.disease = image.disease.__dict__
                Logger.Logger.create(flask_app.config["ELASTICURL"],
                                     'Error',
                                     'Problem deleting plant',
                                     'delete()',
                                     str(image.__dict__),
                                     flask_app.config["TYPE"])
                return self.okResponse(
                    response=image,
                    message="Problem deleting plant",
                    status=500), 200
        except exc.SQLAlchemyError as sqlerr:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'SQL eror',
                                 'put()',
                                 str(sqlerr),
                                 flask_app.config["TYPE"])
            print(str(sqlerr))
            return self.okResponse(
                response=sqlerr,
                message="SQL eror" + str(sqlerr),
                status=500)
        except Exception as err:
            Logger.Logger.create(flask_app.config["ELASTICURL"],
                                 'Error',
                                 'Internal server error',
                                 'put()',
                                 str(err),
                                 flask_app.config["TYPE"])
            return self.okResponse(
                response=err,
                message="Internal server error: " + str(err),
                status=500)


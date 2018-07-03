from flask_restplus import fields
from api.restplus import api

"""
Here we have something like parsers, the difference here, we're building
default json models, which can be used in swagger as example.
"""

image = api.model('Image', {
    'id': fields.Integer(readOnly=True, description='Disease identification'),
    'idDisease': fields.Integer(
        required=True,
        attribute='disease.id',
        description='Disease ID'),
    'url': fields.String(description='URL image or base64 image'),
    'description': fields.String(description='Description'),
    'source': fields.String(description='Metadata info'),
    'size': fields.Integer(description='Size type'),
    })

disease = api.model('Disease', {
    'id': fields.Integer(readOnly=True, description='Disease identification'),
    'idPlant': fields.Integer(
        required=True,
        attribute='plant.id',
        description='Plant ID'),
    'scientificName': fields.String(
        required=True,
        description='Scientific name'),
    'commonName': fields.String(
        required=True,
        description='Common name'),
    'images': fields.List(fields.Nested(image)),
    })

plant = api.model('Plant', {
    'id': fields.Integer(readOnly=True, description='Plant identification'),
    'scientificName': fields.String(
        required=True,
        description='Scientific name'),
    'commonName': fields.String(
        required=True,
        description='Common name'),
    'diseases': fields.List(fields.Nested(disease))
    })

text = api.model('Text', {
    'id': fields.Integer(readOnly=True, description='Text identification'),
    'language': fields.String(
        required=True,
        description='Text language'),
    'tag': fields.String(
        required=True,
        description='Text tag'),
    'value': fields.String(
        required=True,
        description='Text value'),
    'description': fields.String(
        required=True,
        description='Text description')
    })

type = api.model('Type', {
    'id': fields.Integer(readOnly=True, description='Type identification'),
    'value': fields.String(
        required=True,
        description='Type value'),
    'description': fields.String(
        required=True,
        description='Type description'),
    })

user = api.model('User', {
    'id': fields.Integer(readOnly=True, description='User identification'),
    'idType': fields.Integer(
        required=True,
        description='Type identification'),
    'email': fields.String(
        required=True,
        description='Email'),
    'username': fields.String(
        required=True,
        description='Username'),
    'password': fields.String(
        required=True,
        description='Password'),
    'salt': fields.String(
        required=True,
        description='User salt'),
    'dateInsertion': fields.String(
        required=True,
        description='User date insertion'),
    'dateUpdate': fields.String(
        required=True,
        description='User last update'),
    })

analysis = api.model('Analysis', {
    'id': fields.Integer(
        readOlny=True,
        description='Analysis identification'),
    'idImage': fields.Integer(
        required=True,
        description='Image identification')
    })

analysisResult = api.model('AnalysisResult', {
    'id': fields.Integer(
        readOnly=True,
        description='Analysis result identification'),
    'idAnalysis': fields.Integer(
        required=True,
        description='Analysis identification'),
    'idDisease': fields.Integer(
        required=True,
        description='Disease identification'),
    'score': fields.Float(
        required=True,
        description='score of analysis')
    })

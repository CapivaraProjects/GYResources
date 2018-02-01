from flask_restplus import Api


api = Api(version='1.0', title='GYResources-API',
          description='Services application used by Green Eyes applications')


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    return {'message': message}, 500

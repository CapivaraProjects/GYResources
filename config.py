import os


class DefaultConfig(object):
    """Default configuration"""
    # Database setting
    DBHOST = '127.0.0.1'
    DBUSER = 'capivara'
    DBPASS = 'test'
    DBPORT = '5432'
    DBNAME = 'green_eyes'
    # Application setting
    SERVER_NAME = '127.0.0.1:8888'
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    RESTPLUS_ERROR_404_HELP = False
    TYPE = 'DEV'
    ELASTICURL = 'http://127.0.0.1:9200'
    SECRET_KEY = 'testing gyresources api'
    IMAGESPATH = os.getcwd()
    EXPIRATION_TOKEN = 600


class TestConfig(object):
    """Test configuration"""
    # Database setting
    DBHOST = '127.0.0.1'
    DBUSER = 'capivara'
    DBPASS = 'test'
    DBPORT = '5432'
    DBNAME = 'green_eyes'
    # Application setting
    SERVER_NAME = '127.0.0.1:8888'
    SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    RESTPLUS_ERROR_404_HELP = False
    TYPE = 'TEST'
    ELASTICURL = 'http://127.0.0.1:9200'
    SECRET_KEY = 'testing gyresources api'
    IMAGESPATH = os.getcwd()
    EXPIRATION_TOKEN = 30

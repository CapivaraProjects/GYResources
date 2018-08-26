from flask_restplus import reqparse

"""
This script is used to create parsers, it means, parameters which will be used
in actions inside Controllers, as we can repair, every controller use HTTP
methods for requests, here we create what it expects and documents.
"""
plant_search_args = reqparse.RequestParser()
plant_search_args.add_argument('action', type=str, required=True,
                               default='searchByID',
                               help='Defines what kind of search you gonna do',
                               choices=['searchByID', 'search'])
plant_search_args.add_argument('id', type=int, required=False, default=1,
                               help='Plant ID, used when action=searchByID')
plant_search_args.add_argument('scientificName', type=str, required=False,
                               default='', help='Plant scientific name')
plant_search_args.add_argument('commonName', type=str, required=False,
                               default='', help='Plant common name')
plant_search_args.add_argument('pageSize', type=int, required=False,
                               default=10,
                               help='Quantity of elements required')
plant_search_args.add_argument('offset', type=int, required=False, default=10,
                               help='Quantity of elements to be jumped')

text_search_args = reqparse.RequestParser()
text_search_args.add_argument('action', type=str, required=True,
                              default='searchByID',
                              help='Defines what kind of search you gonna do.',
                              choices=['searchByID', 'search'])
text_search_args.add_argument('id', type=int, required=False, default=1,
                              help='Text ID, used when action=searchByID')
text_search_args.add_argument('language', type=str, required=False,
                              default='', help='Text language')
text_search_args.add_argument('tag', type=str, required=False,
                              default='', help='Text tag')
text_search_args.add_argument('value', type=str, required=False,
                              default='', help='Text value')
text_search_args.add_argument('description', type=str, required=False,
                              default='', help='Text description')
text_search_args.add_argument('pageSize', type=int, required=False,
                              default=10,
                              help='Quantity of elements required')
text_search_args.add_argument('offset', type=int, required=False, default=10,
                              help='Quantity of elements to be jumped')

type_search_args = reqparse.RequestParser()
type_search_args.add_argument('action', type=str, required=True,
                              default='searchByID',
                              help='Defines what kind of search you gonna do.',
                              choices=['searchByID', 'search'])
type_search_args.add_argument('id', type=int, required=False, default=1,
                              help='Type ID, used when action=searchByID')
type_search_args.add_argument('value', type=str, required=False,
                              default='', help='Type value')
type_search_args.add_argument('description', type=str, required=False,
                              default='', help='Type description')
type_search_args.add_argument('pageSize', type=int, required=False,
                              default=10,
                              help='Quantity of elements required')
type_search_args.add_argument('offset', type=int, required=False, default=10,
                              help='Quantity of elements to be jumped')

image_search_args = reqparse.RequestParser()
image_search_args.add_argument('action', type=str, required=True,
                               default='searchByID',
                               help='Defines what kind of search you gonna do',
                               choices=['searchByID', 'search', 'read'])
image_search_args.add_argument('id', type=int, required=False, default=1,
                               help='Image ID, used when action=searchByID')
image_search_args.add_argument('url', type=str, required=False,
                               default='', help='Image URL')
image_search_args.add_argument('description', type=str, required=False,
                               default='', help='Image description')
image_search_args.add_argument('source', type=str, required=False,
                               default='', help='Image metadata')
image_search_args.add_argument('size', type=int, required=False,
                               default='', help='Image size',
                               choices=[1, 2, 3])
image_search_args.add_argument('pageSize', type=int, required=False,
                               default=10,
                               help='Quantity of elements required')
image_search_args.add_argument('offset', type=int, required=False, default=0,
                               help='Quantity of elements to be jumped')

user_search_args = reqparse.RequestParser()
user_search_args.add_argument('action', type=str, required=True,
                              default='searchByID',
                              help='Defines what kind of search you gonna do.',
                              choices=['searchByID', 'search'])
user_search_args.add_argument('id', type=int, required=False, default=1,
                              help='User ID, used when action=searchByID')
user_search_args.add_argument('idType', type=int, required=False,
                              default='', help='Type ID')
user_search_args.add_argument('email', type=str, required=False,
                              default='', help='Email')
user_search_args.add_argument('username', type=str, required=False,
                              default='', help='Username')
user_search_args.add_argument('password', type=str, required=False,
                              default='', help='Password')
user_search_args.add_argument('salt', type=str, required=False,
                              default='', help='User salt')
user_search_args.add_argument('dateInsertion', type=str, required=False,
                              default='', help='User date insertion')
user_search_args.add_argument('dateUpdate', type=str, required=False,
                              default='', help='User last update')
user_search_args.add_argument('pageSize', type=int, required=False,
                              default=10,
                              help='Quantity of elements required')
user_search_args.add_argument('offset', type=int, required=False, default=10,
                              help='Quantity of elements to be jumped')

disease_search_args = reqparse.RequestParser()
disease_search_args.add_argument(
        'action', type=str, required=True,
        default='searchByID',
        help='Defines what kind of search you gonna do',
        choices=['searchByID', 'search'])
disease_search_args.add_argument('id', type=int, required=False, default=1,
                                 help='Plant ID, used when action=searchByID')
disease_search_args.add_argument('scientificName', type=str, required=False,
                                 default='', help='Plant scientific name')
disease_search_args.add_argument('commonName', type=str, required=False,
                                 default='', help='Plant common name')
disease_search_args.add_argument('pageSize', type=int, required=False,
                                 default=10,
                                 help='Quantity of elements required')
disease_search_args.add_argument('offset', type=int, required=False,
                                 default=10,
                                 help='Quantity of elements to be jumped')

classifier_search_args = reqparse.RequestParser()
classifier_search_args.add_argument(
        'action', type=str, required=True,
        default='searchByID',
        help='Defines what kind of search you gonna do',
        choices=['searchByID', 'search'])
classifier_search_args.add_argument('id', type=int, required=False, default=1,
                                 help='Plant ID, used when action=searchByID')
classifier_search_args.add_argument('tag', type=str, required=False,
                                 default='', help='tag version of classifier')
classifier_search_args.add_argument('path', type=str, required=False,
                                 default='', help='model path')
classifier_search_args.add_argument('pageSize', type=int, required=False,
                                 default=10,
                                 help='Quantity of elements required')
classifier_search_args.add_argument('offset', type=int, required=False,
                                 default=0,
                                 help='Quantity of elements to be jumped')

log_post_args = reqparse.RequestParser()
log_post_args.add_argument('url', type=str, required=True, default='',
                           help='URL from the ambient that you running')
log_post_args.add_argument('type', type=str, required=False, default='',
                           help='Type of log (Error or informative')
log_post_args.add_argument('message', type=str, required=False, default='No messages here',
                           help='Message to be sended by the POST method')
log_post_args.add_argument('function', type=str, required=True, default='',
                           help='Function of exception')
log_post_args.add_argument('obs', type=str, required=False, default='No observation here',
                           help='Observation of method')
log_post_args.add_argument('config', type=str, required=True, default='',
                           help='Ambient that you are working (EX: TEST, PRODUCTION)')

analysis_search_args = reqparse.RequestParser()
analysis_search_args.add_argument('action', type=str, required=True,
                              default='searchByID',
                              help='Defines what kind of search you gonna do.',
                              choices=['searchByID', 'search'])
analysis_search_args.add_argument('id', type=int, required=False, default=1,
                              help='Analysis ID, used when action=searchByID')
analysis_search_args.add_argument('idImage', type=int, required=False,
                              default='', help='Image ID')
analysis_search_args.add_argument('idClassifier', type=int, required=False,
                              default='', help='Classifier ID')
analysis_search_args.add_argument('pageSize', type=int, required=False,
                              default=10,
                              help='Quantity of elements required')
analysis_search_args.add_argument('offset', type=int, required=False, default=10,
                              help='Quantity of elements to be jumped')

analysisResult_search_args = reqparse.RequestParser()
analysisResult_search_args.add_argument('action', type=str, required=True,
                              default='searchByID',
                              help='Defines what kind of search you gonna do.',
                              choices=['searchByID', 'search'])
analysisResult_search_args.add_argument('id', type=int, required=False, default=1,
                              help='AnalysisResult ID, used when action=searchByID')
analysisResult_search_args.add_argument('idAnalysis', type=int, required=False,
                              default='', help='Analysis ID')
analysisResult_search_args.add_argument('idDisease', type=int, required=False,
                              default='', help='Disease ID')
analysisResult_search_args.add_argument('score', type=float, required=False,
                              default='', help='predicted score')
analysisResult_search_args.add_argument('frame', type=str, required=False,
                              default='', help='frame (28x28) of an image')
analysisResult_search_args.add_argument('pageSize', type=int, required=False,
                              default=10,
                              help='Quantity of elements required')
analysisResult_search_args.add_argument('offset', type=int, required=False, default=10,
                              help='Quantity of elements to be jumped')

from flask_restplus import reqparse

"""
This script is used to create parsers, it means, parameters which will be used in
actions inside Controllers, as we can repair, every controller use HTTP methods
for requests, here we create what it expects and documents.
"""
plant_search_args = reqparse.RequestParser()
plant_search_args.add_argument('action', type=str, required=True,
                               default='searchByID',
                               help='Defines what kind of search you gonna do.',
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

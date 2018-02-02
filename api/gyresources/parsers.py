from flask_restplus import reqparse

"""
This script is used to create parsers, it means, parameters which will be used in
actions inside Controllers, as we can repair, every controller use HTTP methods 
for requests, here we create what it expects and documents.
"""
plant_search_args = reqparse.RequestParser()
plant_search_args.add_argument('action', type=str, required=True,
                               default='searchByID',
                               help='Defines what kind of search you gonna do.'
                               + 'DO YOU KNOW THE WAY?',
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

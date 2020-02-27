# ---
# name: sampledata-contact
# deployed: true
# title: Sample Data Contact
# description: Returns a list of fake contact information
# params:
#   - name: properties
#     type: array
#     description: The properties to return (defaults to all properties). See "Returns" for a listing of the available properties.
#     required: false
#   - name: count
#     type: integer
#     description: Number of fake records to return, between 0 and 10000; defaults to 100
#     required: false
# returns:
#   - name: street1
#     type: string
#     description: The primary street address for the contact info
#   - name: street2
#     type: string
#     description: The secondary street address for the contact info, such as a unit number
#   - name: city
#     type: string
#     description: The city for the address contact info
#   - name: state
#     type: string
#     description: The state for the address contact info
#   - name: zip
#     type: string
#     description: The zipcode for the address contact info
#   - name: email
#     type: string
#     description: A contact email address
#   - name: phone
#     type: string
#     description: A contact phone number
#   - name: homepage
#     type: string
#     description: A contact website
# examples:
#   - '1, "street1, city, state, zip"'
#   - '10, "city, state, zip"'
# ---

import json
import itertools
from datetime import *
from decimal import *
from cerberus import Validator
from collections import OrderedDict
from faker import Faker

def flexio_handler(flex):

    # get the input
    input = flex.input.read()
    try:
        input = json.loads(input)
        if not isinstance(input, list): raise ValueError
    except ValueError:
        raise ValueError

    # define the expected parameters and map the values to the parameter names
    # based on the positions of the keys/values
    params = OrderedDict()
    params['properties'] = {'required': False, 'validator': validator_list, 'coerce': to_list, 'default': '*'}
    params['count'] = {'required': True, 'type': 'integer', 'min': 0, 'max': 10000, 'coerce': int, 'default': 100}
    input = dict(zip(params.keys(), input))

    # validate the mapped input against the validator
    v = Validator(params, allow_unknown = True)
    input = v.validated(input)
    if input is None:
        raise ValueError

    # map this function's property names to appropriate function call
    # use python faker library; see here for more information:
    #   project: https://github.com/joke2k/faker
    #   documentation: https://faker.readthedocs.io/en/latest/index.html
    #   providers: https://faker.readthedocs.io/en/latest/providers.html
    property_map = OrderedDict()
    property_map['street1'] = lambda faker: faker.street_address()
    property_map['street2'] = lambda faker: faker.secondary_address()
    property_map['city'] = lambda faker: faker.city()
    property_map['state'] = lambda faker: faker.state_abbr()
    property_map['zip'] = lambda faker: faker.postalcode_in_state()
    property_map['email'] = lambda faker: faker.safe_email()
    property_map['phone'] = lambda faker: faker.phone_number()
    property_map['homepage'] = lambda faker: faker.uri()

    try:

        # get the properties to return and the property map
        properties = [p.lower().strip() for p in input['properties']]

        # if we have a wildcard, get all the properties
        if len(properties) == 1 and properties[0] == '*':
            properties = list(property_map.keys())

        # build up the result
        result = []

        # don't include header for now
        # result.append(properties)

        faker = Faker()
        for x in range(input['count']):
            row = [property_map.get(p,lambda item: '')(faker) or '' for p in properties]
            result.append(row)

        result = json.dumps(result, default=to_string)
        flex.output.content_type = "application/json"
        flex.output.write(result)

    except:
        raise RuntimeError

def validator_list(field, value, error):
    if isinstance(value, str):
        return
    if isinstance(value, list):
        for item in value:
            if not isinstance(item, str):
                error(field, 'Must be a list with only string values')
        return
    error(field, 'Must be a string or a list of strings')

def to_string(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (Decimal)):
        return str(value)
    return value

def to_list(value):
    # if we have a list of strings, create a list from them; if we have
    # a list of lists, flatten it into a single list of strings
    if isinstance(value, str):
        return value.split(",")
    if isinstance(value, list):
        return list(itertools.chain.from_iterable(value))
    return None


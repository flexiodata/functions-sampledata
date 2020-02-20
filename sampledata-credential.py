# ---
# name: sampledata-credential
# deployed: true
# title: Sample Data Credential
# description: Returns a list of fake credential information
# params:
# - name: count
#   type: integer
#   description: Number of fake records to return, between 0 and 10000
#   required: true
# - name: properties
#   type: array
#   description: The properties to return (defaults to all properties). See "Returns" for a listing of the available properties.
#   required: false
# returns:
# - name: email
#   type: string
#   description: An email address
# - name: username
#   type: string
#   description: A username
# - name: password
#   type: string
#   description: A password
# examples:
# - '1, "email, username"'
# - '10, "email"'
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
    params['count'] = {'required': True, 'type': 'integer', 'min': 0, 'max': 10000, 'coerce': int}
    params['properties'] = {'required': False, 'validator': validator_list, 'coerce': to_list, 'default': '*'}
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
    property_map['email'] = lambda faker: faker.safe_email()
    property_map['username'] = lambda faker: faker.user_name()
    property_map['password'] = lambda faker: faker.password()

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


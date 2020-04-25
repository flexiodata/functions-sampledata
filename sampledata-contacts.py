# ---
# name: sampledata-contacts
# deployed: true
# title: Sample Data Contacts
# description: Returns a list of sample contact information
# params:
#   - name: properties
#     type: array
#     description: The properties to return (defaults to all properties). See "Returns" for a listing of the available properties.
#     required: false
#   - name: filter
#     type: string
#     description: Placeholder for filter; note: filter unimplemented for sample data
#     required: false
# returns:
#   - name: first_name
#     type: string
#     description: The first name of the person
#   - name: last_name
#     type: string
#     description: The last name of the person
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
import urllib
import itertools
from datetime import *
from decimal import *
from cerberus import Validator
from collections import OrderedDict
from faker import Faker

def flexio_handler(flex):

    # generate values using following library:
    # project: https://github.com/joke2k/faker
    # documentation: https://faker.readthedocs.io/en/latest/index.html
    # providers: https://faker.readthedocs.io/en/latest/providers.html
    faker = Faker()

    # get the input
    input = flex.input.read()
    input = json.loads(input)
    if not isinstance(input, list):
        input = []

    # define the expected parameters and map the values to the parameter names
    # based on the positions of the keys/values
    params = OrderedDict()
    params['properties'] = {'required': False, 'validator': validator_list, 'coerce': to_list, 'default': '*'}
    params['filter'] = {'required': False, 'type': 'string', 'default': ''} # placeholder to match form of index-styled functions
    params['config'] = {'required': False, 'type': 'string', 'default': ''} # index-styled config string
    input = dict(zip(params.keys(), input))

    # validate the mapped input against the validator
    v = Validator(params, allow_unknown = True)
    input = v.validated(input)
    if input is None:
        raise ValueError

    # get the properties to return and the property map;
    # if we have a wildcard, get all the properties
    properties = [p.lower().strip() for p in input['properties']]
    if len(properties) == 1 and (properties[0] == '' or properties[0] == '*'):
        properties = list(get_item_info(faker).keys())

    # get any configuration settings
    config = urllib.parse.parse_qs(input['config'])
    config = {k: v[0] for k, v in config.items()}
    limit = int(config.get('limit', 100))
    headers = config.get('headers', 'true').lower()
    if headers == 'true':
        headers = True
    else:
        headers = False

    # write the output
    flex.output.content_type = 'application/json'
    flex.output.write('[')

    first_row = True
    if headers is True:
        result = json.dumps(properties)
        first_row = False
        flex.output.write(result)

    for item in get_data(faker, limit):
        result = json.dumps([item.get(p) for p in properties])
        if first_row is False:
            result = ',' + result
        first_row = False
        flex.output.write(result)

    flex.output.write(']')

def get_data(faker, limit):

    idx = 0
    while True:
        if idx >= limit:
            break
        yield get_item_info(faker)
        idx = idx + 1

def validator_list(field, value, error):
    if isinstance(value, str):
        return
    if isinstance(value, list):
        for item in value:
            if not isinstance(item, str):
                error(field, 'Must be a list with only string values')
        return
    error(field, 'Must be a string or a list of strings')

def to_list(value):
    # if we have a list of strings, create a list from them; if we have
    # a list of lists, flatten it into a single list of strings
    if isinstance(value, str):
        return value.split(",")
    if isinstance(value, list):
        return list(itertools.chain.from_iterable(value))
    return None

def get_item_info(item):

    info = OrderedDict()
    info['first_name'] = item.first_name()
    info['last_name'] = item.last_name()
    info['street1'] = item.street_address()
    info['street2'] = item.secondary_address()
    info['city'] = item.city()
    info['state'] = item.state_abbr()
    info['zip'] = item.postalcode_in_state()
    info['email'] = item.safe_email()
    info['phone'] = item.phone_number()
    info['homepage'] = item.uri()
    return info

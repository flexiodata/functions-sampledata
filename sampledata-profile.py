# ---
# name: sampledata-profile
# deployed: true
# title: Sample Data Profile
# description: Returns a list of fake profile information
# params:
# - name: count
#   type: integer
#   description: Number of fake records to return, between 0 and 10000
#   required: true
# - name: properties
#   type: array
#   description: The properties to return (defaults to all properties). See "Notes" for a listing of the available properties.
#   required: false
# returns:
# - name: uuid
#   type: string
#   description: The unique identifier for the profile
# - name: slug
#   type: string
#   description: The slug for the profile
# - name: email
#   type: string
#   description: The email address for the profile
# - name: username
#   type: string
#   description: The username for the profile
# - name: password
#   type: string
#   description: The password for the profile
# - name: first_name
#   type: string
#   description: The first name for the profile
# - name: last_name
#   type: string
#   description: The last name for the profile
# - name: name
#   type: string
#   description: The name for the profile
# - name: street1
#   type: string
#   description: The primary street address for the profile
# - name: street2
#   type: string
#   description: The secondary street address for the profile
# - name: city
#   type: string
#   description: The city of the address for the profile
# - name: state
#   type: string
#   description: The state of the address for the profile
# - name: zip
#   type: string
#   description: The zipcode of the address for the profile
# - name: phone
#   type: string
#   description: The phone number for the profile
# - name: homepage
#   type: string
#   description: The homepage for the profile
# examples:
# - '1, "name, email"'
# - '10, "name, email, phone, homepage"'
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
    property_map['uuid'] = lambda faker: faker.uuid4()
    property_map['slug'] = lambda faker: faker.slug()
    property_map['email'] = lambda faker: faker.safe_email()
    property_map['username'] = lambda faker: faker.user_name()
    property_map['password'] = lambda faker: faker.password()
    property_map['first_name'] = lambda faker: faker.first_name()
    property_map['last_name'] = lambda faker: faker.last_name()
    property_map['name'] = lambda faker: faker.name()
    property_map['street1'] = lambda faker: faker.street_address()
    property_map['street2'] = lambda faker: faker.secondary_address()
    property_map['city'] = lambda faker: faker.city()
    property_map['state'] = lambda faker: faker.state_abbr()
    property_map['zip'] = lambda faker: faker.postalcode_in_state()
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


import logging
from json import JSONDecodeError

import jsonschema
from jsonschema import validate
from requests import Response

from utilities import custom_logger
from utilities.api_utils.requests import Client


class ApiBase:
    def __init__(self):
        self.client = Client

    log = custom_logger.customlogger(logging.DEBUG)

    def structure(self, response: Response) -> Response:
        """
        Tries to structure response and adds a data attribute to response object with the json response of API

        :param response: response
        :return: validated and modified response with "data" field
        """
        self.log.info(f"Structuring the response and a data field")

        try:
            self.log.info(f"Response: {response.json()}")
            data = response.json()
        except JSONDecodeError:
            self.log.error(f"The response is not JSON, returning just the response")
            data = []

        response.data = data
        self.log.info(response.data)
        self.log.info(f"Response Successfully Structured")
        return response

    def validate_response_json(self, json_data_to_validate, schema_to_validate_against):
        """
        Validates the Json data against the schema

        :param json_data_to_validate:
        :param schema_to_validate_against:
        :return: True if validated successfully
        """
        try:
            validate(instance=json_data_to_validate, schema=schema_to_validate_against)
            self.log.info("Response JSON Successfully Validated")
        except jsonschema.exceptions.ValidationError as err:
            self.log.error(f"Response JSON not Validated due to error: {err}")
            assert False
        return True

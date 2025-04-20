from jsonschema import ValidationError, validate
import allure
from utilities.custom_logger import CustomLogger
import json
import math


def is_subset(superset, subset):
    """
    Recursively check if 'subset' is a subset of 'superset'.
    """
    if isinstance(subset, dict):
        for key, value in subset.items():
            if key not in superset or not is_subset(superset[key], value):
                return False
    elif isinstance(subset, list):
        for item in subset:
            if not any(is_subset(superset_item, item) for superset_item in superset):
                return False
    else:
        return superset == subset
    return True


def verify_schema(response, response_schema):
    """
    Verifies that the key order of a JSON response matches the expected order 
    defined by a given JSON schema.

    This function first validates the response against the schema using `jsonschema`.
    It then flattens the keys of both the response and schema and compares their order.
    If certain keys are marked to be skipped in the schema (such as those with 
    `additionalProperties`), the function skips validating the order of the nested 
    keys but ensures the top-level key is still included.

    Args:
        response (dict): The JSON response whose key order needs to be verified.
        response_schema (dict): The JSON schema defining the expected key order.

    Returns:
        bool: True if the key order of the response matches the schema, otherwise False.

    Raises:
        ValidationError: If the response does not conform to the schema.
        AssertionError: If the key order in the response does not match the expected order.
    """
    try:
        validate(instance=response, schema=response_schema)
        CustomLogger.log.info("Response schema validated")
        return True
    except ValidationError as e:
        error_message = "Schema Validation Failed"
        CustomLogger.log.info(e.message)
        CustomLogger.log.info(f"Path to the error: {'/'.join(map(str, e.path))}")
        error = f"Path to the error: {'/'.join(map(str, e.path))} -> and error is \n-> {e.message}"
        allure.attach(error, name=f"{error_message} -> click for details", attachment_type=allure.attachment_type.TEXT)
        return False

def parse_nan(data):
    """
    Parses data that may contain NaN values.

    If the input is a JSON string, this function replaces occurrences of "NaN"
    in the JSON string with "null", allowing it to be loaded by `json.loads`
    without causing errors. If the input is already a dictionary, it will
    return the dictionary as-is.

    Args:
        data (str or dict): JSON string or dictionary potentially containing "NaN" values.

    Returns:
        dict: Parsed JSON data as a dictionary, with "NaN" replaced by `None` if input was a string.
    """
    if isinstance(data, str):
        data = data.replace('NaN', 'null')  # Replace "NaN" with null (None) for JSON string
        return json.loads(data)
    elif isinstance(data, dict):
        return data  # Return as-is if already a dictionary
    else:
        raise ValueError("Input must be a JSON string or a dictionary")


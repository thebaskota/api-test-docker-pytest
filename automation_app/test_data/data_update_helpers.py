from test_data.read_excel_api_testdata import get_value_by_attribute, get_value_by_attribute_as_json
import re
import pandas as pd

def process_config_value(value):
    if pd.isnull(value):
        return None
    
    str_value = str(value)
    
    # Handle pattern matches
    pattern_match = re.match(r'(int|num|str)\[(\d+)\]', str_value)
    if pattern_match:
        type_, num = pattern_match.groups()
        return int(num) if type_ == 'int' else num  # num is already str
    
    # Handle boolean cases (using set for O(1) lookups)
    if str_value.lower() in {'true', 'false'}:
        return str_value.lower() == 'true'
    
    return value

def update_payload_with_config(payload, config_df):
    """
    Update the payload dictionary by replacing keys starting with '#' with values from the DataFrame.

    Parameters:
    - payload (dict): The payload dictionary to be updated.
    - config_df (pandas.DataFrame): The DataFrame containing the configuration data.

    Returns:
    - dict: The updated payload dictionary.
    """
    updated_payload = payload.copy()  # Create a copy to avoid modifying the original payload

    for key, value in payload.items():
        if isinstance(value, str):
            if value.startswith('##'):
                attribute_name = value[2:]  # Remove the leading '##'
                replacement_value = get_value_by_attribute(config_df, attribute_name)
                processed_replacement_value = process_config_value(replacement_value)
                if replacement_value is not None:
                    updated_payload[key] = processed_replacement_value

    return updated_payload

def get_value_from_response(path, response):
    """
    Retrieve a value from a nested dictionary or list structure using a dot-separated path.

    This function navigates through a nested `response` dictionary (which may also contain lists)
    according to the dot-separated `path`. It extracts the value corresponding to the given path.

    Parameters:
    path (str): A dot-separated string representing the path to the desired value in the `response`.
    response (dict or list): The nested dictionary or list from which to extract the value.

    Returns:
    any: The value found at the specified path, or `None` if the path does not exist in the response.
    
    Example:
    --------
    response = {
        'user': {
            'name': 'John Doe',
            'details': {
                'age': 30,
                'contacts': [{'type': 'email', 'value': 'john@example.com'}]
            }
        }
    }
    
    path = 'user.details.contacts.0.value'
    value = get_value_from_response(path, response)
    
    # The value will be 'john@example.com'
    """
    # print(f"Processing path: {path}")
    parts = path.split('.')
    current_value = response
    for part in parts:
        # print(f"Current part: {part}")

        if isinstance(current_value, list):
            # print("Current value is a list")
            # Assuming you need to get the first item of the list if part is not a number
            if part.isdigit():
                current_value = current_value[int(part)]
            else:
                current_value = current_value[0]
        else:
            current_value = current_value.get(part)
        
        # print("=========")
        # print(f"Current value after {part}: {current_value}")
        # print("=========")
        
        if current_value is None:
            # print(f"Could not find {part} in the current level of the response.")
            break
        
    return current_value

def update_payload_with_prev_response(payload, response):
    """
    Update a payload dictionary by replacing placeholder values with corresponding values from a previous response.

    This function searches for string values in the `payload` dictionary that start with `$$`, 
    treating these as paths to values within the `response` dictionary. It replaces the placeholders 
    with the actual values extracted from the response.

    Parameters:
    payload (dict): A dictionary that may contain placeholder strings (starting with `$$`) representing paths.
    response (dict or list): The nested dictionary or list containing the data from which to extract values.

    Returns:
    dict: The updated payload dictionary with placeholders replaced by actual values from the response.
    
    Example:
    --------
    payload = {
        'userId': '$$.user.id',
        'userDetails': {
            'name': 'John Doe',
            'email': '$$.user.email'
        }
    }
    
    response = {
        'user': {
            'id': '12345',
            'email': 'john@example.com'
        }
    }
    
    updated_payload = update_payload_with_prev_response(payload, response)
    
    # The updated_payload will be:
    # {
    #     'userId': '12345',
    #     'userDetails': {
    #         'name': 'John Doe',
    #         'email': 'john@example.com'
    #     }
    # }
    """
    for key, value in payload.items():
        if isinstance(value, str) and value.startswith('$$'):
            # print(f"key {key}")
            # Remove $$ from the key to form the path
            path = value[2:]
            # Update the payload with the corresponding value from the response
            payload[key] = get_value_from_response(path, response)
        elif isinstance(value, dict):
            update_payload_with_prev_response(value, response)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    update_payload_with_prev_response(item, response)
    
    return payload



def update_payload_with_response(payload, response):
    """
    Update a payload dictionary by replacing placeholder values with corresponding values from a previous response.

    This function searches for string values in the `payload` dictionary that start with `$#`, 
    treating these as paths to values within the `response` dictionary. It replaces the placeholders 
    with the actual values extracted from the response.

    Parameters:
    payload (dict): A dictionary that may contain placeholder strings (starting with `$#`) representing paths.
    response (dict or list): The nested dictionary or list containing the data from which to extract values.

    Returns:
    dict: The updated payload dictionary with placeholders replaced by actual values from the response.
    """
    for key, value in payload.items():
        if isinstance(value, str) and value.startswith('$#'):
            # print(f"key {key}")
            # Remove $# from the key to form the path
            path = value[2:]
            # Update the payload with the corresponding value from the response
            payload[key] = get_value_from_response(path, response)
        elif isinstance(value, dict):
            update_payload_with_prev_response(value, response)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    update_payload_with_prev_response(item, response)
    
    return payload
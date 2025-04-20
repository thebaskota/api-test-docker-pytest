import os.path
import pandas as pd
import json

def get_total_test_cases_excel(df: pd.DataFrame) -> int:
    """
    Count the total number of test cases in the given DataFrame.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the test cases.

    Returns:
    --------
    int
        The total number of test cases.
    """
    # Assuming each row in the DataFrame represents one test case
    return df.shape[0]

def get_attribute_as_json_from_excel(df: pd.DataFrame, testcase_number: int, attribute: str) -> dict:
    """
    Return the attribute as json for a given test case number from the DataFrame.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the test cases.
    
    testcase_number : int
        The test case number (0-indexed) to retrieve the attribute for.
    
    attribute : str
        The attribute to retrieve for the specified test case. Examples include 'api_name', 
        'request_type', 'payload', 'expected_outcome', and 'test_name'.

    Returns:
    --------
    dict
        The attribute for the specified test case as a dictionary.
    """
    try:
        # Retrieve the attribute for the specified test case
        attribute_str = df.iloc[testcase_number][attribute]
        # Convert the JSON string to a dictionary
        if pd.isna(attribute_str):
            return None
        attribute_dict = json.loads(attribute_str)
        return attribute_dict
    except IndexError:
        raise ValueError(f"Test case number {testcase_number} is out of range.")
    except KeyError:
        raise ValueError(f"Payload not found for test case number {testcase_number}.")
    except json.JSONDecodeError:
        raise ValueError(f"Payload for test case number {testcase_number} is not a valid JSON.")
    

def get_attribute_from_excel(df: pd.DataFrame, testcase_number: int, attribute: str) -> str:
    """
    Return the specified attribute for a given test case number from the DataFrame.

    Parameters:
    -----------
    df : pd.DataFrame
        The DataFrame containing the test cases.
    
    testcase_number : int
        The test case number (0-indexed) to retrieve the attribute for.
    
    attribute : str
        The attribute to retrieve for the specified test case. Examples include 'api_name', 
        'request_type', 'payload', 'expected_outcome', and 'test_name'.

    Returns:
    --------
    str
        The value of the specified attribute for the given test case.

    Raises:
    -------
    ValueError
        If the test case number is out of range or the specified attribute is not found.
    """
    try:
        # Retrieve the attribute specified for the specified test case
        attribute_value = df.iloc[testcase_number][attribute]
        return attribute_value
    except IndexError:
        raise ValueError(f"Test case number {testcase_number} is out of range.")
    except KeyError:
        raise ValueError(f"Attribute '{attribute}' not found for test case number {testcase_number}.")


def get_value_by_attribute(df, attribute):
    """
    Get the value corresponding to a specified attribute from the DataFrame.
    The excel sheet needs to be in the format - 
    attribute     value

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the data.
    - attribute (str): The attribute for which to get the value.

    Returns:
    - str: The value corresponding to the specified attribute.
    """
    try:
        value = df.loc[df['attribute'] == attribute, 'value'].values[0]
        return value
    except IndexError:
        return None

def get_value_by_attribute_as_json(df, attribute):
    """
    Get the value corresponding to a specified attribute from the DataFrame as json.
    The excel sheet needs to be in the format - 
    attribute     value

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the data.
    - attribute (str): The attribute for which to get the value.

    Returns:
    - str: The value corresponding to the specified attribute.
    """
    try:
        value = df.loc[df['attribute'] == attribute, 'value'].values[0]
        # Convert the JSON string to a dictionary
        if pd.isna(value):
            return None
        attribute_dict = json.loads(value)
        return value
    except IndexError:
        return None
    except json.JSONDecodeError:
        raise ValueError(f"Schema in Schema_config is not a valid JSON.")
    

def group_test_sequences(df):
    """
    Groups test cases into sequences based on the 'use_next' column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing test cases with 'test_number' and 'use_next' columns.

    Returns:
        List[List[str]]: A list of sequences, where each sequence is a list of test numbers.
    """
    sequences = []  # List to store sequences of test cases
    visited = set()  # Set to track already processed test numbers
    
    for index, row in df.iterrows():
        # Skip the test case if it's already been processed
        if row['test_number'] in visited:
            continue
        
        sequence = []  # Initialize a new sequence
        current_step = row['test_number']  # Start with the current test_number
        
        # Traverse through the sequence based on 'use_next'
        while current_step:
            sequence.append(current_step)  # Add the current test number to the sequence
            visited.add(current_step)  # Mark the current test number as visited

            # Retrieve the next step from the 'use_next' column
            next_row = df[df['test_number'] == current_step]
            current_step = (
                next_row['use_next'].values[0] 
                if not next_row.empty and pd.notna(next_row['use_next'].values[0]) 
                else None
            )
        
        sequences.append(sequence)  # Add the completed sequence to the list of sequences
    
    return sequences  # Return all grouped sequences
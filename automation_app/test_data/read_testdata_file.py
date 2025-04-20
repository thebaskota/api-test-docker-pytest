import json
import os
import pandas as pd

def read_excel_file_data(test_data_file_name='test_data.xlsx', sheet_name=None):
    """
    Read test data from the specified sheet of the Excel file.

    Parameters:
    - test_data_file_name (str, optional): The name of the test data file. Default is 'test_data.xlsx'.
    - sheet_name (str or None, optional): The name of the sheet to read. If None, all sheets are read into a dictionary.
      Default is None.

    Returns:
    - pandas.DataFrame or dict of pandas.DataFrame: DataFrame containing the data from the specified sheet
      or a dictionary of DataFrames if sheet_name is None.

    This function reads test data from the specified Excel file and sheet.
    If no file name is provided, it defaults to 'test_data.xlsx'.
    It returns a pandas DataFrame containing the data from the specified sheet,
    or a dictionary of DataFrames if no sheet name is specified.
    """
    test_data_file = test_data_file_name
    test_data_folder = os.path.dirname(__file__)
    test_data_excel_file = os.path.join(test_data_folder, test_data_file)

    df = pd.read_excel(test_data_excel_file, sheet_name=sheet_name)
    return df

def read_json_data(json_file_name='test_data_tester.json'):
    """
    Read data from a JSON file with comprehensive error handling using standard exceptions.

    Parameters:
    - json_file_name (str, optional): The name of the JSON file. Default is 'data.json'.

    Returns:
    - dict or list: The parsed JSON data as Python objects.

    Raises:
    - FileNotFoundError: If the file doesn't exist
    - PermissionError: If file access is denied
    - IsADirectoryError: If path is a directory
    - json.JSONDecodeError: If JSON is invalid
    - OSError: For other filesystem-related errors
    """
    file_path = os.path.join(os.path.dirname(__file__), json_file_name)
    
    # Check basic file attributes first
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    if not os.path.isfile(file_path):
        raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except PermissionError:
        raise PermissionError(f"Permission denied reading file: {file_path}")
    except json.JSONDecodeError as e:
        # Enhance the JSON decode error message
        raise json.JSONDecodeError(
            msg=f"Invalid JSON in file {file_path}: {e.msg}",
            doc=e.doc,
            pos=e.pos
        )
    except OSError as e:
        raise OSError(f"Error reading file {file_path}: {str(e)}")
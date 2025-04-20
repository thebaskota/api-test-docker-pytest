import json
import logging
import time
import pytest
import allure
import pandas as pd

from api_fixtures.rest_api import RestApi
from test_data.data_update_helpers import update_payload_with_prev_response, update_payload_with_response
from utilities.data_verification_utils import is_subset, verify_schema
from test_data.read_testdata_file import read_excel_file_data
from test_data.read_settings_file import get_rest_api_settings
from test_data.read_excel_api_testdata import group_test_sequences, get_attribute_from_excel, get_attribute_as_json_from_excel
from utilities.api_utils.api_test_status import ApiTestStatus
from utilities.custom_logger import CustomLogger, customlogger

test_data_file = get_rest_api_settings("TESTDATA_FILE")

# finding total number of cases
testcases_sheet_name = "testcases"
df = read_excel_file_data(test_data_file, sheet_name=testcases_sheet_name)

# Helper function to extract test data row as a dictionary
def extract_test_data(n):
    return {
        "test_number": get_attribute_from_excel(df, n, "test_number"),
        "use_next": get_attribute_from_excel(df, n, "use_next"),
        "delay_before_test_sec": get_attribute_from_excel(df, n, "delay_before_test_sec"),
        "use_creds": get_attribute_as_json_from_excel(df, n, "use_creds"),
        "base_url": get_attribute_from_excel(df, n, "base_url"),
        "api_name": get_attribute_from_excel(df, n, "api_name"),
        "request_type": get_attribute_from_excel(df, n, "request_type"),
        "test_group_name": get_attribute_from_excel(df, n, "test_group_name"),
        "test_step_name": get_attribute_from_excel(df, n, "test_step_name"),
        "payload": get_attribute_as_json_from_excel(df, n, "payload"),
        "attachment": get_attribute_from_excel(df, n, "attachment"),
        "test_type": get_attribute_from_excel(df, n, "test_type"),
        "response_schema": get_attribute_as_json_from_excel(df, n, "response_schema"),
        "expected_outcome": get_attribute_as_json_from_excel(df, n, "expected_outcome"),
        "un_expected_outcome": get_attribute_as_json_from_excel(df, n, "un_expected_outcome"),
        "expected_response_header": get_attribute_as_json_from_excel(df, n, "expected_response_header"),
        "skip_test": get_attribute_from_excel(df, n, "skip_test")
    }

# Group test cases into sequences and log the total number of sequences
sequences = group_test_sequences(df)
CustomLogger.log.info(f"Total test Cases: {len(sequences)}")


@pytest.fixture
def generate_test_sequence(request):
    """
    Pytest fixture to generate test data for a given test sequence.

    Args:
        request: The pytest request object containing the sequence as a parameter.

    Returns:
        List[Dict]: A list of dictionaries containing the test data for each step in the sequence.
    """
    sequence = request.param  # Retrieve the sequence from the request parameter
    test_data = []  # Initialize an empty list to store test data for the sequence
    
    with allure.step("Generating Testdata:"):
        for step in sequence:
            # Log the processing of the current step
            TestExcelTestcases.log.info(f"Processing step: {step}")
            
            # Check if the step exists in the DataFrame
            filtered_df = df[df['test_number'] == step]
            if filtered_df.empty:
                pytest.fail(f"Step {step} not found in the Excel sheet")  # Fail the test if the step is missing

            # Get the row index for the current step
            row_index = df[df['test_number'] == step].index[0]
            
            # Extract test data for the current step
            data = extract_test_data(row_index)
            
            # Skip the test if the 'skip_test' flag is set
            if data['skip_test'] == "skip":
                allure.dynamic.title(f"{step} :: {data['test_group_name']} - Skip flag true")
                pytest.skip(f"Step {step} skipped due to skip flag.")

            # Log the extracted test data as an Allure step
            allure.step(f"Extracted Test Data for Step: {step}")
            test_data.append(data)  # Append the extracted test data to the list
    
    return test_data  # Return the list of test data for the sequence

class TestExcelTestcases:
    log = customlogger(logging.DEBUG)

    @pytest.fixture(autouse=True)
    def class_setup(self, request):
        self.rest_api = RestApi()
        self.api_test_status = ApiTestStatus()                   
        

    def perform_api_request(self, test_data, auth_header, base_url):
        """
        Performs the API request, validates the result, and returns response according to the test data provided.
        """
        with allure.step(f"Running Test: {test_data['test_step_name']}"):
            self.log.info(f"::: test -> {test_data['test_step_name']}")
            self.log.info(f"auth_header = {auth_header}")

            if not pd.isna(test_data['delay_before_test_sec']):
                int_delay = int(round(test_data['delay_before_test_sec']))
                self.log.info(f"Waiting for -> {int_delay}")
                time.sleep(int_delay)
            
            if not pd.isna(test_data['attachment']):
                response = self.rest_api.upload_attachment_api_request(
                                base_url=base_url,
                                endpoint=test_data['api_name'],
                                method=test_data['request_type'],
                                header=auth_header,
                                request_body=test_data['payload'],
                                attachment_name=test_data['attachment']
                            )
                
            else: 
                response = self.rest_api.perform_api_request(
                                base_url=base_url,
                                endpoint=test_data['api_name'],
                                method=test_data['request_type'],
                                header=auth_header,
                                request_body=test_data['payload']
                            )

            # Response schema test
            if pd.notna(test_data['response_schema']):
                response_schema_comparision_result = verify_schema(response.data, test_data['response_schema'])
                if not response_schema_comparision_result:
                    allure.attach(json.dumps(test_data['response_schema'], indent=4), name="Expected Response Schema", attachment_type=allure.attachment_type.JSON)
                self.api_test_status.soft_assert_true(
                    response_schema_comparision_result,
                    "The response adheres to the expected schema",
                    "Schema Validation Check"
                )

            # Expected outcome test
            if pd.notna(test_data['expected_outcome']):
                expected_outcome_is_subset_result = is_subset(response.data, test_data['expected_outcome'])
                if not expected_outcome_is_subset_result:
                    allure.attach(json.dumps(test_data['expected_outcome'], indent=4), name="Expected Outcome", attachment_type=allure.attachment_type.JSON)
                self.api_test_status.soft_assert_true(
                    expected_outcome_is_subset_result,
                    "The response values align with the expected outcome",
                    "Validation of expected response values"
                )

            # Unexpected outcome test
            if pd.notna(test_data['un_expected_outcome']):
                un_expected_outcome_is_subset_result = not is_subset(response.data, test_data['un_expected_outcome'])
                if un_expected_outcome_is_subset_result:
                    allure.attach(json.dumps(test_data['un_expected_outcome'], indent=4), name="Unexpected Outcome", attachment_type=allure.attachment_type.JSON)
                self.api_test_status.soft_assert_true(
                    un_expected_outcome_is_subset_result,
                    "The response does not include unexpected values",
                    "Validation against unexpected outcomes"
                )
            
            # Expected response header test
            if pd.notna(test_data['expected_response_header']):
                try:
                    response_headers = dict(response.headers)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Failed to response headers: {e}", pytrace=False)
                allure.attach(json.dumps(response_headers, indent=4), name="Actual Response Headers", attachment_type=allure.attachment_type.JSON)
                expected_response_header_is_subset_result = is_subset(response_headers, test_data['expected_response_header'])
                if not expected_response_header_is_subset_result:
                    allure.attach(json.dumps(test_data['expected_response_header'], indent=4), name="Expected Response Header", attachment_type=allure.attachment_type.JSON)
                self.api_test_status.soft_assert_true(
                    expected_response_header_is_subset_result,
                    "The response header values align with the expected response headers",
                    "Validation of expected response header"
                )

            self.api_test_status.assert_final(test_data['test_group_name'])
            return response.data

    @pytest.mark.parametrize("generate_test_sequence", group_test_sequences(df), indirect=True)
    def test_exceltestcases(self, generate_test_sequence):
        """
        Tests Excel Test cases APIs according to the Excel sheet.

        This test runs through a sequence of API requests defined in an Excel sheet.
        Each sequence represents a series of dependent API calls, where the payload
        for each step may depend on the response from the previous step.
        """
        sequence_data = generate_test_sequence  # Retrieve test sequence data from the fixture
        response = {}  # Initialize an empty dictionary to store the response from each API call 
        response_previous = {} # Initialize an empty dictionary to store the response from Previous API call
        auth_header = sequence_data[0]['use_creds']
        
        allure.dynamic.title(f"{sequence_data[0]['test_group_name']}")
        base_url = sequence_data[0]['base_url'] # since base url needs to be entered only at first test 

        # Iterate over each step in the test sequence
        for step_data in sequence_data:
            # Update the current step's payload with data from the previous API response
            step_data['payload'] = update_payload_with_response(
                payload=step_data['payload'],
                response=response_previous)
            step_data['payload'] = update_payload_with_prev_response(
                payload=step_data['payload'],
                response=response)
            
            response_previous = response
            # Perform the API request for the current step and store the response
            response = self.perform_api_request(step_data, auth_header, base_url)
            self.log.info(f"api name is {step_data['api_name']}")
            
        # Log a message indicating the test sequence is complete
        self.log.info(f"<------Test {sequence_data[0]['test_group_name']} Complete --------->")
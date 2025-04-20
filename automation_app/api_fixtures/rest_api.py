import logging
from requests import Response
import allure
import json
import time
import os

from api_fixtures.api_base import ApiBase
from load_config import ATTACHMENT_PATH
from test_data.read_settings_file import get_rest_api_settings
from utilities import custom_logger

class RestApi(ApiBase):
    log = custom_logger.customlogger(logging.DEBUG)

    def __init__(self):
        super().__init__()
        self.url = get_rest_api_settings("url")

    def perform_api_request(self,endpoint: str, method: str, request_body: dict, base_url: str="use_env_url", header=None) -> Response:
        """
        Send an HTTP request to the specified workflow endpoint.

        This method allows sending an HTTP request to a given endpoint with the specified 
        request method, body, and optional headers. The endpoint is part of the URL where 
        the request is sent. The method should be a valid HTTP method like 'GET', 'POST', etc.

        Parameters:
        -----------
        endpoint : str
            The specific API endpoint to which the request is to be sent. It is appended 
            to the base URL fetched from the settings.
        
        method : str
            The HTTP method to use for the request. Examples include 'GET', 'POST', 'PUT', 'DELETE', etc.
        
        request_body : dict
            The JSON body to be included in the request. This is typically used for 'POST' and 'PUT' requests.

        base_url : str, optional
            The specific API base to which the request is to be sent. It is appended 
            to the endpoint passed in the function.if left empty, the base URL fetched from the settings.
        
        header : dict, optional
            Additional headers to include in the request. If not provided, defaults to 
            {'Content-Type': 'application/json'}.

        Returns:
        --------
        Response
            The response object returned by the requests library, structured appropriately 
            by the `structure` method. Returns `None` if the request fails.
        """
        header = header if header is not None else {"Content-Type": "application/json"}
        if base_url == "use_env_url":
            full_url = f"{self.url}/{endpoint}"
        else: 
            full_url = f"{base_url}/{endpoint}"

        self.log.info(f"Sending {method} Request to Endpoint at {full_url}")
        self.log.info(f"Request Payload: {request_body}")
        allure.attach(json.dumps(request_body, indent=4), name="Request Payload", attachment_type=allure.attachment_type.JSON)
        try:
            start_time = time.time()
            response = self.client.request(
                method=method,
                url=full_url,
                json=request_body,
                headers=header,
            )
            end_time = time.time()
            response_time = end_time - start_time
            api_response_time = f"API Response Time = {response_time} Seconds"
            response_structured = self.structure(response)
            self.log.info(response)

            allure.attach(json.dumps(response_structured.data, indent=4), name="Response Data", attachment_type=allure.attachment_type.JSON)
            allure.attach("", name=api_response_time, attachment_type=allure.attachment_type.TEXT)
            self.log.info(f"Response - {response_structured.data}")
            return response_structured
        except Exception as e:
            self.log.error(f"Request failed: {e}")
            return None
    
    def upload_attachment_api_request(self, endpoint: str, method: str, request_body: dict, 
                               attachment_name: str, base_url: str = "use_env_url", 
                               header=None) -> Response:
        """
        Send an HTTP request to upload an attachment to the specified endpoint.

        Parameters:
        -----------
        endpoint : str
            The specific API endpoint to which the request is to be sent.
        method : str
            The HTTP method to use for the request (typically POST).
        request_body : dict
            The JSON body to be included in the request.
        attachment_name : str
            The name of the file to be uploaded.
        base_url : str, optional
            The base URL for the API. Defaults to environment URL if "use_env_url".
        header : dict, optional
            Additional headers to include in the request.

        Returns:
        --------
        Response
            The response object returned by the requests library.
        """
        header = header if header is not None else {"Content-Type": "application/json"}
        if base_url == "use_env_url":
            full_url = f"{self.url}/{endpoint}"
        else: 
            full_url = f"{base_url}/{endpoint}"

        # Attachment path
        attachment_path = os.path.join(ATTACHMENT_PATH, attachment_name)

        self.log.info(f"Sending {method} Request to Endpoint at {full_url}")
        self.log.info(f"Request Payload: {request_body}")
        self.log.info(f"Attachment Path: {attachment_path}")

        allure.attach(json.dumps(request_body, indent=4), name="Request Payload", 
                    attachment_type=allure.attachment_type.JSON)

        try: 
            # Determine file type and prepare appropriate MIME type
            if attachment_name.endswith(".docx"):
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif attachment_name.endswith(".pdf"):
                mime_type = "application/pdf"
            else:
                mime_type = "application/octet-stream"

            with open(attachment_path, "rb") as file:
                file_content = file.read()

            # Prepare multipart form-data
            files = {
                "file": (attachment_name, file_content, mime_type),
                "data": (None, json.dumps(request_body), "application/json")
            }

            # Update headers for multipart form-data
            upload_headers = header.copy()
            if "Content-Type" in upload_headers:
                del upload_headers["Content-Type"]

            start_time = time.time()
            response = self.client.request(
                method=method,
                url=full_url,
                headers=upload_headers,
                files=files
            )
            end_time = time.time()
            response_time = end_time - start_time
            api_response_time = f"API Response Time = {response_time} Seconds"
            response_structured = self.structure(response)

            allure.attach(json.dumps(response_structured.data, indent=4), 
                        name="Response Data", attachment_type=allure.attachment_type.JSON)
            allure.attach("", name=api_response_time, attachment_type=allure.attachment_type.TEXT)
            
            self.log.info(f"Response json: {response_structured.data}")
            self.log.info(f"API response time: {api_response_time}")
            self.log.info(f"Status Code: {response.status_code}")
            self.log.info(f"Response Text: {response.text}")
            
            return response_structured

        except FileNotFoundError as e:
            self.log.error(f"Attachment file not found: {e}")
            return None
        except Exception as e:
            self.log.error(f"Request failed: {e}")
            return None

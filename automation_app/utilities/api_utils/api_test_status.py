import logging
import allure
import utilities.custom_logger as custom_logger

"""
A class for checkpoints and logging them as well as assertion
"""


class ApiTestStatus:
    log = custom_logger.customlogger(logging.DEBUG)

    def __init__(self):
        self.result_list = []

    def soft_assert_true(self, result, result_message, checkpoint_name=''):
        """
        Soft Assert for false
        logs everything for false soft assertions.
        Should only be called if the test should continue even if the checkpoint fails.

        :param result: result of a test, should be true or false
        :param result_message: the message to be logged
        :param checkpoint_name: the checkpoint_name to be logged 
        :return: None
        """
        try:
            if result is not None:
                if result:
                    self.result_list.append("PASS")
                    self.log.info(f"### VERIFICATION SUCCESSFUL :: {result_message}")
                    allure.attach(result_message, name=f"Checkpoint Passed -> {checkpoint_name}", attachment_type=allure.attachment_type.TEXT)
                else:
                    self.result_list.append("FAIL")
                    self.log.error(f"### VERIFICATION FAILED :: {result_message}")
                    allure.attach(result_message, name=f"Checkpoint Failed -> {checkpoint_name}", attachment_type=allure.attachment_type.TEXT)
            else:
                self.result_list.append("FAIL")
                self.log.error(f"### VERIFICATION FAILED :: {result_message}")
                allure.attach(result_message, name=f"Checkpoint Failed -> {checkpoint_name}", attachment_type=allure.attachment_type.TEXT)
        except Exception as e:
            self.result_list.append("FAIL")
            self.log.error(f"### EXCEPTION OCCURRED :: {e}")
            allure.attach(result_message, name=f"Checkpoint Failed -> {checkpoint_name}", attachment_type=allure.attachment_type.TEXT)

    def assert_true(self, result, result_message):
        """
        Hard Assert for True
        Marks the intermediate result of a Positive verification point in the test case.
        call this for a Positive hard assert in the test

        :param result: result of a test, should be true or false
        :param result_message: the message to be logged
        :return: None
        """
        if result:
            self.log.info(f"### VERIFICATION SUCCESSFUL :: {result_message}")
            allure.attach(result_message, name="Assertion Passed", attachment_type=allure.attachment_type.TEXT)
            assert True
        else:
            self.log.error(f"### VERIFICATION FAILED :: {result_message}")
            allure.attach(result_message, name="Assertion Failed", attachment_type=allure.attachment_type.TEXT)
            assert False, result_message

    def soft_assert_false(self, result, result_message,  checkpoint_name=''):
        """
        Soft Assert for false
        logs everything for false soft assertion.
        Should only be called if the test should continue even if the checkpoint fails.

        :param result: result of a test, should be true or false
        :param result_message: the message to be logged
        :param checkpoint_name: the checkpoint_name to be logged 
        :return: None
        """
        try:
            if result is not None:
                if result is False:
                    self.result_list.append("PASS")
                    self.log.info(f"### VERIFICATION SUCCESSFUL :: {result_message}")
                    allure.attach(result_message, name=f"Checkpoint Passed -> {checkpoint_name}", attachment_type=allure.attachment_type.TEXT)
                else:
                    self.result_list.append("FAIL")
                    self.log.error(f"### VERIFICATION FAILED :: {result_message}")
                    allure.attach(result_message, name=f"Checkpoint Failed -> {checkpoint_name}", attachment_type=allure.attachment_type.TEXT)
            else:
                self.result_list.append("FAIL")
                self.log.error(f"### VERIFICATION FAILED :: {result_message}")
                allure.attach(result_message, name=f"Checkpoint Failed -> {checkpoint_name}", attachment_type=allure.attachment_type.TEXT)
        except Exception as e:
            self.result_list.append("FAIL")
            self.log.error(f"### EXCEPTION OCCURRED :: {e}")
            allure.attach(result_message, name=f"Checkpoint Failed -> {checkpoint_name}", attachment_type=allure.attachment_type.TEXT)

    def assert_false(self, result, result_message):
        """
        Hard Assert for False
        Marks the intermediate result of a negative verification point in the test case.
        call this for a negative hard assert in the test

        :param result: result of a test, should be true or false
        :param result_message: the message to be logged
        :return: None
        """
        if result is False:
            self.log.info(f"### VERIFICATION SUCCESSFUL :: {result_message}")
            allure.attach(result_message, name="Assertion Passed", attachment_type=allure.attachment_type.TEXT)
            assert True
        else:
            self.log.error(f"### VERIFICATION FAILED :: {result_message}")
            allure.attach(result_message, name="Assertion Failed", attachment_type=allure.attachment_type.TEXT)
            assert False, result_message

    def assert_final(self, result_message):
        """
        Marks the final result of the verification point in a test case for soft asserts.
        This needs to be called at last in a test case which uses soft assert.

        :param result_message: the message to be logged
        :return: None
        """
        if "FAIL" in self.result_list:
            self.result_list.clear()
            self.log.error(f"### TEST FAILED :: {result_message}")
            allure.attach("", name=f"Test Failed -> {result_message}", attachment_type=allure.attachment_type.TEXT)
            assert False, result_message
        else:
            self.result_list.clear()
            self.log.info(f"### TEST PASSED :: {result_message}")
            allure.attach("", name=f"Test Pass -> {result_message}", attachment_type=allure.attachment_type.TEXT)
            assert True
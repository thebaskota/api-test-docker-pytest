import pytest
from test_data.config.config import SettingsUpdaterLogger
from utilities.custom_logger import CustomLogger

@pytest.fixture(scope="session", autouse=True)
def loading_configs():
    """Session-level fixture that automatically loads configurations and performs teardown.

    This fixture is automatically used for all tests in the session (autouse=True) and runs only once
    per test session (scope="session").

    Actions:
        - Logs the start of configuration loading at session level
        - Yields to allow test execution to proceed
        - Logs the completion of session-level teardown after all tests finish

    Logging:
        - Uses SettingsUpdaterLogger to log config loading initialization
        - Uses CustomLogger to log teardown completion

    Note:
        Since this is an autouse fixture, it will run automatically for all tests in the session
        without needing explicit reference in test functions.
    """
    SettingsUpdaterLogger.log.info("Loading Configs, session level")

    yield
    CustomLogger.log.info("Running session level tearDown")
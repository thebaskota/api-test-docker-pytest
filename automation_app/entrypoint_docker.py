import os
import subprocess
import sys
import re
import shutil
import logging
import argparse

# Set up logging
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(logs_dir, exist_ok=True)
log_file_path = os.path.join(logs_dir, 'entrypoint.log')
verbose_log_file = os.path.join(logs_dir, 'pytest_verbose_output.log')

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def install_requirements(requirements_file):
    """
    Install requirements from the specified requirements file.
    """
    command = f"pip install -r {requirements_file}"
    
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error("Error installing requirements:", e)
        sys.exit(1)

def run_tests_and_summarize(pytest_run_command):
    """
    Run pytest to execute tests and then summarize the results.
    Capture all verbose output from the pytest run and store it in a log file.
    """
    try:
        # Run the pytest command and capture both stdout and stderr
        result = subprocess.run(
            pytest_run_command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        # Extract test results from stdout
        output = result.stdout
        error_output = result.stderr

        # Parse the test results
        passed_match = re.search(r'(\d+) passed', output, re.IGNORECASE)
        failed_match = re.search(r'(\d+) failed', output, re.IGNORECASE)

        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0

        total = passed + failed

        # Write a summary to a text file
        with open("test_summary.txt", "w") as summary_file:
            summary_file.write(f"Test API\n")
            summary_file.write(f"Total Tests: {total}\n")
            summary_file.write(f"Passed Tests: {passed}\n")
            summary_file.write(f"Failed Tests: {failed}\n")
        
        # Write full verbose output to a separate log file
        with open(verbose_log_file, "w") as log_file:
            log_file.write("STDOUT:\n")
            log_file.write(output)
            log_file.write("\n\nSTDERR:\n")
            log_file.write(error_output)

        logging.info(f"Test summary written with {total} total tests: {passed} passed, {failed} failed.")
        logging.info("Verbose output captured in 'pytest_verbose_output.log'.")

    except subprocess.CalledProcessError as e:
        logging.error("Error running pytest command:", e)
        sys.exit(1)

def copy_history(src_dir, dst_dir):
    """
    Copy history directory from src_dir to dst_dir.
    """
    if os.path.exists(src_dir):
        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
        logging.info(f"Copied history from {src_dir} to {dst_dir}.")

def generate_allure_report(results_dir, report_dir, single_file=False):
    """
    Generate the Allure report.
    """
    if single_file:
        command = f"allure generate {results_dir} --clean --output {report_dir} --single-file"
    else:
        command = f"allure generate {results_dir} --clean --output {report_dir}"
    
    try:
        subprocess.run(command, shell=True, check=True)
        logging.info(f"Allure report generated at {report_dir} with single_file={single_file}.")

    except subprocess.CalledProcessError as e:
        logging.error("Error generating Allure report:", e)
        sys.exit(1)

def main(args):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the parent directory for all results and reports
    root_parent_dir = os.path.join(script_dir, 'allure_data')
    api_parent_dir = os.path.join(root_parent_dir, 'api_allure_data')
    if args.testtype == 'rest':
        parent_dir = os.path.join(api_parent_dir, 'rest')
    if args.testtype == 'graphql':
        parent_dir = os.path.join(api_parent_dir, 'graphql')

    # Define directories for Allure reports and history within the parent directory
    allure_results_dir = os.path.join(parent_dir, 'allure-results')
    allure_history_dir = os.path.join(parent_dir, 'allure-history')
    allure_report_dir = os.path.join(parent_dir, 'allure-report')

    # Delete existing allure results and report directories if they exist and are accessible
    if os.path.exists(allure_results_dir) and os.access(allure_results_dir, os.W_OK):
        shutil.rmtree(allure_results_dir)
        logging.info(f"Deleted directory: {allure_results_dir}")
    else:
        logging.warning(f"Cannot delete {allure_results_dir}: Directory does not exist or lacks write permission.")

    if os.path.exists(allure_report_dir) and os.access(allure_report_dir, os.W_OK):
        shutil.rmtree(allure_report_dir)
        logging.info(f"Deleted directory: {allure_report_dir}")
    else:
        logging.warning(f"Cannot delete {allure_report_dir}: Directory does not exist or lacks write permission.")

    # Ensure directories exist
    os.makedirs(allure_results_dir, exist_ok=True)
    os.makedirs(allure_history_dir, exist_ok=True)
    os.makedirs(allure_report_dir, exist_ok=True)

    # Copy the previous history to the new allure-results directory before running tests
    copy_history(os.path.join(allure_history_dir, 'history'), os.path.join(allure_results_dir, 'history'))

    # Run the pytest command and summarize results
    if args.testtype == 'rest':
        pytest_run_command = "pytest tests/test_api/test_rest_api --alluredir=" + allure_results_dir
    if args.testtype == 'graphql':
        pytest_run_command = "pytest tests/test_graphql --alluredir=" + allure_results_dir
    run_tests_and_summarize(pytest_run_command)

    # Generate the full Allure report
    generate_allure_report(allure_results_dir, allure_report_dir)

    # Check if history is generated and copy it back for future runs
    generated_history_dir = os.path.join(allure_report_dir, 'history')
    history_src_dir = os.path.join(allure_history_dir, 'history')
    if os.path.exists(generated_history_dir):
        copy_history(generated_history_dir, history_src_dir)
    else:
        logging.warning("No history directory found in the generated Allure results.")

    # Generate the single HTML file using --single-file option
    single_file_report_dir = os.path.join(parent_dir, 'single-file-report')
    os.makedirs(single_file_report_dir, exist_ok=True)
    generate_allure_report(allure_results_dir, single_file_report_dir, single_file=True)

    # Rename the single HTML file to make it clear
    single_file_html = os.path.join(single_file_report_dir, 'index.html')
    final_single_html = os.path.join(parent_dir, 'allure-report.html')
    if os.path.exists(single_file_html):
        shutil.move(single_file_html, final_single_html)
        logging.info(f"Single HTML report generated at: {final_single_html}")
    else:
        logging.warning("Single HTML file was not created.")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="for Test Type")
    parser.add_argument("--testtype", type=str, help="rest or graphql")

    args = parser.parse_args()
    main(args)

import json
import time
from flask import Flask, jsonify, request, render_template, send_from_directory, render_template_string, abort
import subprocess
import os
import threading
import shutil

app = Flask(__name__)
root_dir = os.path.dirname(__file__)
environment = os.getenv("ENVIRONMENT")

# Global flags to track if the scripts are running
rest_api_test_running = False
graphql_api_test_running = False

# Serve the rest Tests Allure report
@app.route('/allure-report-rest')
def serve_smoke_report():
    report_dir = os.path.join(root_dir, "allure_data", "api_allure_data", "rest")
    return send_from_directory(report_dir, 'allure-report.html')

# Serve the graphql Tests Allure report
@app.route('/allure-report-graphql')
def serve_detailed_report():
    report_dir = os.path.join(root_dir, "allure_data", "api_allure_data", "graphql")
    return send_from_directory(report_dir, 'allure-report.html')

@app.route('/')
def index():
    if environment == "staging":
        return render_template('stag_index.html')
    elif environment == "production":
        return render_template('prod_index.html')


def run_script_in_background(script_type):
    global rest_api_test_running, graphql_api_test_running

    if script_type == "rest":
        rest_api_test_running = True
    elif script_type == "graphql":
        graphql_api_test_running = True

    try:
        logs_dir = os.path.join(root_dir, "logs")
        # Delete the logs directory if it exists
        if os.path.exists(logs_dir):
            shutil.rmtree(logs_dir)

        # Create a new logs directory
        os.makedirs(logs_dir, exist_ok=True)

        log_file_path = os.path.join(logs_dir, f'{script_type}_output.log')
        # Open the log file in append mode
        with open(log_file_path, "a") as log_file:
            try:
                # Execute the subprocess and log output in real-time
                process = subprocess.Popen(
                    ['python', f'{root_dir}/entrypoint_docker.py', '--testtype', script_type],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Stream and write the output to the log file
                for line in process.stdout:
                    log_file.write(f"STDOUT: {line}")
                    print(f"STDOUT: {line.strip()}")  # Optional: Print to console

                for line in process.stderr:
                    log_file.write(f"STDERR: {line}")
                    print(f"STDERR: {line.strip()}")  # Optional: Print to console

                # Wait for the process to complete
                process.wait()

                # Check the return code for success or failure
                if process.returncode != 0:
                    log_file.write(f"Process exited with code {process.returncode}\n")
                    print(f"Process exited with code {process.returncode}")
                else:
                    log_file.write("Process completed successfully.\n")
                    print("Process completed successfully.")

            except Exception as e:
                error_message = f"An error occurred while running the subprocess: {str(e)}\n"
                log_file.write(error_message)
                print(error_message)
    finally:
        if script_type == "rest":
            rest_api_test_running = False 
        elif script_type == "graphql":
            graphql_api_test_running = False


@app.route('/run-rest-tests', methods=['POST'])
def run_smoke_tests():
    if not rest_api_test_running:
        threading.Thread(target=run_script_in_background("rest"), args=("rest",)).start()
        return "rest tests started successfully"
    else:
        return "rest tests are already running"

@app.route('/run-graphql-tests', methods=['POST'])
def run_detailed_tests():
    if not graphql_api_test_running:
        threading.Thread(target=run_script_in_background("graphql"), args=("graphql",)).start()
        return "graphql tests started successfully"
    else:
        return "graphql tests are already running"

@app.route('/status')
def status():
    return jsonify({
        "rest_api_test_running": rest_api_test_running,
        "graphql_api_test_running": graphql_api_test_running
    })

# Route to list all log files
@app.route('/logs')
def list_logs():
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    files = os.listdir(logs_dir)
    files = [f for f in files if os.path.isfile(os.path.join(logs_dir, f)) and f.endswith('.log')]
    
    # Render an HTML template to display the list of log files as links
    return render_template_string('''
        <html>
            <head>
                <title>Logs</title>
            </head>
            <body>
                <h1>Log Files</h1>
                <ul>
                    {% for file in files %}
                        <li><a href="{{ url_for('view_log', filename=file) }}">{{ file }}</a></li>
                    {% endfor %}
                </ul>
            </body>
        </html>
    ''', files=files)

# Route to display log file contents in the browser
@app.route('/logs/view/<filename>')
def view_log(filename):
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    file_path = os.path.join(logs_dir, filename)
    
    # Ensure the file exists and has a .log extension for security
    if not os.path.isfile(file_path) or not filename.endswith('.log'):
        return abort(404)
    
    # Read the file contents and render as plain text
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Display the log content in the browser
    return render_template_string('''
        <html>
            <head>
                <title>{{ filename }}</title>
            </head>
            <body>
                <h1>{{ filename }}</h1>
                <pre>{{ content }}</pre>
                <a href="{{ url_for('list_logs') }}">Back to log files</a>
            </body>
        </html>
    ''', filename=filename, content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

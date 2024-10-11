#!/usr/bin/env python3
import requests
import os
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(filename='/tmp/pam_login_notifier.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def send_login_data(server_ip, client_ip, login_time, username, success):
    api_url = "http://localhost:5010/login"  # Adjust the URL as needed
    data = {
        "server_ip": server_ip,
        "client_ip": client_ip,
        "login_time": login_time,
        "username": username,
        "success": success  # Add success status
    }
    try:
        response = requests.post(api_url, json=data)
        logging.debug(f'Sent data to API: {data}, Response: {response.status_code}')
        if response.status_code != 200:
            logging.error(f'Failed to send data to API: {response.text}')
            return response.status_code
        return response.status_code
    except Exception as e:
        logging.error(f'Exception occurred: {e}')
        return 500

if __name__ == "__main__":
    logging.debug("PAM script started.")

    # Log environment variables for debugging
    logging.debug(f'Environment Variables: {os.environ}')

    # Get the required information
    server_ip = os.popen("hostname -I | awk '{print $1}'").read().strip()  # Get server's IP
    client_ip = os.environ.get("PAM_RHOST", "unknown")  # Get client's IP from PAM
    username = os.environ.get("PAM_USER", "unknown")  # Get the username from PAM
    login_time = datetime.now().isoformat()  # Get current datetime in ISO format

    logging.debug(f'Received data - Server IP: {server_ip}, Client IP: {client_ip}, Username: {username}, Login Time: {login_time}')

    # Determine if the login is successful or not
    # PAM's exit code: 0 = success, anything else = failure
    if os.environ.get("PAM_SUCCESS", "0") == "1":
        success = True
        exit_code = 0
    else:
        success = False
        exit_code = 1

    # Send data to the API
    send_login_data(server_ip, client_ip, login_time, username, success)

    # Exit with appropriate code
    sys.exit(exit_code)


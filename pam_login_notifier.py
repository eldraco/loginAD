#!/usr/bin/env python3
import requests
import os
import sys
from datetime import datetime
import json
import logging
import syslog

# Set up logging to syslog
syslog.openlog('pam_login_notifier')
syslog.syslog('PAM script started.')

# Configure logging
logging.basicConfig(filename='/tmp/pam_login_notifier.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Add this at the beginning of your script
logging.debug("PAM script executed.")

def send_login_data(server_ip, client_ip, login_time, username):
    api_url = "http://147.32.80.37:5010/login"  # Adjust the URL as needed
    data = {
        "server_ip": server_ip,
        "client_ip": client_ip,
        "login_time": login_time,
        "username": username
    }
    try:
        response = requests.post(api_url, json=data)
        return response.status_code, response.json()
    except Exception as e:
        return 500, {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Get the required information
    server_ip = os.popen("hostname -I | awk '{print $1}'").read().strip()  # Get server's IP
    client_ip = os.environ.get("PAM_RHOST", "unknown")  # Get client's IP from PAM
    username = os.environ.get("PAM_USER", "unknown")  # Get the username from PAM
    login_time = datetime.now().isoformat()  # Get current datetime in ISO format

    # Send data to the API
    status_code, response = send_login_data(server_ip, client_ip, login_time, username)
    sys.exit(status_code)

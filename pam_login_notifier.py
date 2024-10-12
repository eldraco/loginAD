#!/usr/bin/env python3
import requests
import os
import sys
from datetime import datetime
import syslog

# Initialize syslog with a specific facility
syslog.openlog("pam_login_notifier", facility=syslog.LOG_LOCAL7)

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
        syslog.syslog(syslog.LOG_DEBUG, f'Sent data to API: {data}, Response: {response.status_code}')
        if response.status_code != 200:
            syslog.syslog(syslog.LOG_ERR, f'Failed to send data to API: {response.text}')
            return response.status_code
        return response.status_code
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f'Exception occurred: {e}')
        return 500

if __name__ == "__main__":
    syslog.syslog(syslog.LOG_DEBUG, "PAM script started.")

    # Log environment variables for debugging
    syslog.syslog(syslog.LOG_DEBUG, f'Environment Variables: {os.environ}')

    # Get the required information
    server_ip = os.popen("hostname -I | awk '{print $1}'").read().strip()  # Get server's IP

    # Extract client IP from SSH_CONNECTION variable
    ssh_connection = os.environ.get("SSH_CONNECTION", "")
    if ssh_connection:
        client_ip = ssh_connection.split()[0]  # The first field is the client IP
    else:
        client_ip = "unknown"  # Default to unknown if SSH_CONNECTION is not set

    # Extract username from PAM_USER and USER
    username = os.environ.get("PAM_USER") or os.environ.get("USER", "unknown")

    login_time = datetime.now().isoformat()  # Get current datetime in ISO format

    syslog.syslog(syslog.LOG_DEBUG, f'Received data - Server IP: {server_ip}, Client IP: {client_ip}, Username: {username}, Login Time: {login_time}')

    # Assume the login is successful for this example
    success = True  # Update this based on your PAM logic

    # Send data to the API
    exit_code = send_login_data(server_ip, client_ip, login_time, username, success)

    # Exit with appropriate code
    sys.exit(exit_code)


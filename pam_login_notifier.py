#!/usr/bin/env python3
import requests
import os
import sys
from datetime import datetime
import syslog

# Initialize syslog with a specific facility
syslog.openlog("pam_login_notifier", facility=syslog.LOG_LOCAL7)

def send_login_data(server_ip, client_ip, login_time, username, success, connection_type):
    api_url = "http://localhost:5000/login"  # Adjust the URL as needed
    data = {
        "server_ip": server_ip,
        "client_ip": client_ip,
        "login_time": login_time,
        "username": username,
        "success": success,
        "connection_type": connection_type  # Add connection type
    }
    try:
        response = requests.post(api_url, json=data)
        syslog.syslog(syslog.LOG_DEBUG, f'Sent data to API: {data}, Response: {response.status_code}')
        if response.status_code != 200:
            syslog.syslog(syslog.LOG_ERR, f'Failed to send data to API: {response.text}')
            return 1  # Return 1 for failure
        return 0  # Success
    except Exception as e:
        syslog.syslog(syslog.LOG_ERR, f'Exception occurred: {e}')
        return 1  # Return 1 for exception

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

    # Determine the connection type and success
    pam_type = os.environ.get("PAM_TYPE", "unknown")
    success = False  # Default to failure
    connection_type = "unknown"  # Default connection type

    if pam_type == 'auth':
        pam_result = os.environ.get("PAM_RESULT", "1")  # Default to failure
        syslog.syslog(syslog.LOG_DEBUG, f'PAM_RESULT: {pam_result}')
        if pam_result == "0":  # Check if PAM_RESULT indicates success
            success = True
        connection_type = "password"  # Set connection type to password
    else:
        connection_type = "public key"  # Set connection type to public key
        success = username != "unknown"  # Assume success based on valid username

    syslog.syslog(syslog.LOG_DEBUG, f'Received data - Server IP: {server_ip}, Client IP: {client_ip}, Username: {username}, Login Time: {login_time}, Success: {success}, Connection Type: {connection_type}')

    # Send data to the API
    exit_code = send_login_data(server_ip, client_ip, login_time, username, success, connection_type)

    # Exit with appropriate code
    sys.exit(exit_code)

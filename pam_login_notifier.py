#!/usr/bin/env python3
import requests
import os
import sys
from datetime import datetime
import syslog


# Initialize syslog with a specific facility
syslog.openlog("pam_login_notifier", facility=syslog.LOG_LOCAL7)

def send_login_data(server_ip, client_ip, login_time, username, success, connection_type):
    api_url = "http://192.168.1.23.:5010/login"  # Adjust the URL as needed
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

    # EXtract if pubkey
    ssh_auth_info = os.environ.get("SSH_AUTH_INFO_0", 'unset').strip()

    # Determine the connection type and success
    pam_type = os.environ.get("PAM_TYPE", "unknown")
    connection_type = "unknown"  # Default connection type
    success = False  # Default to failure
    session_class = os.environ.get("XDG_SESSION_CLASS", "unknown")

    # Check if the script is in the auth phase
    if 'password' in ssh_auth_info:
        connection_type = "password"  # Assume password login
        syslog.syslog(syslog.LOG_DEBUG, f'Type of connection identified: password')
        if pam_type == 'open_session':
            # When in open_session, assume the user has logged in successfully
            success = True
            syslog.syslog(syslog.LOG_DEBUG, f'- Succesful: True')
            # Log received data
            syslog.syslog(syslog.LOG_DEBUG, f'Received data - Server IP: {server_ip}, Client IP: {client_ip}, Username: {username}, Login Time: {login_time}, Success: {success}, Connection Type: {connection_type}')
            # Send data to the API only
            exit_code = send_login_data(server_ip, client_ip, login_time, username, success, connection_type)
        elif pam_type == 'unknown':
            success = False
            syslog.syslog(syslog.LOG_DEBUG, f'- Succesful: False')
            # Log received data
            syslog.syslog(syslog.LOG_DEBUG, f'Received data - Server IP: {server_ip}, Client IP: {client_ip}, Username: {username}, Login Time: {login_time}, Success: {success}, Connection Type: {connection_type}')
            # Send data to the API only
            exit_code = send_login_data(server_ip, client_ip, login_time, username, success, connection_type)
    elif 'publickey' in ssh_auth_info:
        connection_type = "public key"  # Assume public key if authentication fails
        syslog.syslog(syslog.LOG_DEBUG, f'Type of connection identified: pubkey')
        if pam_type == 'open_session':
            # When in open_session, assume the user has logged in successfully
            success = True
            syslog.syslog(syslog.LOG_DEBUG, f'- Succesful: True')
            # Log received data
            syslog.syslog(syslog.LOG_DEBUG, f'Received data - Server IP: {server_ip}, Client IP: {client_ip}, Username: {username}, Login Time: {login_time}, Success: {success}, Connection Type: {connection_type}')
            # Send data to the API only
            exit_code = send_login_data(server_ip, client_ip, login_time, username, success, connection_type)
        elif pam_type == 'unknown':
            success = False
            syslog.syslog(syslog.LOG_DEBUG, f'- Succesful: False')
    elif 'unset' in ssh_auth_info:
        if session_class == 'user':
            # This is the session after a success ful password login. We already logged this. Ignore
            pass
        else:
            connection_type = "password"  # Assume password login
            syslog.syslog(syslog.LOG_DEBUG, f'Type of connection identified: password')
            success = False
            syslog.syslog(syslog.LOG_DEBUG, f'- Succesful: False (SSH Authis unset)')
            # Log received data
            syslog.syslog(syslog.LOG_DEBUG, f'Received data - Server IP: {server_ip}, Client IP: {client_ip}, Username: {username}, Login Time: {login_time}, Success: {success}, Connection Type: {connection_type}')
            # Send data to the API only
            exit_code = send_login_data(server_ip, client_ip, login_time, username, success, connection_type)
    elif pam_type == 'close_session':
        # session is being closed. Do nothing
        syslog.syslog(syslog.LOG_INFO, "Closed session. Not sending data to API.")


    # Exit with appropriate code
    sys.exit(exit_code if success else 0)


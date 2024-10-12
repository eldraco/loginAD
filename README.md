# loginAD
Anomaly detection for logins in Linux systems

This program works by running two different python scripts. First, the one called `loginAD-server.py` which opens a port with Flask and a REST API to receve the logins. Second, the one called `pam_login_notifier.py` which sends the logins from the monitored computer.

A particular thing to notice is that logins with password are managed by PAM, but logins with pubkey are managed by SSHd. So we need to tell these two programs to send the logs.

# Usage and installation

# Clone this program into the computer that will receive the logs, and the computer you want to monitor.

# Copy the script

In the computer you want to monitor, as root copy the script `pam_login_notifier.py` to `/usr/sbin/`.

# Modify the permisions of the script

`chmod 774 /usr/sbin/pam_login_notifier.py`

# Start the loginAD server

In the computer that will receive the logins logs, do:

`python your_script_name.py --port 5000`

Probably is better to run in a tmux, or docker.

## If you want to keep the server running always, make it a service in systemd.


# Modifications in the computer you want to monitor

## 1. Modify the `pam_login_notifier.py` to add the IP address of the loginAD server

Edit `pam_login_notifier.py`

Modify the `api_url` variable to point to the IP address of the loginAD server and port
```
api_url = "http://192.168.1.23:5000/login"  # Adjust the URL as needed
```

## 2. Modify SSH conf
Modify SSH conf to handle the logs of pubkey logins and to log all the attempts to loginAD server.
Remember that apart from this login program, SSHd can have configurations if to allow or not passwords logins. Allowing or not to login, is differnt from sending logs about attempts.

Edit `/etc/ssh/sshd_config`

```
PubkeyAuthentication yes
PasswordAuthentication yes
ForceCommand /usr/bin/python3 /usr/sbin/pam_login_notifier.py; exec /bin/bash
UsePAM yes
```

If your setup does NOT allow for users to login with password, be sure it works by having
```
PasswordAuthentication no
```

## 3. Modify PAM
Modify PAM to send the logs of the password logins

Edit /etc/pam.d/sshd

```
auth required pam_unix.so nullok
auth optional pam_exec.so /usr/sbin/pam_login_notifier.py
auth include common-auth
session optional pam_exec.so /usr/sbin/pam_login_notifier.py
```

## 4. Restart SSH

```
/etc/init.d/ssh restart
```

# loginAD
Anomaly detection for logins in Linux systems


# Start the loginAD server

`python your_script_name.py --port 5000`


# Modifications in the computer you want to monitor


## Modify SSH conf to handle both password logins and pubkey logins and to log all the attempts to loginAD server.

Edit `/etc/ssh/sshd_config`

```
PasswordAuthentication yes
ForceCommand /usr/bin/python3 /usr/sbin/pam_login_notifier.py; exec /bin/bash
```
## Modify the notifier to add the IP address of the loginAD server

Edit pam_login_notifier.py

Modify the api_url variable to point to the IP address of the loginAD server and port
```
api_url = "http://192.168.1.23:5000/login"  # Adjust the URL as needed
```



### Modify PAM
Edit /etc/pam.d/sshd

```
auth optional pam_exec.so /usr/sbin/pam_login_notifier.py
auth required pam_unix.so nullok
auth include common-auth
```


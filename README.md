# loginAD
Anomaly detection for logins in Linux systems


# Start the server

`python your_script_name.py --port 5000`


# Modify the computer you want to monitor

### Modify PAM
Edit /etc/pam.d/sshd

```
auth required pam_exec.so /usr/sbin/pam_login_notifier.py
auth include common-auth
```

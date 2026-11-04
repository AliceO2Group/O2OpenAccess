
# Starting an local CCDB server

Here are the instruction to start a local CCDB server
based on https://gitlab.cern.ch/grigoras/ccdb-local

## Deploying a local CCDB server

1. Build the jar file(s) - the server
run ./build-ccdb-local command, which will package the jar files in local directory
these files are to be moved to location from where the service unit will use them.

2. Generate a systemd service file with command "gen-ccdb-local-service.py"
help page of command:
```
./gen-ccdb-local-service.py -h
usage: gen-ccdb-local-service.py [-h] -r REPOSITORY [-j JAR] [-u USER] [-g GROUP] [-a ADDRESS] [-p PORT] [-o OUTPUT]

Render ccdb-local.service from ccdb-local.service.j2 (same directory as this script).

Defaults:
  user/group  root/root when run as root (effective UID 0), otherwise the
              invoking user and its primary group. --user without --group
              uses that user's primary group.
  --jar       ./local.jar, written as its realpath (symlinks resolved)
  --address   *
  --port      10080

optional arguments:
  -h, --help            show this help message and exit
  -r REPOSITORY, --repository REPOSITORY
                        FILE_REPOSITORY_LOCATION (made absolute)
  -j JAR, --jar JAR     path to local.jar (default: ./local.jar)
  -u USER, --user USER  service User=
  -g GROUP, --group GROUP
                        service Group=
  -a ADDRESS, --address ADDRESS
                        TOMCAT_ADDRESS, comma-separated list allowed (default: "*")
  -p PORT, --port PORT  TOMCAT_PORT (default: 10080)
  -o OUTPUT, --output OUTPUT
                        output file (default: stdout)
```

example of service unit creation:
```
./gen-ccdb-local-service.py -r /fastdata/ccdb_local -j /fastdata/ccdb_srv/local.jar -u adrian -g alice -p 10080 -o ccdb-local.service
```


## System level ccdb service

Example of usage, adapt the user/group/repository location

```
echo "Create the repository location first (required by AssertPathIsDirectory=):"
echo "example command:  sudo install -d -o adrian -g alice -m 0750 /fastdata/ccdb_local"

# generate the unit in the current directory (no sudo); make sure that paths are valid
./gen-ccdb-local-service.py -r /fastdata/ccdb_local -j /fastdata/ccdb_srv/local.jar \
    -u adrian -g alice -o ccdb-local.service

# install, enable, start and show the result: one sudo call
sudo bash -c '
install -m 0644 -o root -g root ccdb-local.service /etc/systemd/system/ccdb-local.service &&
{ ! command -v restorecon >/dev/null || restorecon -v /etc/systemd/system/ccdb-local.service; } &&
systemd-analyze verify /etc/systemd/system/ccdb-local.service &&
systemctl daemon-reload &&
systemctl enable --now ccdb-local.service
systemctl --no-pager status ccdb-local.service
journalctl --no-pager -n 20 -u ccdb-local.service
'
```

## User level ccdb service

```
mkdir -p ~/.config/systemd/user
mkdir -p /my_user_directory/ccdb_local   # needs write access the destination

# adapt the unit for the user service manager:
#  - drop User=/Group= (a user service always runs as that user; Group= would fail)
#  - drop Wants=network-online.target (not available to user services)
#  - WantedBy=default.target (multi-user.target is not available to user services)
./gen-ccdb-local-service.py -r /fastdata/ccdb_local -j /fastdata/ccdb_srv/local.jar \
  | sed -e '/^User=/d' -e '/^Group=/d' -e '/^Wants=network-online.target/d' \
        -e 's/^WantedBy=multi-user.target/WantedBy=default.target/' \
  > ~/.config/systemd/user/ccdb-local.service

systemd-analyze --user verify ~/.config/systemd/user/ccdb-local.service
systemctl --user daemon-reload
systemctl --user enable --now ccdb-local.service
systemctl --user status ccdb-local.service
journalctl --user -u ccdb-local.service -f

# keep it running when you are not logged in, and start it at boot
loginctl enable-linger "$USER"
```

## 






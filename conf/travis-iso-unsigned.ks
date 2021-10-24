%include travis-iso.ks

repo --name=unsigned --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-primary --baseurl=http://ftp.qubes-os.org/~marmarek/repo-verify-unsigned --ignoregroups=true

%include travis-iso.ks

repo --name=unknown-key --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-3.1-primary --baseurl=http://ftp.qubes-os.org/~marmarek/repo-verify-unknown-key --ignoregroups=true

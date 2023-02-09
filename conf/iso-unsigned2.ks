%include iso-online-testing.ks

# unsigned package to be downladed by lorax
repo --name=unsigned2 --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-3.1-primary --baseurl=http://ftp.qubes-os.org/~marmarek/repo-verify-unsigned2 --ignoregroups=true

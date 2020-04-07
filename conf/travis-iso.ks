%include qubes-kickstart.cfg

repo --name=qubes-r4.1-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.1-primary --baseurl=http://yum.qubes-os.org/r4.1/current-testing/dom0/fc32 --ignoregroups=true

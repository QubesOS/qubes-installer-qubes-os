%include qubes-kickstart.cfg

repo --name=qubes-r4.2-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.2-primary --baseurl=http://yum.qubes-os.org/r4.2/current-testing/host/fc37 --ignoregroups=true

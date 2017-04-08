%include qubes-kickstart.cfg

repo --name=qubes-r4.0-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-primary --baseurl=http://yum.qubes-os.org/r4.0/current-testing/dom0/fc25

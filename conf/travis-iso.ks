%include qubes-kickstart.cfg

repo --name=qubes-r3.1-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-3.1-primary --baseurl=http://yum.qubes-os.org/r3.1/current-testing/dom0/fc20

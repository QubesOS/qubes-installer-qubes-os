%include qubes-kickstart.cfg

repo --name=qubes-r4.0-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-primary --baseurl=http://mirrors.ukfast.co.uk/sites/qubes-os.org/repo/yum/r4.0/current-testing/dom0/fc25 --ignoregroups=true
repo --name=qubes-r4.0-templates-itl --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-primary --baseurl=http://mirrors.ukfast.co.uk/sites/qubes-os.org/repo/yum/r4.0/templates-itl --ignoregroups=true
repo --name=qubes-r4.0-templates-community --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-templates-community --baseurl=http://mirrors.ukfast.co.uk/sites/qubes-os.org/repo/yum/r4.0/templates-community --ignoregroups=true


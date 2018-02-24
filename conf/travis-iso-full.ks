%include qubes-kickstart.cfg

repo --name=qubes-r3.2-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-3.2-primary --baseurl=http://mirrors.ukfast.co.uk/sites/qubes-os.org/repo/yum/r3.2/current-testing/dom0/fc25 --ignoregroups=true
repo --name=qubes-r3.2-templates-itl --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-3.2-primary --baseurl=http://mirrors.ukfast.co.uk/sites/qubes-os.org/repo/yum/r3.2/templates-itl --ignoregroups=true
repo --name=qubes-r3.2-templates-community --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-3.2-templates-community --baseurl=http://mirrors.ukfast.co.uk/sites/qubes-os.org/repo/yum/r3.2/templates-community --ignoregroups=true

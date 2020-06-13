%include iso-full-online.ks

repo --name=qubes-r4.1-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.1-primary --baseurl=http://yum.qubes-os.org/r4.1/current-testing/dom0/fc32 --ignoregroups=true
repo --name=qubes-r4.1-templates-itl-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.1-primary --metalink=http://yum.qubes-os.org/r4.1/templates-itl-testing/repodata/repomd.xml.metalink --ignoregroups=true
repo --name=qubes-r4.1-templates-community-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.1-templates-community --metalink=http://yum.qubes-os.org/r4.1/templates-community-testing/repodata/repomd.xml.metalink --ignoregroups=true


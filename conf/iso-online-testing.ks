%include iso-online.ks

repo --name=qubes-r4.2-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.2-primary --baseurl=http://yum.qubes-os.org/r4.2/current-testing/host/fc37 --ignoregroups=true
repo --name=qubes-r4.2-templates-itl-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.2-primary --metalink=http://yum.qubes-os.org/r4.2/templates-itl-testing/repodata/repomd.xml.metalink --ignoregroups=true
repo --name=qubes-r4.2-templates-community-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.2-templates-community --metalink=http://yum.qubes-os.org/r4.2/templates-community-testing/repodata/repomd.xml.metalink --ignoregroups=true


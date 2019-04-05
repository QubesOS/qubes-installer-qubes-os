%include iso-full-online.ks

repo --name=qubes-r4.0-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-primary --baseurl=http://yum.qubes-os.org/r4.0/current-testing/dom0/fc25 --ignoregroups=true
repo --name=qubes-r4.0-templates-itl-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-primary --mirrorlist=http://yum.qubes-os.org/r4.0/templates-itl-testing/repodata/repomd.xml.metalink --ignoregroups=true
repo --name=qubes-r4.0-templates-community-testing --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-templates-community --mirrorlist=http://yum.qubes-os.org/r4.0/templates-community-testing/repodata/repomd.xml.metalink --ignoregroups=true


# Full ISO build using packages from online repositories instead of local build
%include qubes-kickstart.cfg

repo --name=qubes-r4.1 --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.1-primary --baseurl=http://yum.qubes-os.org/r4.1/current-testing/dom0/fc32 --ignoregroups=true
repo --name=qubes-r4.1-templates-itl --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.1-primary --metalink=http://yum.qubes-os.org/r4.1/templates-itl/repodata/repomd.xml.metalink --ignoregroups=true
repo --name=qubes-r4.1-templates-community --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.1-templates-community --metalink=http://yum.qubes-os.org/r4.1/templates-community/repodata/repomd.xml.metalink --ignoregroups=true


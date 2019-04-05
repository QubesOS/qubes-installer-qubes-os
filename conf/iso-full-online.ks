# Full ISO build using packages from online repositories instead of local build
%include qubes-kickstart.cfg

repo --name=qubes-r4.0 --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-primary --baseurl=http://yum.qubes-os.org/r4.0/current-testing/dom0/fc25 --ignoregroups=true
repo --name=qubes-r4.0-templates-itl --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-primary --mirrorlist=http://yum.qubes-os.org/r4.0/templates-itl/repodata/repomd.xml.metalink --ignoregroups=true
repo --name=qubes-r4.0-templates-community --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.0-templates-community --mirrorlist=http://yum.qubes-os.org/r4.0/templates-community/repodata/repomd.xml.metalink --ignoregroups=true


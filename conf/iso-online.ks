# Full ISO build using packages from online repositories instead of local build
%include qubes-kickstart.cfg

repo --name=qubes-r4.2 --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.2-primary --baseurl=http://yum.qubes-os.org/r4.2/current/host/fc37 --ignoregroups=true
repo --name=qubes-r4.2-templates-itl --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.2-primary --metalink=http://yum.qubes-os.org/r4.2/templates-itl/repodata/repomd.xml.metalink --ignoregroups=true
repo --name=qubes-r4.2-templates-community --gpgkey=file:///tmp/qubes-installer/qubes-release/RPM-GPG-KEY-qubes-4.2-templates-community --metalink=http://yum.qubes-os.org/r4.2/templates-community/repodata/repomd.xml.metalink --ignoregroups=true


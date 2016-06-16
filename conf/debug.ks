# This kickstart is used for building "debug" ISO, which is used for automatic
# tests. Do not use for releases.

%include qubes-kickstart.cfg

%packages

gdb
python-ipython
netplug
openssh-server
rpm-build
rpm-sign
strace
xdotool
xen-debuginfo

qubes-core-dom0-debuginfo
qubes-core-dom0-linux-debuginfo
qubes-gui-dom0-debuginfo

%end

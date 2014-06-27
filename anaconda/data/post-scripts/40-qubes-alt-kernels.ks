%post --nochroot

for pkg in /run/install/repo/extrakernels/*.rpm; do
  name=`basename $pkg .rpm`
  rpm --root=$ANA_INSTALL_PATH -q $name > /dev/null || rpm --root=$ANA_INSTALL_PATH -i --oldpackage $pkg
done

# Set default VM kernel back to newest one
kver=`ls /var/lib/qubes/vm-kernels|sort -n|tail -1`
chroot $ANA_INSTALL_PATH qubes-prefs -s default-kernel $kver

# Set grub default to the current kernel if running not the latest one
latest=`basename /run/install/repo/Packages/k/kernel-[0-9]*.rpm .rpm|cut -d- -f2-`
if [ "$latest" != "`uname -r`" ]; then
    rootdev=`grep " $ANA_INSTALL_PATH " /proc/mounts | cut -f 1 -d ' '`
    sysid=`blkid -o value -s UUID $rootdev`
    xenver=`dmesg | grep 'Xen version:' | sed -e 's/.*version: \([0-9.]\+\).*/\1/'`
    grubid="gnulinux-advanced-$sysid"
    grubid="$grubid>xen-hypervisor-$xenver-$sysid"
    grubid="$grubid>xen-gnulinux-`uname -r`-advanced-$sysid"
    grub2-set-default --boot-directory=$ANA_INSTALL_PATH/boot "$grubid"
fi

%end

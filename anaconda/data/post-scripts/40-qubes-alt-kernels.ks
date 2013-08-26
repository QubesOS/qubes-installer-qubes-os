%post --nochroot

for pkg in /run/install/repo/extrakernels/*.rpm; do
  name=`basename $pkg .rpm`
  rpm --root=$ANA_INSTALL_PATH -q $name > /dev/null || rpm --root=$ANA_INSTALL_PATH -i --oldpackage $pkg
done

%end

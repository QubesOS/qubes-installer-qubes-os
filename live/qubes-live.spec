Name:       qubes-live
Version:    1.0
Release:    1%{?dist}
Summary:    Various fixes for Qubes Live edition

Group:      System
License:    GPL
URL:        https://qubes-os.org

%description
Various fixes for Qubes Live edition

%prep

%build

%install

%post

# livecd-tools expects strange xen.gz name
xen=$(ls -1 /boot/xen-*gz | tail -n 1)
for kernel in /boot/vmlinuz-*; do
    # see __copy_kernel_and_initramfs function in imgcreate/live.py
    version=$(echo ${kernel} | cut -f 2- -d -)
    short_version=$(echo -n ${version} | head -c -3)
    ln -s $(basename ${xen}) /boot/xen.gz-${short_version}
done


%files


%changelog



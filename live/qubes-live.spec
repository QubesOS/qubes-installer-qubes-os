%if 0%{?qubes_builder}
%define _builddir %(pwd)/live
%endif

Name:       qubes-live
Version:    1.0
Release:    1%{?dist}
Summary:    Various fixes for Qubes Live edition

Group:      System
License:    GPL
URL:        https://qubes-os.org

# ensure that the whole %%post is run when xen and kernel are already installed
Requires(post): xen-hypervisor
Requires(post): kernel

%description
Various fixes for Qubes Live edition

%prep

%build

%install


install -d -m 0755 $RPM_BUILD_ROOT/etc/rc.d/init.d/
install -m 0755 -t $RPM_BUILD_ROOT/etc/rc.d/init.d/ \
    livesys \
    livesys-late

install -D -m 0644 lightdm-qubes-live.conf \
            $RPM_BUILD_ROOT/etc/lightdm/lightdm.conf.d/50-qubes-live.conf


install -D -m 0644 default-appmenus-fedora \
            $RPM_BUILD_ROOT/usr/share/qubes/live-default-appmenus-fedora
install -D -m 0644 default-appmenus-debian \
            $RPM_BUILD_ROOT/usr/share/qubes/live-default-appmenus-debian

%post

/sbin/restorecon /etc/rc.d/init.d/livesys
/sbin/chkconfig --add livesys

/sbin/restorecon /etc/rc.d/init.d/livesys-late
/sbin/chkconfig --add livesys-late

# livecd-tools expects strange xen.gz name
xen=$(ls -1 /boot/xen-*gz | tail -n 1)
for kernel in /boot/vmlinuz-*; do
    # see __copy_kernel_and_initramfs function in imgcreate/live.py
    version=$(echo ${kernel} | cut -f 2- -d -)
    short_version=$(echo -n ${version} | head -c -3)
    ln -s $(basename ${xen}) /boot/xen.gz-${short_version}
done

# EFI: prepare small version of initrd to fit in 32MB ISO9660 limit
xen=$(ls -1 /boot/efi/EFI/qubes/xen-*.efi | tail -n 1)
if [ -n "$xen" ]; then
    kernel=$(ls -1 /boot/vmlinuz-*|sort -n|tail -n 1)
    cp "${kernel}" /boot/efi/EFI/qubes/vmlinuz
    version=$(echo ${kernel} | cut -f 2- -d -)
    # copy from lorax-templates-qubes/templates/efi.tmpl:
    scsi_modules="3w-9xxx 3w-sas 3w-xxxx BusLogic a100u2w aacraid advansys aic79xx aic7xxx am53c974 arcmsr atp870u bfa bnx2fc csiostor dc395x dmx3191d esas2r esp_scsi fcoe fnic gdth hpsa hptiop hv_storvsc initio ipr ips isci iscsi_boot_sysfs libfc libfcoe libiscsi libosd libsas lpfc megaraid megaraid_mbox megaraid_mm megaraid_sas mpt2sas mpt3sas mvsas mvumi osd pm80xx pmcraid qla1280 qla2xxx qla4xxx raid_class scsi_debug scsi_dh_emc scsi_dh_rdac scsi_transport_fc scsi_transport_iscsi scsi_transport_sas scsi_transport_spi scsi_transport_srp stex sym53c8xx ufshcd virtio_scsi vmw_pvscsi wd719x"
    extra_modules="affs befs coda cuse dlm gfs2 mptfc ncpfs nilfs2 ocfs2 ocfs2_dlm ocfs2_dlmfs ocfs2_nodemanager ocfs2_stack_o2cb ocfs2_stack_user ocfs2_stackglue sctp sysv ubifs ufs"
    dracut --nomdadmconf --nolvmconf --xz \
        --omit "network multipath modsign systemd crypt shutdown plymouth" \
        --omit "fcoe fcoe-uefi nfs iscsi ifcfg" \
        --omit-drivers="${scsi_modules}" \
        --omit-drivers="${extra_modules}" \
        /boot/efi/EFI/qubes/initrd-small.img ${version}
fi

%files
/etc/rc.d/init.d/livesys
/etc/rc.d/init.d/livesys-late
/etc/lightdm/lightdm.conf.d/50-qubes-live.conf
/usr/share/qubes/live-default-appmenus-fedora
/usr/share/qubes/live-default-appmenus-debian

%changelog



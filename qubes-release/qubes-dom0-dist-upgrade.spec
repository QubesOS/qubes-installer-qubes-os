%define fedora_base_version %{fedora}

Summary:	Qubes dom0 dist upgrade
Name:		qubes-dom0-dist-upgrade
Version:	2.0
Release:	2
License:	GPLv2
Group:		System Environment/Base
Source0:	%{name}-%{version}.tar.bz2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch

%description
Qubes dom0 upgrade transitional package.

%prep
%autosetup -p1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc

install -d -m 755 $RPM_BUILD_ROOT/etc/pki/rpm-gpg

install -m 644 RPM-GPG-KEY-fedora-%{fedora_base_version}-primary $RPM_BUILD_ROOT/etc/pki/rpm-gpg/

install -d -m 755 $RPM_BUILD_ROOT/etc/yum.repos.d
sed -e "s/%%DIST%%/fc%{fedora_base_version}/" qubes-dom0.repo.in > $RPM_BUILD_ROOT/etc/yum.repos.d/qubes-dom0-upgrade.repo
sed -e "s/%%FCREL%%/%{fedora_base_version}/" fedora.repo.in > $RPM_BUILD_ROOT/etc/yum.repos.d/fedora-upgrade.repo
sed -e "s/%%FCREL%%/%{fedora_base_version}/" fedora-updates.repo.in > $RPM_BUILD_ROOT/etc/yum.repos.d/fedora-updates-upgrade.repo

sed -i -e "s/^\[/[upgrade-/;s/^name=.*/\0 (upgrade)/" $RPM_BUILD_ROOT/etc/yum.repos.d/*repo

%post
# Import all keys b/c rpm won't do it automatically (as opposite to yum)
rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-* || true

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%config(noreplace) /etc/yum.repos.d/fedora-upgrade.repo
%config(noreplace) /etc/yum.repos.d/fedora-updates-upgrade.repo
%config(noreplace) /etc/yum.repos.d/qubes-dom0-upgrade.repo
/etc/pki/rpm-gpg/*

%changelog

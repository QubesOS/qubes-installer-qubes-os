%define dist_version 4.0
%define release_name R%{dist_version}
%define fedora_base_version %{fedora}

Summary:	Qubes release files
Name:		qubes-release
Version:	%{dist_version}
Release:	7
License:	GPLv2
Group:		System Environment/Base
Source0:	%{name}-%{version}.tar.bz2
Obsoletes:	fedora-release
Obsoletes:	redhat-release
Provides:	fedora-release = %{fedora_base_version}-%{release}
Provides:	redhat-release = %{fedora_base_version}-%{release}
Provides:	system-release = %{fedora_base_version}-%{release}
Provides:	system-release(releasever) = %{version}
Obsoletes:	qubes-dom0-dist-upgrade <= 3.2
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:	noarch

%description
Qubes release files such as yum configs and various /etc/ files that
define the release.

%package notes
Summary:	Release Notes
License:	Open Publication
Group:		System Environment/Base
Provides:	system-release-notes = %{version}-%{release}
Conflicts:	fedora-release-notes

%description notes
Qubes release notes package.


%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc
echo "Qubes release %{version} (%{release_name})" > $RPM_BUILD_ROOT/etc/qubes-release
echo "cpe:/o:ITL:qubes:%{version}" > $RPM_BUILD_ROOT/etc/system-release-cpe
cp -p $RPM_BUILD_ROOT/etc/qubes-release $RPM_BUILD_ROOT/etc/issue
echo "Kernel \r on an \m (\l)" >> $RPM_BUILD_ROOT/etc/issue
cp -p $RPM_BUILD_ROOT/etc/issue $RPM_BUILD_ROOT/etc/issue.net
echo >> $RPM_BUILD_ROOT/etc/issue
ln -s qubes-release $RPM_BUILD_ROOT/etc/fedora-release
ln -s qubes-release $RPM_BUILD_ROOT/etc/redhat-release
ln -s qubes-release $RPM_BUILD_ROOT/etc/system-release

cat << EOF >>$RPM_BUILD_ROOT/etc/os-release
NAME=Qubes
VERSION="%{version} (%{release_name})"
ID=qubes
VERSION_ID=%{version}
PRETTY_NAME="Qubes %{version} (%{release_name})"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:ITL:qubes:%{version}"
EOF

install -d -m 755 $RPM_BUILD_ROOT/etc/pki/rpm-gpg

install -m 644 RPM-GPG-KEY* $RPM_BUILD_ROOT/etc/pki/rpm-gpg/

install -d -m 755 $RPM_BUILD_ROOT/etc/yum.repos.d
sed -e "s/%%DIST%%/fc%{fedora_base_version}/" qubes-dom0.repo.in > $RPM_BUILD_ROOT/etc/yum.repos.d/qubes-dom0.repo
sed -e "s/%%FCREL%%/%{fedora_base_version}/" fedora.repo.in > $RPM_BUILD_ROOT/etc/yum.repos.d/fedora.repo
sed -e "s/%%FCREL%%/%{fedora_base_version}/" fedora-updates.repo.in > $RPM_BUILD_ROOT/etc/yum.repos.d/fedora-updates.repo
install -m 644 qubes-templates.repo $RPM_BUILD_ROOT/etc/yum.repos.d

install -d -m 755 $RPM_BUILD_ROOT/usr/share/qubes
install -m 644 comps-qubes.xml $RPM_BUILD_ROOT/usr/share/qubes/Qubes-comps.xml

# Set up the dist tag macros
install -d -m 755 $RPM_BUILD_ROOT/etc/rpm
cat >> $RPM_BUILD_ROOT/etc/rpm/macros.dist << EOF
# dist macros.

%%qubes		%{dist_version}
%%dist		.qbs%{dist_version}
%%fedora		%{fedora_base_version}
%%qbs3		1
%%fc%{fedora_base_version}		1
EOF

%posttrans
# Import all keys b/c rpm won't do it automatically (as opposite to yum)
systemd-run --on-active=5min rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-*


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc GPL 
%config %attr(0644,root,root) /etc/os-release
%config %attr(0644,root,root) /etc/qubes-release
%config %attr(0644,root,root) /etc/fedora-release
/etc/redhat-release
/etc/system-release
%config %attr(0644,root,root) /etc/system-release-cpe
%dir /etc/yum.repos.d
%config(noreplace) /etc/yum.repos.d/fedora.repo
%config(noreplace) /etc/yum.repos.d/fedora-updates.repo
%config(noreplace) /etc/yum.repos.d/qubes-dom0.repo
%config(noreplace) /etc/yum.repos.d/qubes-templates.repo
%config(noreplace) %attr(0644,root,root) /etc/issue
%config(noreplace) %attr(0644,root,root) /etc/issue.net
%config %attr(0644,root,root) /etc/rpm/macros.dist
%dir /etc/pki/rpm-gpg
/etc/pki/rpm-gpg/*
/usr/share/qubes/Qubes-comps.xml

%files notes
%defattr(-,root,root,-)
%doc README.Qubes-Release-Notes

%changelog
* Wed Jan 13 2010 Tomasz Sterna <smoku@xiaoka.com> - 1
- Initial Qubes 1 Release package

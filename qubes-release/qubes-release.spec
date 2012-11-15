%define release_name R1
%define dist_version 1
%define fedora_base_version 13

Summary:	Qubes release files
Name:		qubes-release
Version:	1
Release:	3
License:	GPLv2
Group:		System Environment/Base
Source:		%{name}-%{version}.tar.bz2
Obsoletes:	fedora-release
Obsoletes:	redhat-release
Provides:	fedora-release = %{fedora_base_version}-%{release}
Provides:	redhat-release = %{fedora_base_version}-%{release}
Provides:	system-release = %{version}-%{release}
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

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc
echo "Qubes release %{version} (%{release_name})" > $RPM_BUILD_ROOT/etc/qubes-release
echo "cpe://o:qubes:qubes:%{version}" > $RPM_BUILD_ROOT/etc/system-release-cpe
cp -p $RPM_BUILD_ROOT/etc/qubes-release $RPM_BUILD_ROOT/etc/issue
echo "Kernel \r on an \m (\l)" >> $RPM_BUILD_ROOT/etc/issue
cp -p $RPM_BUILD_ROOT/etc/issue $RPM_BUILD_ROOT/etc/issue.net
echo >> $RPM_BUILD_ROOT/etc/issue
ln -s qubes-release $RPM_BUILD_ROOT/etc/fedora-release
ln -s qubes-release $RPM_BUILD_ROOT/etc/redhat-release
ln -s qubes-release $RPM_BUILD_ROOT/etc/system-release

install -d -m 755 $RPM_BUILD_ROOT/etc/pki/rpm-gpg

install -m 644 RPM-GPG-KEY* $RPM_BUILD_ROOT/etc/pki/rpm-gpg/

install -d -m 755 $RPM_BUILD_ROOT/etc/yum.repos.d
for file in {qubes,fedora,fedora-updates}*repo ; do
  install -m 644 $file $RPM_BUILD_ROOT/etc/yum.repos.d
done

# Set up the dist tag macros
install -d -m 755 $RPM_BUILD_ROOT/etc/rpm
cat >> $RPM_BUILD_ROOT/etc/rpm/macros.dist << EOF
# dist macros.

%%qubes		%{dist_version}
%%dist		.qbs%{dist_version}
%%fedora		%{fedora_base_version}
%%qbs%{dist_version}		1
%%fc%{fedora_base_version}		1
EOF

%post
# On Mar 31, 2012, the Qubes signing key has changed
# The new key is brought by this RPM, but we also
# need to explicitly import it to RPM DB
if [ $1 -gt 1 ]; then
    rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-qubes-1-primary
fi


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc GPL 
%config %attr(0644,root,root) /etc/qubes-release
%config %attr(0644,root,root) /etc/fedora-release
/etc/redhat-release
/etc/system-release
%config %attr(0644,root,root) /etc/system-release-cpe
%dir /etc/yum.repos.d
%config(noreplace) /etc/yum.repos.d/fedora.repo
%config(noreplace) /etc/yum.repos.d/fedora-updates.repo
%config(noreplace) /etc/yum.repos.d/qubes-dom0.repo
%config(noreplace) %attr(0644,root,root) /etc/issue
%config(noreplace) %attr(0644,root,root) /etc/issue.net
%config %attr(0644,root,root) /etc/rpm/macros.dist
%dir /etc/pki/rpm-gpg
/etc/pki/rpm-gpg/*

%files notes
%defattr(-,root,root,-)
%doc README.Qubes-Release-Notes

%changelog
* Tue Jan 13 2010 Tomasz Sterna <smoku@xiaoka.com> - 1
- Initial Qubes 1 Release package

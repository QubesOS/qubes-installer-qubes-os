Name:           qubes-anaconda-addon
Version:        4.0.10
Release:        1%{?dist}
Summary:        Anaconda addon useful for Qubes OS specific setup procedures

License:        GPLv2+

BuildArch:      noarch
BuildRequires:  python3
Requires:       python3
Requires:       qubes-mgmt-salt-dom0-virtual-machines >= 4.0.11
#Requires:       anaconda >= 19

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0: %{name}-%{version}.tar.gz

%description
This is an addon that makes available Qubes OS specific setup functionality
at first boot time.

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/%{_datadir}/anaconda/addons
cp -a org_qubes_os_initial_setup $RPM_BUILD_ROOT/%{_datadir}/anaconda/addons/

%files
%defattr(-,root,root,-)
%doc LICENSE README
%dir %{_datadir}/anaconda/addons/org_qubes_os_initial_setup
%{_datadir}/anaconda/addons/org_qubes_os_initial_setup/*

%changelog
* Sun Mar 27 2016 M. Vefa Bicakci <m.v.b@runbox.com> - 1.0-1
- Initial package for qubes-anaconda-addon

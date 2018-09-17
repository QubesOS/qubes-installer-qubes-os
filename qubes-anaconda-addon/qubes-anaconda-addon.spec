%if 0%{?qubes_builder}
%define _builddir %(pwd)/qubes-anaconda-addon
%endif

Name:           qubes-anaconda-addon
Version:        3.2.4
Release:        1%{?dist}
Summary:        Anaconda addon useful for Qubes OS specific setup procedures

License:        GPLv2+

BuildArch:      noarch
BuildRequires:  python3
Requires:       python3
#Requires:       anaconda >= 19

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
This is an addon that makes available Qubes OS specific setup functionality
at first boot time.

%prep
true

%build
true

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT/%{_datadir}/qubes
install --mode 0755 firstboot-qubes-text $RPM_BUILD_ROOT/%{_datadir}/qubes/firstboot-qubes-text

install -d $RPM_BUILD_ROOT/%{_datadir}/anaconda/addons
cp -a org_qubes_os_initial_setup $RPM_BUILD_ROOT/%{_datadir}/anaconda/addons/

%files
%defattr(-,root,root,-)
%doc LICENSE README
%{_datadir}/qubes/firstboot-qubes-text
%dir %{_datadir}/anaconda/addons/org_qubes_os_initial_setup
%{_datadir}/anaconda/addons/org_qubes_os_initial_setup/*

%changelog
* Sun Mar 27 2016 M. Vefa Bicakci <m.v.b@runbox.com> - 1.0-1
- Initial package for qubes-anaconda-addon

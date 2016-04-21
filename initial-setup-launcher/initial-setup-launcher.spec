Name:		initial-setup-launcher
Version:	1.0
Release:	1%{?dist}
Summary:	Initial system configuration utility launcher

Group:		System Environment/Base
License:	GPLv2+
URL:		https://fedoraproject.org/wiki/InitialSetup

Source0:	%{name}-%{version}.tar.bz2

Requires:	initial-setup

%if 0%{?qubes_builder}
%define _builddir %(pwd)/initial-setup-launcher
%endif

%description
Launcher for initial-setup utility. Used to avoid race condition described here:
https://fedoraproject.org/wiki/Common_F23_bugs#Initial_setup_sometimes_starts_in_text_mode_instead_of_in_graphics_mode

%prep
%if ! 0%{?qubes_builder}
%setup -q
%endif


%build

%install
install -D run-initial-setup $RPM_BUILD_ROOT/usr/bin/run-initial-setup
install -m 0644 -D initial-setup-graphical.service.d \
            $RPM_BUILD_ROOT%{_unitdir}/initial-setup-graphical.service.d/30-initial-setup-launcher.conf
install -m 0644 -D initial-setup-text.service.d \
            $RPM_BUILD_ROOT%{_unitdir}/initial-setup-text.service.d/30-initial-setup-launcher.conf
install -m 0644 -D initial-setup.service \
            $RPM_BUILD_ROOT%{_unitdir}/initial-setup.service

%files
/usr/bin/run-initial-setup
%{_unitdir}/initial-setup-graphical.service.d/30-initial-setup-launcher.conf
%{_unitdir}/initial-setup-text.service.d/30-initial-setup-launcher.conf
%{_unitdir}/initial-setup.service

%changelog


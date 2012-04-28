%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define pkg_cobbler 1
%define pkg_comps 1
%define pkg_composer 0
%define pkg_delta 0
%define pkg_hub 0
%define pkg_isolinux 1
%define pkg_jigdo 0
%define pkg_mock 1
%define pkg_rebrand 0
%define pkg_reuseinstaller 1
%define pkg_server 0
%define pkg_unity 1
%define pkg_unity_scripts 1
%define pkg_virt 0
%define pkg_wui 0

Summary:        Fedora "Spin" Graphical User Interface
Name:           revisor
Version:        2.2
Release:        5%{?dist}
License:        GPLv2
Group:          Applications/System
URL:            http://fedorahosted.org/revisor
Source0:        http://fedorahosted.org/releases/r/e/revisor/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch:      noarch
Requires:       revisor-gui = %{version}-%{release}

%description
Revisor provides a set of graphical tools for building customized, updated
Fedora "Spins". This tool has been built around two other projects. First
is pungi, which builds the installation media. The other is livecd-tools,
which builds the live image.

##
## Revisor CLI
##
%package cli
Summary:        Revisor CLI components
Group:          Applications/System
BuildRequires:  intltool, gettext, python, desktop-file-utils

Requires:       revisor-comps = %{version}-%{release}
# Package Management Requirements
Requires:       yum >= 3, yum-utils, comps-extras, createrepo
# Kickstart
Requires:       pykickstart
# Compose tools
Requires:       livecd-tools >= 015, anaconda-runtime, squashfs-tools
# Kickstarts for use with Revisor
Requires:       spin-kickstarts
# Other
Requires:       libxml2-python
Requires:       notify-python
Requires:       usermode
Requires:       pam
Requires:       python(abi) >= 2.4
Conflicts:      fedora-release < 7
# Can't conflict with this one!
#Conflicts:      centos-release < 5
# Can't conflict with this one!
#Conflicts:      redhat-release < 5
# Or:
#Conflicts:      redhat-release = 4, redhat-release = 3
Requires:       fedora-kickstarts
Requires:       custom-kickstarts
%if ! %{pkg_comps}
Obsoletes:      revisor-comps < %{version}-%{release}
Provides:       revisor-comps = %{version}-%{release}
%endif
%if ! %{pkg_cobbler}
Obsoletes:      revisor-cobbler < %{version}-%{release}
Provides:       revisor-cobbler = %{version}-%{release}
%endif
%if ! %{pkg_composer}
Obsoletes:      revisor-composer < %{version}-%{release}
Provides:       revisor-composer = %{version}-%{release}
%endif
%if ! %{pkg_delta}
Obsoletes:      revisor-delta < %{version}-%{release}
Provides:       revisor-delta = %{version}-%{release}
%endif
%if ! %{pkg_hub}
Obsoletes:      revisor-hub < %{version}-%{release}
Provides:       revisor-hub = %{version}-%{release}
%endif
%if ! %{pkg_isolinux}
Obsoletes:      revisor-isolinux < %{version}-%{release}
Provides:       revisor-isolinux = %{version}-%{release}
%endif
%if ! %{pkg_jigdo}
Obsoletes:      revisor-jigdo < %{version}-%{release}
Provides:       revisor-jigdo = %{version}-%{release}
%endif
%if ! %{pkg_mock}
Obsoletes:      revisor-mock < %{version}-%{release}
Provides:       revisor-mock = %{version}-%{release}
%endif
%if ! %{pkg_rebrand}
Obsoletes:      revisor-rebrand < %{version}-%{release}
Provides:       revisor-rebrand = %{version}-%{release}
%endif
%if ! %{pkg_reuseinstaller}
Obsoletes:      revisor-reuseinstaller < %{version}-%{release}
Provides:       revisor-reuseinstaller = %{version}-%{release}
%endif
%if ! %{pkg_server}
Obsoletes:      revisor-server < %{version}-%{release}
Provides:       revisor-server = %{version}-%{release}
%endif
%if ! %{pkg_unity}
Obsoletes:      revisor-unity < %{version}-%{release}
Provides:       revisor-unity = %{version}-%{release}
%else
Requires:       revisor-unity = %{version}-%{release}
%endif
%if ! %{pkg_unity_scripts}
Obsoletes:      revisor-unity-scripts < %{version}-%{release}
Provides:       revisor-unity-scripts = %{version}-%{release}
%endif
%if ! %{pkg_virt}
Obsoletes:      revisor-virt < %{version}-%{release}
Provides:       revisor-virt = %{version}-%{release}
%endif
%if ! %{pkg_wui}
Obsoletes:      revisor-wui < %{version}-%{release}
Provides:       revisor-wui = %{version}-%{release}
%endif

Source100: F13-buildinstall
Patch100:  revisor-2.2-comps.patch
Patch101:  revisor-2.2-release.patch
Patch102:  revisor-2.2-volume-label.patch

%description cli
Revisor provides a set of graphical tools for building customized, updated
Fedora "Spins". This tool has been built around two other projects. First
is pungi, which builds the installation media. The other is livecd-tools,
which builds the live image.

##
## Revisor Comps
##
%if %{pkg_comps}
%package comps
Summary:    Revisor Comps Files
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}

%description comps
A number of comps files, as up-to-date as possible
%endif

##
## Revisor cobbler plugin
##
%if %{pkg_cobbler}
%package cobbler
Summary:    Revisor Cobbler Integration
Group:      Applications/System
ExcludeArch: ppc ppc64
Requires:   cobbler, koan, revisor-cli = %{version}-%{release}

%description cobbler
Revisor Integration with Cobbler for having Revisor do DHCP, PXE,
Xen and KVM stuff.
%endif

##
## Revisor Composer plugin
##
%if %{pkg_composer}
%package composer
Summary:    Revisor Composer, for use with the Hub
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}

%description composer
Revisor build farms need Composers. This is it.
%endif

##
## Revisor DeltaRPM/DeltaISO plugin
##
%if %{pkg_delta}
%package delta
Summary:    Revisor Deltarpm Integration
Group:      Applications/System
Requires:   deltarpm, revisor-cli = %{version}-%{release}

%description delta
Revisor Integration with deltarpm for generating delta ISO images.
%endif

##
## Revisor GUI
##
%package gui
Summary:    Revisor GUI
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}, pygtk2 >= 2.9.2, pygtk2-libglade, gnome-python2-gconf
Requires:   system-config-kickstart, system-config-keyboard >= 1.3.0

%description gui
This is the Revisor GUI package

##
## Revisor HUB plugin
##
%if %{pkg_hub}
%package hub
Summary:    Revisor Hub for build farms
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}

%description hub
Revisor build farms need a Hub. This is it.
%endif

##
## Revisor customize isolinux.cfg
##
%if %{pkg_isolinux}
%package isolinux
Summary:    Revisor plugin for supplying a custom isolinux.cfg
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}

%description isolinux
Supply a custom isolinux.cfg to Revisor to incorporate in the installation media
%endif

##
## Revisor Jigdo integration
##
%if %{pkg_jigdo}
%package jigdo
Summary:    Revisor Integration with Jigdo
Group:      Applications/System
Requires:   jigdo, revisor-cli = %{version}-%{release}

%description jigdo
Pre-Alpha of Revisor Integration with Jigdo for distributing your compose
%endif

##
## Revisor Mock integration
##
%if %{pkg_mock}
%package mock
Summary:    Revisor Integration with Mock
Group:      Applications/System
Requires:   mock, revisor-cli = %{version}-%{release}

%description mock
Revisor Integration with Mock for building the installer images
%endif

##
## Revisor Rebranding plugin
##
%if %{pkg_rebrand}
%package rebrand
Summary:    Revisor Rebranding Fedora Utilies
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}, revisor-gui = %{version}-%{release}

%description rebrand
Utilities for Revisor to support rebranding Fedora
%endif

##
## Revisor Re-Use Installer Images plugin
##
%if %{pkg_reuseinstaller}
%package reuseinstaller
Summary:    Revisor Plugin to enable Reusing existing installer images
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}

%description reuseinstaller
Revisor Plugin to enable Reusing existing installer images
%endif

##
## Revisor Server plugin
##
%if %{pkg_server}
%package server
Summary:    Revisor Server
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}

%description server
Utilities for Revisor to support rebranding Fedora
%endif

##
## Fedora Unity Configuration and Scripts for Revisor
##
%if %{pkg_unity}
%package unity
Summary:    Fedora Unity Configuration and Scripts for Revisor
Group:      Applications/System
Requires:   revisor-cli

%description unity
The configuration files and scripts Fedora Unity uses with
Revisor to create Re-Spins and do testing.
%endif

##
## Fedora Unity Configuration and Scripts for Revisor
##
%if %{pkg_unity_scripts}
%package unity-scripts
Summary:    Fedora Unity Configuration and Scripts for Revisor
Group:      Applications/System
Requires:   revisor-cli

%description unity-scripts
The configuration files and scripts Fedora Unity uses with
Revisor to create Re-Spins and do testing.
%endif

##
## Revisor virtualization plugin
##
%if %{pkg_virt}
%package virt
Summary:    Revisor Virtualization Media Features
Group:      Applications/System
Requires:   python-virtinst, revisor-cli = %{version}-%{release}

%description virt
Revisor Virtualization Media Features for provisioning virtual guests
%endif

##
## Revisor WUI
##
%if %{pkg_wui}
%package wui
Summary:    Revisor WUI
Group:      Applications/System
Requires:   revisor-cli = %{version}-%{release}

%description wui
This is the Revisor Web User Interface package
%endif

%prep
%setup -q
%patch100 -p1
%patch101 -p1
%patch102 -p1

%build
%configure
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
install -m 755 %{SOURCE100} $RPM_BUILD_ROOT/usr/lib/revisor/scripts/F13-buildinstall

%if ! %{pkg_comps}
    rm -rf %{buildroot}/%{_datadir}/revisor/comps
    rm -rf %{buildroot}/%{_datadir}/revisor/comps-cleanup.xsl
%endif

%if ! %{pkg_cobbler}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modcobbler
%endif

%if ! %{pkg_composer}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modcomposer
%endif

%if ! %{pkg_delta}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/moddelta
%endif

%if ! %{pkg_hub}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modhub
%endif

%if ! %{pkg_isolinux}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modisolinux
%endif

%if ! %{pkg_jigdo}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modjigdo
%endif

%if ! %{pkg_mock}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modmock
%endif

%if ! %{pkg_rebrand}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modrebrand
%endif

%if ! %{pkg_reuseinstaller}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modreuseinstaller
%endif

%if ! %{pkg_server}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modserver
%endif

%if ! %{pkg_unity}
    rm -rf %{buildroot}/%{_sysconfdir}/revisor-unity/
    rm -rf %{buildroot}/%{_datadir}/revisor/unity/
%endif

%if ! %{pkg_unity_scripts}
    rm -rf %{buildroot}/%{_datadir}/revisor/unity/scripts/
%endif

%if ! %{pkg_virt}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modvirt
%endif

%if ! %{pkg_wui}
    rm -rf %{buildroot}/%{python_sitelib}/revisor/modwui
%endif

desktop-file-install --vendor="fedora"              \
  --delete-original                                 \
  --dir=%{buildroot}%{_datadir}/applications        \
  %{buildroot}/%{_datadir}/applications/revisor.desktop

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)

%files cli
%defattr(-,root,root,-)
%doc README NEWS AUTHORS COPYING
%doc %{_mandir}/man5/*
%doc %{_mandir}/man8/*
%dir %{_datadir}/revisor
%dir %{python_sitelib}/revisor
%{python_sitelib}/revisor/*.py
%{python_sitelib}/revisor/*.pyc
%{python_sitelib}/revisor/*.pyo
%{_bindir}/*
%{_sbindir}/*
%dir %{_prefix}/lib/revisor
%dir %{_prefix}/lib/revisor/scripts
%dir %{_sysconfdir}/revisor
%dir %{_sysconfdir}/revisor/conf.d
%config(noreplace) %{_sysconfdir}/revisor/revisor.conf
%config(noreplace) %{_sysconfdir}/revisor/conf.d/*
%config(noreplace) %{_sysconfdir}/pam.d/*
%config(noreplace) %{_sysconfdir}/security/console.apps/*
%{_datadir}/locale/*/LC_MESSAGES/revisor.mo
%defattr(0755,root,root,-)
%{_prefix}/lib/revisor/scripts/*

%if %{pkg_comps}
%files comps
%defattr(-,root,root,-)
%dir %{_datadir}/revisor/comps/
%{_datadir}/revisor/comps/*
%{_datadir}/revisor/comps-cleanup.xsl
%endif

%if %{pkg_cobbler}
%files cobbler
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modcobbler
%{python_sitelib}/revisor/modcobbler/*.py
%{python_sitelib}/revisor/modcobbler/*.pyc
%{python_sitelib}/revisor/modcobbler/*.pyo
%endif

%if %{pkg_composer}
%files composer
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modcomposer
%{python_sitelib}/revisor/modcomposer/*.py
%{python_sitelib}/revisor/modcomposer/*.pyc
%{python_sitelib}/revisor/modcomposer/*.pyo
%endif

%if %{pkg_delta}
%files delta
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/moddelta
%{python_sitelib}/revisor/moddelta/*.py
%{python_sitelib}/revisor/moddelta/*.pyc
%{python_sitelib}/revisor/moddelta/*.pyo
%endif

%files gui
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modgui
%{python_sitelib}/revisor/modgui/*.py
%{python_sitelib}/revisor/modgui/*.pyc
%{python_sitelib}/revisor/modgui/*.pyo
%dir %{_datadir}/revisor/ui
%dir %{_datadir}/revisor/pixmaps
%{_datadir}/revisor/ui/*
%{_datadir}/revisor/pixmaps/*
%{_datadir}/pixmaps/*
%{_datadir}/applications/*.desktop

%if %{pkg_hub}
%files hub
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modhub
%{python_sitelib}/revisor/modhub/*.py
%{python_sitelib}/revisor/modhub/*.pyc
%{python_sitelib}/revisor/modhub/*.pyo
%endif

%if %{pkg_isolinux}
%files isolinux
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modisolinux
%{python_sitelib}/revisor/modisolinux/*.py
%{python_sitelib}/revisor/modisolinux/*.pyc
%{python_sitelib}/revisor/modisolinux/*.pyo
%endif

%if %{pkg_jigdo}
%files jigdo
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modjigdo
%{python_sitelib}/revisor/modjigdo/*.py
%{python_sitelib}/revisor/modjigdo/*.pyc
%{python_sitelib}/revisor/modjigdo/*.pyo
%endif

%if %{pkg_mock}
%files mock
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modmock
%{python_sitelib}/revisor/modmock/*.py
%{python_sitelib}/revisor/modmock/*.pyc
%{python_sitelib}/revisor/modmock/*.pyo
%endif

%if %{pkg_rebrand}
%files rebrand
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modrebrand
%{python_sitelib}/revisor/modrebrand/*.py
%{python_sitelib}/revisor/modrebrand/*.pyc
%{python_sitelib}/revisor/modrebrand/*.pyo
%endif

%if %{pkg_reuseinstaller}
%files reuseinstaller
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modreuseinstaller
%{python_sitelib}/revisor/modreuseinstaller/*.py
%{python_sitelib}/revisor/modreuseinstaller/*.pyc
%{python_sitelib}/revisor/modreuseinstaller/*.pyo
%endif

%if %{pkg_server}
%files server
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modserver
%{python_sitelib}/revisor/modserver/*.py
%{python_sitelib}/revisor/modserver/*.pyc
%{python_sitelib}/revisor/modserver/*.pyo
%endif

%if %{pkg_unity}
%files unity
%defattr(-,root,root,-)
%dir %{_sysconfdir}/revisor-unity
%dir %{_sysconfdir}/revisor-unity/conf.d
%config(noreplace) %{_sysconfdir}/revisor-unity/*.conf
%config(noreplace) %{_sysconfdir}/revisor-unity/conf.d/*
%dir %{_datadir}/revisor/unity/
%{_datadir}/revisor/unity/*.*
%endif

%if %{pkg_unity_scripts}
%files unity-scripts
%defattr(-,root,root,-)
%{_datadir}/revisor/unity/scripts/
%endif

%if %{pkg_virt}
%files virt
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modvirt
%{python_sitelib}/revisor/modvirt/*.py
%{python_sitelib}/revisor/modvirt/*.pyc
%{python_sitelib}/revisor/modvirt/*.pyo
%endif

%if %{pkg_wui}
%files wui
%defattr(-,root,root,-)
%dir %{python_sitelib}/revisor/modwui
%{python_sitelib}/revisor/modwui/*.py
%{python_sitelib}/revisor/modwui/*.pyc
%{python_sitelib}/revisor/modwui/*.pyo
%endif

%changelog
* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Fri Jun 04 2010 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.2-1
- Fix os not being imported (#541443)

* Tue Nov 24 2009 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.1.8-2
- Fix configuration file issues
- Better estimation for the size of a tree that is to become an iso
- Huge improvements to package ordering
- Exclude boot.iso from installation media iso files

* Mon Sep 7 2009 Jonathan Steffan <jon a fedoraunity.org> 2.1.8-2
- Remove rhpl
- Add s-c-keyboard Requires

* Thu Feb 25 2009 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.1.3-1
- Add modmock, modhub, modcomposer
- Rebuild for Fedora 10
- Include modisolinux and modreuseinstaller

* Wed Oct 22 2008 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.1.2-2
- Fix anaconda removing splittree.py
- Latest rebuild
- Minor bugfixes (#344 pkgorder traceback)
- Add SELinux Check

* Tue Jul 01 2008 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.1.1-5
- Fix running GUI
- Add check for architecture composing
- Bugfixes in live media creation
- Add bluray disc support
- F-9 Release

* Wed Jan 30 2008 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.1.0-1rc5
- Add Rescue Image capabilities
- Add modserver into package
- Remove conflicts
- Updates
- Let's not build revisor-cobbler on ppc/ppc64

* Thu Dec 20 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.1.0-1rc2
- Updates to many components related to plugins and kickstart

* Wed Nov 07 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.1.0-1rc1
- import piruterrors
- Minor fixes related to respinning Fedora for release
- Applied patch from Alexander Todorov for filtering comps
- Applied patch from Alexander Todorov to get_comps() failing when comps not tidy
- Move GUI to it's own package
- API changes!
- Point at Everything, not Fedora (from 2.0.5-13)
- Add in ignore_list for pkglist_required() (from 2.0.5-13)
- Catch a Bob Jensen Corner Case (from 2.0.5-13)
- Minor bugfixes in packaging (from 2.0.5-13)
- Other minor fixes (from 2.0.5-13)

* Sat Oct 20 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.5-5
- Update spec for release

* Tue Oct 02 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.5-3
- Bugfixes to x86_64 packageSack creation
- Bugfixes

* Fri Sep 07 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.4.3-7
- Bugfixes
- Removed pungi dependency
- Added kickstart interfacing for pykickstart API differences
- Enable Revisor to run in CLI mode on Enterprise Linux 5
- Split comps in their own package
- Add rebrand module
- Fixed pkgorder, copy_dir
- Development release

* Thu Aug 09 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.4.2-1
- Added Source RPM Tree for Installation Media
- Rebased livecd-tools and created/submitted the necessary patches
- Added pre-alpha jigdo sub-package
- Disable jigdo, virt and dual media compose for release
- Lots of bug fixes
- Fixed up some features

* Thu Jul 26 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.4.2-1rc1
- Adding a workaround fix for yum issues

* Tue Jul 10 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.4.1-2
- Trivial specfile change
- Added one for one delta suport

* Sun Jul 01 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.4.1-1rc2
- Adding cobbler support for CLI mode
- Fixing pkgorder issue
- Fixing inefficient pkgorder
- Adding Enterprise Linux configuration files
- Moving some packages to be suggested instead of required
- Fixed progress bar during ISO creation
- Fixed SHA1SUM file not having all ISOs
- Adding full support for installation tree and cleanup

* Wed Jun 27 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.4.0-1
- Bugfixes from 2.0.3.x
- Start of all the new features of 2.0.4

* Sun Jun 24 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.3.12-1
- Removed excludearchs ppc, ppc64 and added some logic to the spec file
  including a patch to disable livecd composure.
- Fixed bug in repository configuration
- Re-enabled CLI

* Sat Jun 23 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.3.11-1
- Adding comps-f7 to our distribution
- Removing pungi configuration files
- Fixed a major bug in unlinking / unmounting the left-overs of a previous
  live media run.
- Enabled translation
- Added ExcludeArch: ppc, ppc64. Our dependency livecd-tools is not available
  for these archs.

* Sun Jun 17 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.3.10-1
- Final round of fixes for 2.0.3.x
- Added requirement for fedora-release >= 7

* Sun Jun 10 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.3.9-1
- Bugfixes, more bugfixes

* Thu Jun 07 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.3.8-1
- Updated to 2.0.3.8
- More major bugfixes

* Tue Jun 05 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.3.7-1
- Major bugfixes and speed improvements - tagging for reference purposes
- Added /etc/revisor/comps-fc6.xml as a %%config file

* Thu May 31 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.3.6-1
- Updated with all combined changes for release
- Fixed up configs
- Added fc6 comps data
- Bug fixes from LinuxTag

* Wed May 30 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.3-1
- Repackage for release

* Thu May 24 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.2-3
- Added desktop-file-install and needed BR
- Updated for COPYING
- Updated revisor.desktop

* Thu May 17 2007 Jeroen van meeuwen <kanarip a fedoraunity.org> 2.0.2-2
- Rebuild

* Tue May 08 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.2-1
- Final beta version for RH Summit 2007, San Diego

* Mon May 07 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.1-5
- Fixed configuration files
- New files added

* Mon Apr 30 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.1-4
- Fixed symlink to consolehelper relative path instead of absolute
  path in Makefile, rather then specfile
- Added missing s-c-kickstart dep
- Fixed shipped config files to be more targeted for end users

* Tue Apr 17 2007 Jef Spaleta <jspaleta@gmail.com> 2.0.1-3
- Specfile cleanup for fedora package submission review
- remove makeinstall macro
- add usermode and pam requires
- removed desktop-update-database scriptlets and associated deps

* Mon Apr 16 2007 Jeroen van Meeuwen <kanarip a fedoraunity.org> 2.0.1-2
- Corrected some file locations
- Build for F7

* Wed Apr 11 2007 Jonathan Steffan <jon a fedoraunity.org> 2.0.1-1
- Updated for the new revisor 2.x

* Sat Feb 17 2007 Jonathan Steffan <jon a fedoraunity.org> 1.0.2-1
- Updated config (in)sanity
- Added some configuration options

* Thu Feb 15 2007 Jonathan Steffan <jon a fedoraunity.org> 1.0.1-1
- Added a "Select All" button to help ease full distro Re-Spins

* Wed Feb 14 2007 Jonathan Steffan <jon a fedoraunity.org> 1.0-2
- Cleaned up code to include as little duplicate Pirut code as
  possible.
- Updated config file to default to mirrorlist

* Mon Feb 12 2007 Jonathan Steffan <jon a fedoraunity.org> 1.0-1
- Initial build based on pirutspin 1.0-1


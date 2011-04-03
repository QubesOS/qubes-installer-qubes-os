Name: qubes-logos
Summary: Icons and pictures
Version: 1
Release: 1
Group: System Environment/Base
Source0: qubes-logos-%{version}.tar.bz2
License: GPLv2 and LGPL
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
Obsoletes: fedora-logos
Obsoletes: redhat-logos
Provides: fedora-logos = 13-%{release}
Provides: redhat-logos = 13-%{release}
Provides: system-logos = %{version}-%{release}
Conflicts: kdebase <= 3.1.5
Conflicts: anaconda-images <= 10
Conflicts: redhat-artwork <= 5.0.5
# For _kde4_appsdir macro:
BuildRequires: kde-filesystem


%description
The qubes-logos package contains various image files which can be
used by the bootloader, anaconda, and other related tools.

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT

# should be ifarch i386
mkdir -p $RPM_BUILD_ROOT/boot/grub
install -p -m 644 bootloader/splash.xpm.gz $RPM_BUILD_ROOT/boot/grub/splash.xpm.gz
# end i386 bits

mkdir -p $RPM_BUILD_ROOT%{_datadir}/firstboot/themes/qubes
for i in firstboot/* ; do
  install -p -m 644 $i $RPM_BUILD_ROOT%{_datadir}/firstboot/themes/qubes
done

mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps/splash
for i in gnome-splash/* ; do
  install -p -m 644 $i $RPM_BUILD_ROOT%{_datadir}/pixmaps/splash
done

mkdir -p $RPM_BUILD_ROOT%{_kde4_appsdir}/ksplash/Themes/Leonidas/2048x1536
install -p -m 644 ksplash/SolarComet-kde.png $RPM_BUILD_ROOT%{_kde4_appsdir}/ksplash/Themes/Leonidas/2048x1536/logo.png

mkdir -p $RPM_BUILD_ROOT%{_datadir}/plymouth/themes/charge/
for i in plymouth/charge/* ; do
    install -p -m 644 $i $RPM_BUILD_ROOT%{_datadir}/plymouth/themes/charge/
done

(cd anaconda; make DESTDIR=$RPM_BUILD_ROOT install)

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc COPYING COPYING-kde-logo
%{_datadir}/firstboot/themes/*
%{_datadir}/anaconda/pixmaps/*
%{_datadir}/plymouth/themes/charge/*
%{_datadir}/pixmaps/splash/*
/usr/lib/anaconda-runtime/*.jpg
%{_kde4_appsdir}/ksplash/Themes/Leonidas/2048x1536/logo.png
# should be ifarch i386
/boot/grub/splash.xpm.gz
# end i386 bits

%changelog
* Tue Jan 13 2010 Tomasz Sterna <smoku@xiaoka.com> - 1
- Initial Qubes 1 Release package

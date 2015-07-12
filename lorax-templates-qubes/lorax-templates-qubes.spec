%if 0%{?qubes_builder}
%define _builddir %(pwd)/lorax-templates-qubes
%endif

Name:		lorax-templates-qubes
Version:	2.2
Release:	1%{?dist}
Summary:	Lorax templates for Qubes installation ISO

Group:		Applications/System
License:	GPLv2+
URL:		http://www.qubes-os.org/
Source0:	%{name}-%{version}.tar.bz2

#BuildRequires:	
Requires:	lorax
BuildArch:      noarch

%description
Lorax templates for Qubes installation ISO.

%prep
%if ! 0%{?qubes_builder}
%setup -q
%endif

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/usr/share/lorax-qubes
cp -r templates/* $RPM_BUILD_ROOT/usr/share/lorax-qubes/

%post
# pungi does not allow to specify alternative config, so must override the default one
if [ -r /etc/lorax/lorax.conf -a ! -r /etc/lorax/lorax-pre-qubes.conf ]; then
	mv /etc/lorax/lorax.conf /etc/lorax/lorax-pre-qubes.conf
fi

cat > /etc/lorax/lorax.conf << EOF
# Lorax configuration file
[lorax]
sharedir: /usr/share/lorax-qubes
EOF

%files
%defattr(-,root,root,-)
/usr/share/lorax-qubes


%changelog


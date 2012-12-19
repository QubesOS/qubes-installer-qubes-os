#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2011  Tomasz Sterna <tomek@xiaoka.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#

TOP := $(shell pwd)
RPMBUILD_DEFINES := --define "_rpmdir rpm/" --define "_sourcedir $(TOP)/rpm/SOURCES"

spec_version = $(shell rpm -q --qf "%{VERSION}\n" --specfile $(1)| head -1)
package = $(shell \
	mkdir -p rpm/SOURCES; \
	cd rpm/SOURCES; \
	rm -f $(1)-$(2)*; \
	ln -s ../../$(1) $(1)-$(2); \
	tar jcf $(1)-$(2).tar.bz2 --dereference --exclude-vcs $(1)-$(2); \
	rm $(1)-$(2) )

ANACONDA_VERSION := $(call spec_version,anaconda/anaconda.spec)
FIRSTBOOT_VERSION := $(call spec_version,firstboot/firstboot.spec)
QBSLOGOS_VERSION := $(call spec_version,qubes-logos/qubes-logos.spec)
QBSRELEASE_VERSION := $(call spec_version,qubes-release/qubes-release.spec)
REVISOR_VERSION := $(call spec_version,revisor/revisor.spec)

REVISOR_OPTS := --install-dvd
ifdef QUBES_RELEASE
    REVISOR_OPTS += --product-version="$(QUBES_RELEASE)"
endif

help:
	@echo "make rpms             <--- make all rpms and sign them";\
	    echo "make rpms_anaconda    <--- create binary rpms for Anaconda"; \
	    echo "make rpms_firstboot   <--- create binary rpms for Firstboot"; \
	    echo "make rpms_logos       <--- create binary rpms for Qubes Logos package"; \
	    echo "make rpms_release     <--- create binary rpms for Qubes Release package"; \
	    echo "make rpms_revisor     <--- create binary rpms for Revisor"; \
	    echo; \
	    echo "make update-repo      <-- copy newly generated rpms to installer yum repo";\
		echo "make iso              <== \o/";\
	    echo; \
		echo "make clean";\
	    echo; \
	    exit 0;

.PHONY: rpms rpms_anaconda rpms_firstboot rpms_logos rpms_release rpms_revisor \
	update-repo update-repo-testing clean

rpms: rpms_anaconda rpms_firstboot rpms_logos rpms_release rpms_revisor
	rpm --addsign `ls -d rpm/x86_64/*.rpm rpm/i686/*.rpm rpm/noarch/*.rpm 2>/dev/null`

rpms-dom0: rpms

rpms-vm:

rpm/SOURCES/anaconda-$(ANACONDA_VERSION).tar.bz2: anaconda anaconda/anaconda.spec
	$(call package,anaconda,$(ANACONDA_VERSION))

rpm/SOURCES/firstboot-$(FIRSTBOOT_VERSION).tar.bz2: firstboot firstboot/firstboot.spec
	$(call package,firstboot,$(FIRSTBOOT_VERSION))

rpm/SOURCES/qubes-logos-$(QBSLOGOS_VERSION).tar.bz2: qubes-logos qubes-logos/qubes-logos.spec
	$(call package,qubes-logos,$(QBSLOGOS_VERSION))

rpm/SOURCES/qubes-release-$(QBSRELEASE_VERSION).tar.bz2: qubes-release qubes-release/qubes-release.spec
	$(call package,qubes-release,$(QBSRELEASE_VERSION))

rpms_anaconda: rpm/SOURCES/anaconda-$(ANACONDA_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb anaconda/anaconda.spec

rpms_firstboot: rpm/SOURCES/firstboot-$(FIRSTBOOT_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb firstboot/firstboot.spec

rpms_logos: rpm/SOURCES/qubes-logos-$(QBSLOGOS_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb qubes-logos/qubes-logos.spec

rpms_release: rpm/SOURCES/qubes-release-$(QBSRELEASE_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb qubes-release/qubes-release.spec

rpms_revisor: revisor/revisor-$(REVISOR_VERSION).tar.gz revisor/revisor.spec
	rpmbuild --define "_rpmdir rpm/" --define "_sourcedir $(TOP)/revisor" -bb revisor/revisor.spec

RPMS = rpm/noarch/qubes-logos-$(QBSLOGOS_VERSION)-*.rpm \
	rpm/noarch/qubes-release-$(QBSRELEASE_VERSION)-*.rpm \
	rpm/noarch/qubes-release-notes-$(QBSRELEASE_VERSION)-*.rpm \
	rpm/noarch/revisor*-$(REVISOR_VERSION)-*.rpm \
	rpm/x86_64/anaconda-$(ANACONDA_VERSION)-*.rpm \
	rpm/x86_64/firstboot-$(FIRSTBOOT_VERSION)-*.rpm

update-repo:
	@ln -f $(RPMS) yum/installer/rpm/
	@echo "--> Updating Installer repos..."
	@(cd yum && ./update_repo.sh)

update-repo-current:
	ln -f $(RPMS) ../yum/current-release/current/dom0/rpm/

update-repo-current-testing:
	ln -f $(RPMS) ../yum/current-release/current-testing/dom0/rpm/

update-repo-unstable:
	ln -f $(RPMS) ../yum/current-release/unstable/dom0/rpm/

iso:
	cp rpm_verify /usr/local/bin/
	ln -sf `pwd` /tmp/qubes-installer
	revisor --cli --config=conf/qubes-install.conf --model=qubes-x86_64 $(REVISOR_OPTS) -d99
	isohybrid build/ISO/qubes-x86_64/iso/*.iso
	rpm_verify build/work/revisor-install/*/qubes-x86_64/x86_64/os/Packages/*.rpm

clean-repos:
	@echo "--> Removing old rpms from the installer repos..."
	@(cd yum && ./clean_repos.sh)

clean:
	sudo rm -fr build/*
	rm -fr rpm/SOURCES/*.bz2
	rm -fr rpm/noarch/*.rpm
	rm -fr rpm/x86_64/*.rpm

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
QBSRELEASE_VERSION := $(call spec_version,qubes-release/qubes-release.spec)
LORAXQBS_VERSION := $(call spec_version,lorax-templates-qubes/lorax-templates-qubes.spec)
PUNGI_VERSION := $(call spec_version,pungi/pungi.spec)
PYKICKSTART_VERSION := $(call spec_version,pykickstart/pykickstart.spec)

PUNGI_OPTS := --nosource --nodebuginfo --nogreedy --all-stages
ifdef QUBES_RELEASE
    ISO_VERSION := $(QUBES_RELEASE)
    PUNGI_OPTS += --isfinal
else
    ISO_VERSION := $(shell date +%Y%m%d)
endif
PUNGI_OPTS += --ver="$(ISO_VERSION)"

help:
	@echo "make rpms             <--- make all rpms and sign them";\
	    echo "make rpms_anaconda    <--- create binary rpms for Anaconda"; \
	    echo "make rpms_firstboot   <--- create binary rpms for Firstboot"; \
	    echo "make rpms_release     <--- create binary rpms for Qubes Release package"; \
	    echo; \
	    echo "make update-repo      <-- copy newly generated rpms to installer yum repo";\
		echo "make iso              <== \o/";\
	    echo; \
		echo "make clean";\
	    echo; \
	    exit 0;

.PHONY: rpms rpms_anaconda rpms_firstboot rpms_release rpms_lorax \
	rpms_pungi rpms_pykickstart \
	update-repo update-repo-testing clean iso

rpms: rpms_anaconda rpms_firstboot rpms_release rpms_lorax rpms_pungi rpms_pykickstart
	rpm --addsign `ls -d rpm/x86_64/*.rpm rpm/i686/*.rpm rpm/noarch/*.rpm 2>/dev/null`

rpms-dom0: rpms

rpms-vm:

rpm/SOURCES/anaconda-$(ANACONDA_VERSION).tar.bz2: anaconda anaconda/anaconda.spec
	$(call package,anaconda,$(ANACONDA_VERSION))

rpm/SOURCES/lorax-templates-qubes-$(LORAXQBS_VERSION).tar.bz2: lorax-templates-qubes lorax-templates-qubes/lorax-templates-qubes.spec
	$(call package,lorax-templates-qubes,$(LORAXQBS_VERSION))

rpm/SOURCES/firstboot-$(FIRSTBOOT_VERSION).tar.bz2: firstboot firstboot/firstboot.spec
	$(call package,firstboot,$(FIRSTBOOT_VERSION))

rpm/SOURCES/qubes-release-$(QBSRELEASE_VERSION).tar.bz2: qubes-release qubes-release/qubes-release.spec conf/comps-qubes.xml
	$(call package,qubes-release,$(QBSRELEASE_VERSION))
	cp conf/comps-qubes.xml rpm/SOURCES/Qubes-comps.xml

rpms_anaconda: rpm/SOURCES/anaconda-$(ANACONDA_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb anaconda/anaconda.spec

rpms_lorax: rpm/SOURCES/lorax-templates-qubes-$(LORAXQBS_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb lorax-templates-qubes/lorax-templates-qubes.spec

rpms_pungi: pungi/pungi-$(PUNGI_VERSION).tar.bz2 pungi/pungi.spec
	rpmbuild --define "_rpmdir rpm/" --define "_sourcedir $(TOP)/pungi" -bb pungi/pungi.spec

rpms_pykickstart: pykickstart/pykickstart-$(PYKICKSTART_VERSION).tar.gz pykickstart/pykickstart.spec
	rpmbuild --define "_rpmdir rpm/" --define "_sourcedir $(TOP)/pykickstart" -bb pykickstart/pykickstart.spec

rpms_firstboot: rpm/SOURCES/firstboot-$(FIRSTBOOT_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb firstboot/firstboot.spec

rpms_release: rpm/SOURCES/qubes-release-$(QBSRELEASE_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb qubes-release/qubes-release.spec

RPMS = \
	rpm/noarch/qubes-release-$(QBSRELEASE_VERSION)-*.rpm \
	rpm/noarch/qubes-release-notes-$(QBSRELEASE_VERSION)-*.rpm \
	rpm/noarch/lorax-templates-qubes-$(LORAXQBS_VERSION)-*.rpm \
	rpm/noarch/pungi-$(PUNGI_VERSION)-*.rpm \
	rpm/noarch/pykickstart-$(PYKICKSTART_VERSION)-*.rpm \
	rpm/x86_64/anaconda*-$(ANACONDA_VERSION)-*.rpm \
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
	ln -sf `pwd` /tmp/qubes-installer
	createrepo -q -g ../../conf/comps-qubes.xml --update yum/qubes-dom0
	mkdir -p work
	pushd work && pungi --name=Qubes  $(PUNGI_OPTS) -c $(PWD)/conf/qubes-kickstart.cfg && popd
	# Move result files to known-named directories
	mkdir -p build/ISO/qubes-x86_64/iso build/work
	mv work/$(ISO_VERSION)/x86_64/iso/*-DVD.iso build/ISO/qubes-x86_64/iso/
	rm -rf build/work/$(ISO_VERSION)
	mv work/$(ISO_VERSION)/x86_64/os build/work/$(ISO_VERSION)
	chown --reference=Makefile -R build yum
	rm -rf work

clean-repos:
	@echo "--> Removing old rpms from the installer repos..."
	@(cd yum && ./clean_repos.sh)

clean:
	sudo rm -fr build/*
	rm -fr rpm/SOURCES/*.bz2
	rm -fr rpm/noarch/*.rpm
	rm -fr rpm/x86_64/*.rpm

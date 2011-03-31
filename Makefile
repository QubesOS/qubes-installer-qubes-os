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

spec_version = $(shell sed -n '/^Version:/s/.*:[ \t]\+//p' $(1))
package = $(shell \
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

help:
	@echo "make rpms             <--- make all rpms and sign them";\
	    echo "make rpms_anaconda    <--- create binary rpms for Anaconda"; \
	    echo "make rpms_firstboot   <--- create binary rpms for Firstboot"; \
	    echo "make rpms_logos       <--- create binary rpms for Qubes Logos package"; \
	    echo "make rpms_release     <--- create binary rpms for Qubes Release package"; \
	    echo "make rpms_revisor     <--- create binary rpms for Revisor"; \
	    echo; \
	    echo "make update-repo      <-- copy newly generated rpms to qubes yum repo";\
	    echo "make update-repo-testing  <-- same, but to "testing" repo";\
	    echo "make clean            <--- clean all the binary files";\
	    exit 0;

.PHONY: rpms rpms_anaconda rpms_firstboot rpms_logos rpms_release rpms_revisor \
	update-repo update-repo-testing clean

rpms: rpms_anaconda rpms_firstboot rpms_logos rpms_release rpms_revisor
	rpm --addsign rpm/x86_64/*.rpm
	(if [ -d rpm/i686 ] ; then rpm --addsign rpm/i686/*.rpm; fi)

rpm/SOURCES/anaconda-$(ANACONDA_VERSION).tar.bz2: anaconda
	$(call package,anaconda,$(ANACONDA_VERSION))

rpm/SOURCES/firstboot-$(FIRSTBOOT_VERSION).tar.bz2: firstboot
	$(call package,firstboot,$(FIRSTBOOT_VERSION))

rpm/SOURCES/qubes-logos-$(QBSLOGOS_VERSION).tar.bz2: qubes-logos
	$(call package,qubes-logos,$(QBSLOGOS_VERSION))

rpm/SOURCES/qubes-release-$(QBSRELEASE_VERSION).tar.bz2: qubes-release
	$(call package,qubes-release,$(QBSRELEASE_VERSION))

rpms_anaconda: rpm/SOURCES/anaconda-$(ANACONDA_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb anaconda/anaconda.spec

rpms_firstboot: rpm/SOURCES/firstboot-$(FIRSTBOOT_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb firstboot/firstboot.spec

rpms_logos: rpm/SOURCES/qubes-logos-$(QBSLOGOS_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb qubes-logos/qubes-logos.spec

rpms_release: rpm/SOURCES/qubes-release-$(QBSRELEASE_VERSION).tar.bz2
	rpmbuild $(RPMBUILD_DEFINES) -bb qubes-release/qubes-release.spec

rpms_revisor: rpm/SOURCES/revisor-$(REVISOR_VERSION).tar.bz2
	rpmbuild --define "_rpmdir rpm/" --define "_sourcedir $(TOP)/revisor" -bb revisor/revisor.spec

update-repo:
	ln -f rpm/x86_64/qubes-gui-vm-*.rpm ../yum/r1/appvm/rpm/
	ln -f rpm/x86_64/qubes-gui-vm-*.rpm ../yum/r1/netvm/rpm/
	ln -f rpm/x86_64/qubes-vchan-vm-*.rpm ../yum/r1/appvm/rpm/
	ln -f rpm/x86_64/qubes-vchan-vm-*.rpm ../yum/r1/netvm/rpm/
	ln -f rpm/x86_64/qubes-gui-dom0-*.rpm ../yum/r1/dom0/rpm/

update-repo-testing:
	ln -f rpm/x86_64/qubes-gui-vm-*.rpm ../yum/r1-testing/appvm/rpm/
	ln -f rpm/x86_64/qubes-gui-vm-*.rpm ../yum/r1-testing/netvm/rpm/
	ln -f rpm/x86_64/qubes-vchan-vm-*.rpm ../yum/r1-testing/appvm/rpm/
	ln -f rpm/x86_64/qubes-vchan-vm-*.rpm ../yum/r1-testing/netvm/rpm/
	ln -f rpm/x86_64/qubes-gui-dom0-*.rpm ../yum/r1-testing/dom0/rpm/

clean:
	(cd common; $(MAKE) clean)
	(cd gui-agent; $(MAKE) clean)
	(cd gui-common; $(MAKE) clean)
	(cd gui-daemon; $(MAKE) clean)
	(cd shmoverride; $(MAKE) clean)
	$(MAKE) -C pulse clean
	(cd xf86-input-mfndev; if [ -e Makefile ] ; then $(MAKE) distclean; fi; ./bootstrap --clean || echo )
	(cd vchan; $(MAKE) clean)
	(cd vchan/event_channel; ./cleanup.sh || echo)
	(cd vchan/u2mfn; ./cleanup.sh || echo)
	$(MAKE) -C relaxed_xf86ValidateModes clean


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

ISO_INSTALLER ?= 1
ISO_LIVEUSB ?= 0

PUNGI_OPTS := --nosource --nodebuginfo --nogreedy --all-stages
ifdef QUBES_RELEASE
    ISO_VERSION := $(QUBES_RELEASE)
    PUNGI_OPTS += --isfinal
else
    ISO_VERSION := $(shell date +%Y%m%d)
endif
PUNGI_OPTS += --ver="$(ISO_VERSION)"

INSTALLER_KICKSTART ?= $(PWD)/conf/qubes-kickstart.cfg
LIVE_KICKSTART ?= $(PWD)/conf/liveusb.ks

help:
	@echo "make iso              <== \o/";\
	    echo; \
		echo "make clean";\
	    echo; \
	    exit 0;

.PHONY:	clean clean-repos iso iso-prepare iso-installer iso-liveusb

ifeq ($(ISO_INSTALLER),1)
iso: iso-installer
endif
ifeq ($(ISO_LIVEUSB),1)
iso: iso-liveusb
endif

iso-prepare:
	ln -nsf `pwd` /tmp/qubes-installer
	createrepo -q -g ../../conf/comps-qubes.xml --update yum/qubes-dom0

iso-installer: iso-prepare
	mkdir -p work
	pushd work && pungi --name=Qubes  $(PUNGI_OPTS) -c $(INSTALLER_KICKSTART) && popd
	# Move result files to known-named directories
	mkdir -p build/ISO/qubes-x86_64/iso
	mv work/$(ISO_VERSION)/x86_64/iso/*-DVD*.iso build/ISO/qubes-x86_64/iso/
	rm -rf build/work
	mv work build/work
	chown --reference=Makefile -R build yum
	rm -rf work

iso-liveusb: $(LIVE_KICKSTART) iso-prepare
	mkdir -p work
	pushd work && ../livecd-creator-qubes --debug --product='Qubes OS' --title="Qubes OS $(ISO_VERSION)" --fslabel="Qubes-$(ISO_VERSION)-x86_64-LIVE" --config $(LIVE_KICKSTART) && popd
	# Move result files to known-named directories
	mkdir -p build/ISO/qubes-x86_64/iso build/work
	mv work/*.iso build/ISO/qubes-x86_64/iso/
	chown --reference=Makefile -R build yum
	rm -rf work

clean-repos:
	@echo "--> Removing old rpms from the installer repos..."
	@(cd yum && ./clean_repos.sh)

clean:
	sudo rm -fr build/*

get-sources:
	$(MAKE) -C livecd-tools get-sources

verify-sources:
	$(MAKE) -C livecd-tools verify-sources

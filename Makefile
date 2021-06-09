#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2011  Tomasz Sterna <tomek@xiaoka.com>
# Copyright (C) 2019  Frédéric Pierret <frederic.pierret@qubes-os.org>
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
DIST ?= fc32
DIST_VER = $(subst fc,,$(DIST))

INSTALLER_DIR ?= $(PWD)

ISO_INSTALLER ?= 1
INSTALLER_KICKSTART ?= $(INSTALLER_DIR)/conf/qubes-kickstart.cfg

ISO_LIVEUSB ?= 0
LIVE_KICKSTART ?= $(INSTALLER_DIR)/conf/liveusb.ks

CREATEREPO := $(shell which createrepo_c createrepo 2>/dev/null |head -1)

ifdef QUBES_RELEASE
	ISO_VERSION := $(QUBES_RELEASE)
	LORAX_OPTS += --isfinal
else
	ISO_VERSION ?= $(shell date +%Y%m%d)
endif

ifneq (,$(ISO_FLAVOR))
ISO_NAME := Qubes-$(ISO_VERSION)-$(ISO_FLAVOR)-x86_64
else
ISO_NAME := Qubes-$(ISO_VERSION)-x86_64
endif
ISO_VOLID := $(shell echo $(ISO_NAME) | tr a-z A-Z | tr -s -c [:alnum:]'\n' - | head -c 32)
BASE_DIR := $(INSTALLER_DIR)/work/$(ISO_VERSION)/x86_64

DNF := /usr/bin/dnf
DNF_ROOT := /tmp/dnfroot
DNF_REPO := $(DNF_ROOT)/etc/yum.repos.d/installer.repo
DNF_PACKAGES := $(DNF_ROOT)/tmp/packages.list
DNF_OPTS := -y --releasever=$(DIST_VER) --installroot=$(DNF_ROOT)
DNF_OPTS += --downloaddir=$(BASE_DIR)/os/Packages --downloadonly install

LORAX := /usr/sbin/lorax
LORAX_OPTS := --product "Qubes OS" --variant "qubes" --macboot --force --rootfs-size=4

LORAX_OPTS += --version "$(ISO_VERSION)" --release "Qubes OS $(ISO_VERSION)" --volid $(ISO_VOLID)
LORAX_OPTS += --workdir $(INSTALLER_DIR)/work/work/x86_64 --logfile $(INSTALLER_DIR)/work/logs/lorax-x86_64.log
LORAX_OPTS += --repo $(DNF_REPO) --skip-branding

ifeq ($(ISO_USE_KERNEL_LATEST),1)
LORAX_OPTS += --installpkgs kernel-latest --excludepkgs kernel
endif

MKISOFS := /usr/bin/xorriso -as mkisofs
# common mkisofs flags
MKISOFS_OPTS := -v -U -J --joliet-long -R -T -m repoview -m boot.iso
# x86 boot args
MKISOFS_OPTS += -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table
# efi boot args
MKISOFS_OPTS += -eltorito-alt-boot -e images/efiboot.img -no-emul-boot


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
	rm -rf work && mkdir work
	rm -rf $(DNF_ROOT)

	# Copy the comps file
	cp $(INSTALLER_DIR)/conf/comps-dom0.xml /tmp/comps.xml
	if [ "$(ISO_USE_KERNEL_LATEST)" == 1 ]; then \
		sed -i 's#optional">kernel-latest#mandatory">kernel-latest#g' /tmp/comps.xml; \
	fi;

	# Update installer repo
	$(CREATEREPO) -q -g /tmp/comps.xml --update yum/qubes-dom0

	# Destination directory for RPM
	mkdir -p $(BASE_DIR)/os/Packages

	# Copy Fedora key to DNF installroot
	mkdir -p $(DNF_ROOT)/etc/pki/rpm-gpg
	cp $(INSTALLER_DIR)/qubes-release/RPM-GPG-KEY-fedora-$(DIST_VER)-primary $(DNF_ROOT)/etc/pki/rpm-gpg

	# Provide qubes-release/conf for Qubes keys
	mkdir -p $(DNF_ROOT)/tmp/qubes-installer
	ln -nsf $(INSTALLER_DIR) $(DNF_ROOT)/tmp/qubes-installer

	# Legacy conf using this folder
	ln -nsf $(INSTALLER_DIR) /tmp/qubes-installer

	# Extract repos conf and packages from kickstart
	mkdir -p $(DNF_ROOT)/etc/yum.repos.d
	$(INSTALLER_DIR)/scripts/ksparser --ks $(INSTALLER_KICKSTART) --extract-repo-conf-to $(DNF_REPO) --extract-packages-to $(DNF_PACKAGES)

iso-installer-gather:
	umask 022; $(DNF) $(DNF_OPTS) $(shell cat $(DNF_PACKAGES))
	pushd $(BASE_DIR)/os/ && $(CREATEREPO) -q -g /tmp/comps.xml .

iso-installer-lorax:
	$(LORAX) $(LORAX_OPTS) $(BASE_DIR)/os

iso-installer-mkisofs:
	mkdir -p $(BASE_DIR)/iso/
	chmod og+rX -R $(BASE_DIR)/os/
	$(MKISOFS) $(MKISOFS_OPTS) -V $(ISO_VOLID) -o $(BASE_DIR)/iso/$(ISO_NAME).iso $(BASE_DIR)/os/
	/usr/bin/isohybrid -u $(BASE_DIR)/iso/$(ISO_NAME).iso
	/usr/bin/implantisomd5  $(BASE_DIR)/iso/$(ISO_NAME).iso

iso-installer: iso-prepare iso-installer-gather iso-installer-lorax iso-installer-mkisofs
	# Move result files to known-named directories
	mkdir -p build/ISO/qubes-x86_64/iso
	mv $(BASE_DIR)/iso/$(ISO_NAME).iso build/ISO/qubes-x86_64/iso/
	echo $(ISO_VERSION) > build/ISO/qubes-x86_64/iso/build_latest
	rm -rf build/work
	mv work build/work
	chown --reference=Makefile -R build yum
	rm -rf work

iso-liveusb: $(LIVE_KICKSTART) iso-prepare
	pushd work && $(INSTALLER_DIR)/scripts/livecd-creator-qubes --debug --product='Qubes OS' --title="Qubes OS $(ISO_VERSION)" --fslabel="Qubes-$(ISO_VERSION)-x86_64-LIVE" --config $(LIVE_KICKSTART) && popd
	# Move result files to known-named directories
	mkdir -p build/ISO/qubes-x86_64/iso build/work
	mv work/*.iso build/ISO/qubes-x86_64/iso/
	chown --reference=Makefile -R build yum
	rm -rf work

clean-repos:
	@echo "--> Removing old rpms from the installer repos..."
	@(cd yum && ./clean_repos.sh)

clean:
	sudo rm -rf $(DNF_ROOT)
	sudo rm -fr build/*

get-sources:
	git submodule update --init --recursive

ifeq ($(ISO_LIVEUSB),1)
get-sources:
	$(MAKE) -C livecd-tools get-sources

verify-sources:
	$(MAKE) -C livecd-tools verify-sources
else
verify-sources:
	@true
endif

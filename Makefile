# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2022 Frédéric Pierret (fepitre) <frederic@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-2.0-or-later

DIST ?= fc37
DIST_VER = $(subst fc,,$(DIST))

INSTALLER_DIR ?= $(PWD)

ISO_INSTALLER ?= 1
INSTALLER_KICKSTART ?= $(INSTALLER_DIR)/conf/qubes-kickstart.cfg

ISO_LIVEUSB ?= 0
LIVE_KICKSTART ?= $(INSTALLER_DIR)/conf/liveusb.ks

CREATEREPO := $(shell which createrepo_c createrepo 2>/dev/null |head -1)

ifdef QUBES_RELEASE
	ISO_VERSION := $(QUBES_RELEASE)
endif
ISO_VERSION ?= $(shell date +%Y%m%d)

ifneq (,$(ISO_FLAVOR))
ISO_NAME := Qubes-$(ISO_VERSION)-$(ISO_FLAVOR)-x86_64
else
ISO_NAME := Qubes-$(ISO_VERSION)-x86_64
endif
ISO_VOLID := $(shell echo $(ISO_NAME) | tr a-z A-Z | tr -s -c [:alnum:]'\n' - | head -c 32)

BASE_DIR := $(INSTALLER_DIR)/work/$(ISO_VERSION)/x86_64
TMP_DIR := $(PWD)/work

DNF := /usr/bin/dnf
DNF_ROOT := /tmp/dnfroot
DNF_REPO := $(DNF_ROOT)/etc/yum.repos.d/installer.repo
DNF_PACKAGES := $(DNF_ROOT)/tmp/packages.list
DNF_OPTS := -y --releasever=$(DIST_VER) --installroot=$(DNF_ROOT) --config=$(DNF_ROOT)/etc/dnf/dnf.conf

LORAX := /usr/sbin/lorax
LORAX_PACKAGES := $(DNF_ROOT)/tmp/lorax_packages.list
LORAX_OPTS := --product "Qubes OS" --variant "qubes" --macboot --force --rootfs-size=4
LORAX_OPTS += --version "$(ISO_VERSION)" --release "Qubes OS $(ISO_VERSION)" --volid $(ISO_VOLID)
LORAX_OPTS += --workdir $(INSTALLER_DIR)/work/work/x86_64 --logfile $(INSTALLER_DIR)/work/logs/lorax-x86_64.log
LORAX_OPTS += --repo $(DNF_REPO) --skip-branding --disablerepo=fedora --disablerepo=fedora-updates --disablerepo=updates --disablerepo='qubes-*'

ifeq ($(ISO_USE_KERNEL_LATEST),1)
LORAX_OPTS += --installpkgs kernel-latest --excludepkgs kernel
endif

ifdef QUBES_RELEASE
	LORAX_OPTS += --isfinal
endif


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
	#
	# Prepare repositories
	#

	rm -rf $(TMP_DIR)
	rm -rf $(DNF_ROOT)

	# Copy the comps file
	mkdir -p $(TMP_DIR)
	cp $(INSTALLER_DIR)/meta-packages/comps/comps-dom0.xml $(TMP_DIR)/comps.xml
	if [ "$(ISO_USE_KERNEL_LATEST)" == 1 ]; then \
		sed -i 's#optional">kernel-latest#mandatory">kernel-latest#g' $(TMP_DIR)/comps.xml; \
	fi;

	# Legacy conf using this folder
	ln -nsf $(INSTALLER_DIR) /tmp/qubes-installer

	mkdir -p /tmp/qubes-installer/yum/installer/rpm
	rm -rf $(INSTALLER_DIR)/yum/installer/repodata
	$(CREATEREPO) -q -g $(TMP_DIR)/comps.xml yum/installer

	mkdir -p yum/qubes-dom0
	$(CREATEREPO) -q -g $(TMP_DIR)/comps.xml --update yum/qubes-dom0

	#
	# Prepare DNF
	#

	# Destination directory for RPM
	mkdir -p $(BASE_DIR)/os/Packages

	# Create default DNF conf
	mkdir -p $(DNF_ROOT)/etc/dnf
	cp $(INSTALLER_DIR)/yum/dnf.conf $(DNF_ROOT)/etc/dnf/

	# Copy Fedora key to DNF installroot
	mkdir -p $(DNF_ROOT)/etc/pki/rpm-gpg
	cp $(INSTALLER_DIR)/qubes-release/RPM-GPG-KEY-fedora-$(DIST_VER)-primary $(DNF_ROOT)/etc/pki/rpm-gpg

iso-parse-kickstart:
	# Extract repos conf and packages from kickstart
	mkdir -p $(DNF_ROOT)/etc/yum.repos.d $(DNF_ROOT)/tmp
	$(INSTALLER_DIR)/scripts/ksparser --ks $(INSTALLER_KICKSTART) --extract-repo-conf-to $(DNF_REPO) --extract-packages-to $(DNF_PACKAGES)

iso-parse-tmpl:
	$(INSTALLER_DIR)/scripts/tmplparser --repo $(DNF_REPO) --extract-packages-to $(LORAX_PACKAGES)


iso-packages-anaconda:
	$(DNF) $(DNF_OPTS) clean all
	umask 022; $(DNF) $(DNF_OPTS) --downloaddir=$(BASE_DIR)/os/Packages --downloadonly install $(shell cat $(DNF_PACKAGES))
	pushd $(BASE_DIR)/os/ && $(CREATEREPO) -q -g $(TMP_DIR)/comps.xml .

iso-packages-lorax:
	$(DNF) $(DNF_OPTS) clean all
	umask 022; $(DNF) $(DNF_OPTS) --downloaddir=$(INSTALLER_DIR)/yum/installer/rpm --downloadonly install $(shell cat $(LORAX_PACKAGES))
	pushd $(INSTALLER_DIR)/yum/installer && $(CREATEREPO) -q -g $(TMP_DIR)/comps.xml --update .

iso-installer-lorax:
	$(LORAX) $(LORAX_OPTS) $(BASE_DIR)/os

iso-installer-mkisofs:
	mkdir -p $(BASE_DIR)/iso/
	chmod og+rX -R $(BASE_DIR)/os/
	xorrisofs -o $(BASE_DIR)/iso/$(ISO_NAME).iso \
		-R -J -V $(ISO_VOLID) \
		--grub2-mbr /usr/lib/grub/i386-pc/boot_hybrid.img \
		-partition_offset 16 \
		-appended_part_as_gpt \
		-append_partition 2 C12A7328-F81F-11D2-BA4B-00A0C93EC93B $(BASE_DIR)/os/images/efiboot.img \
		-iso_mbr_part_type EBD0A0A2-B9E5-4433-87C0-68B6B72699C7 \
		-c boot.cat --boot-catalog-hide \
		-b images/eltorito.img \
		-no-emul-boot -boot-load-size 4 -boot-info-table --grub2-boot-info \
		-eltorito-alt-boot \
		-e '--interval:appended_partition_2:all::' -no-emul-boot \
		-graft-points \
		.=$(BASE_DIR)/os \
		boot/grub2/i386-pc=/usr/lib/grub/i386-pc
	/usr/bin/implantisomd5 $(BASE_DIR)/iso/$(ISO_NAME).iso

iso-installer: iso-prepare iso-parse-kickstart iso-parse-tmpl iso-packages-anaconda iso-packages-lorax iso-installer-lorax iso-installer-mkisofs
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

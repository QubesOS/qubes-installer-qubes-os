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
DIST ?= fc31
DIST_VER = $(subst fc,,$(DIST))

INSTALLER_DIR ?= $(PWD)

ISO_INSTALLER ?= 1
INSTALLER_KICKSTART ?= $(INSTALLER_DIR)/conf/qubes-kickstart.cfg

ISO_LIVEUSB ?= 0
LIVE_KICKSTART ?= $(INSTALLER_DIR)/conf/liveusb.ks

CREATEREPO := $(shell which createrepo_c createrepo 2>/dev/null |head -1)

PUNGI := /usr/bin/pungi-gather
PUNGI_OPTS := --arch=x86_64 --greedy=none --exclude-debug --exclude-source

LORAX := /usr/sbin/lorax
LORAX_OPTS := --product "Qubes OS" --variant "qubes" --macboot --force --rootfs-size=4
LORAX_OPTS += --dracut-arg="--xz"
LORAX_OPTS += --dracut-arg="--install /.buildstamp"
LORAX_OPTS += --dracut-arg="--no-early-microcode"
LORAX_OPTS += --dracut-arg="--no-hostonly"
LORAX_OPTS += --dracut-arg="--debug"
LORAX_OPTS += --dracut-arg="--omit plymouth"
LORAX_OPTS += --dracut-arg="--add fips livenet dmsquash-live convertfs pollcdrom qemu qemu-net"
LORAX_OPTS += --dracut-arg="--add-drivers intel_lpss intel_lpss_pci spi_pxa2xx_platform spi_pxa2xx_pci applespi apple_ib_tb"

ifdef QUBES_RELEASE
    ISO_VERSION := $(QUBES_RELEASE)
    LORAX_OPTS += --isfinal
else
    ISO_VERSION ?= $(shell date +%Y%m%d)
endif
ISO_NAME := Qubes-$(ISO_VERSION)-x86_64
ISO_VOLID := $(shell echo $(ISO_NAME) | tr a-z A-Z | tr -s -c [:alnum:]'\n' -)
BASE_DIR := $(INSTALLER_DIR)/work/$(ISO_VERSION)/x86_64

LORAX_OPTS += --version "$(ISO_VERSION)" --release "Qubes OS $(ISO_VERSION)" --volid $(ISO_VOLID)
LORAX_OPTS += --workdir $(INSTALLER_DIR)/work/work/x86_64 --logfile $(INSTALLER_DIR)/work/logs/lorax-x86_64.log
LORAX_OPTS += --repo $(INSTALLER_DIR)/conf/dnf-lorax.repo

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
	rm -rf && mkdir work
	ln -nsf $(INSTALLER_DIR) /tmp/qubes-installer
	$(CREATEREPO) -q -g ../../conf/comps-qubes.xml --update yum/qubes-dom0

iso-installer-gather:
	mkdir -p $(BASE_DIR)/os/Packages
	umask 022; $(PUNGI) $(PUNGI_OPTS) --config $(INSTALLER_KICKSTART) --download-to=$(BASE_DIR)/os/Packages
	pushd $(BASE_DIR)/os/ && $(CREATEREPO) -q -g $(INSTALLER_DIR)/conf/comps-qubes.xml .

iso-installer-lorax:
	$(INSTALLER_DIR)/scripts/ksparser --ks $(INSTALLER_KICKSTART) --extract-repo-conf-to $(INSTALLER_DIR)/conf/dnf-lorax.repo
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

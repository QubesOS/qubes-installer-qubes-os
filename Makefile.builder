RPM_SPEC_FILES.dom0 := \
    pykickstart/pykickstart.spec \
    blivet/python-blivet.spec \
    lorax/lorax.spec \
    lorax-templates-qubes/lorax-templates-qubes.spec \
    pungi/pungi.spec \
    anaconda/anaconda.spec \
    qubes-anaconda-addon/qubes-anaconda-addon.spec \
    qubes-release/qubes-release.spec

#    qubes-release/qubes-dom0-dist-upgrade.spec

ifeq ($(ISO_LIVEUSB),1)
RPM_SPEC_FILES.dom0 += \
    livecd-tools/livecd-tools.spec \
    live/qubes-live.spec
endif

RPM_SPEC_FILES := $(RPM_SPEC_FILES.$(PACKAGE_SET))
SOURCE_COPY_IN := $(RPM_SPEC_FILES.dom0)

$(RPM_SPEC_FILES.dom0): SPEC=$(notdir $@)
$(RPM_SPEC_FILES.dom0): PACKAGE=$(dir $@)
$(RPM_SPEC_FILES.dom0): SOURCE_ARCHIVE_NAME=$(notdir $(shell $(RPM_PLUGIN_DIR)/tools/spectool --list-files --source 0 $(CHROOT_DIR)/$(DIST_SRC)/$(PACKAGE)/$(SPEC) | cut -d' ' -f2))
$(RPM_SPEC_FILES.dom0):
	# Create the archive for specific Qubes packages
	[[ -e $(CHROOT_DIR)/$(DIST_SRC)/$(PACKAGE)/$(SOURCE_ARCHIVE_NAME) ]] \
		|| $(BUILDER_DIR)/scripts/create-archive $(CHROOT_DIR)/$(DIST_SRC)/$(PACKAGE) $(SOURCE_ARCHIVE_NAME)

NO_ARCHIVE = 1

dist-package-build: RPM_SOURCE_DIR=$(dir $(DIST_SRC)/$(PACKAGE))

# vim: ft=make

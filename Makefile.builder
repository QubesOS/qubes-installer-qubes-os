RPM_SPEC_FILES.dom0 := \
    pykickstart/pykickstart.spec \
    lorax/lorax.spec \
    lorax-templates-qubes/lorax-templates-qubes.spec \
    pungi/pungi.spec \
    anaconda/anaconda.spec \
    initial-setup-launcher/initial-setup-launcher.spec \
    qubes-anaconda-addon/qubes-anaconda-addon.spec \
    qubes-release/qubes-release.spec \
    qubes-release/qubes-dom0-dist-upgrade.spec

ifeq ($(ISO_LIVEUSB),1)
RPM_SPEC_FILES.dom0 += \
    livecd-tools/livecd-tools.spec \
	live/qubes-live.spec
endif

RPM_SPEC_FILES := $(RPM_SPEC_FILES.$(PACKAGE_SET))


# vim: ft=make

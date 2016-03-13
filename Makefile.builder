ifeq ($(PACKAGE_SET),dom0)
RPM_SPEC_FILES := \
	anaconda/anaconda.spec \
	firstboot/firstboot.spec \
	qubes-release/qubes-release.spec \
	lorax/lorax.spec \
	lorax-templates-qubes/lorax-templates-qubes.spec \
	pungi/pungi.spec \
	pykickstart/pykickstart.spec \
	qubes-release/qubes-dom0-dist-upgrade.spec \
    livecd-tools/livecd-tools.spec \
    live/qubes-live.spec
endif

RPM_SPEC_FILES.dom0 := \
    pykickstart/pykickstart.spec \
    lorax/lorax.spec \
    lorax-templates-qubes/lorax-templates-qubes.spec \
    pungi/pungi.spec \
    anaconda/anaconda.spec \
    firstboot/firstboot.spec \
    qubes-release/qubes-release.spec \
    qubes-release/qubes-dom0-dist-upgrade.spec \
    livecd-tools/livecd-tools.spec \
    live/qubes-live.spec

RPM_SPEC_FILES := $(RPM_SPEC_FILES.$(PACKAGE_SET))

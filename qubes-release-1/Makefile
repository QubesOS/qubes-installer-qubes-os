VERSION=$(shell awk '/Version/ { print $$2 }' qubes-release.spec)

CVSROOT = $(shell cat CVS/Root 2>/dev/null || :)

CVSTAG = V$(subst .,-,$(VERSION))

all:

tag-archive:
	@cvs -Q tag -F $(CVSTAG)

create-archive:
	@rm -rf /tmp/fedora-release
	@cd /tmp ; cvs -Q -d $(CVSROOT) export -r$(CVSTAG) qubes-release || echo "Um... export aborted."
	@mv /tmp/qubes-release /tmp/qubes-release-$(VERSION)
	@cd /tmp ; tar -czSpf qubes-release-$(VERSION).tar.gz qubes-release-$(VERSION)
	@rm -rf /tmp/qubes-release-$(VERSION)
	@cp /tmp/qubes-release-$(VERSION).tar.gz .
	@rm -f /tmp/qubes-release-$(VERSION).tar.gz
	@echo ""
	@echo "The final archive is in qubes-release-$(VERSION).tar.gz"

archive: tag-archive create-archive

NAME = generic-logos
XML = backgrounds/desktop-backgrounds-fedora.xml

all: update-po archive
VERSION := $(shell awk '/Version:/ { print $$2 }' $(NAME).spec)
RELEASE := $(shell awk '/Release:/ { print $$2 }' $(NAME).spec | sed 's|%{?dist}||g')
TAG=$(NAME)-$(VERSION)-$(RELEASE)

tag:
	@git tag -a -f -m "Tag as $(TAG)" -f $(TAG)
	@echo "Tagged as $(TAG)"

archive: tag
	@git archive --format=tar --prefix=$(NAME)-$(VERSION)/ HEAD > $(NAME)-$(VERSION).tar
	@bzip2 -f $(NAME)-$(VERSION).tar
	@echo "The archive is at $(NAME)-$(VERSION).tar.bz2"

clean:
	rm -f *~ *bz2

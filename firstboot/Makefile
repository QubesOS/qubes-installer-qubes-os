PKGNAME=firstboot
VERSION=$(shell awk '/Version:/ { print $$2 }' ${PKGNAME}.spec)
RELEASE=$(shell awk '/Release:/ { print $$2 }' ${PKGNAME}.spec | sed -e 's|%.*$$||g')
TAG=r$(VERSION)-$(RELEASE)

SITELIB := $(shell python -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")

PYCHECKEROPTS=--no-shadowbuiltin --no-argsused --no-miximport --maxreturns 0 --maxargs 0 --no-local -\# 0 --only

default: all

all:
	$(MAKE) -C po

check:
	PYTHONPATH=. pychecker $(PYCHECKEROPTS) firstboot/*.py modules/*.py progs/*.py

clean:
	-rm firstboot/*.pyc modules/*.pyc
	-rm ${PKGNAME}-$(VERSION).tar.bz2
	$(MAKE) -C po clean
	python setup.py -q clean --all

install: all
	for py in progs/* ; do \
		sed -i -e s,@VERSION@,$(VERSION),g $${py} ; \
	done
	python setup.py install --root=$(DESTDIR) --install-lib=$(SITELIB)
	$(MAKE) -C po install

tag:
	git tag -f $(TAG)

archive: tag
	git archive --format=tar --prefix=${PKGNAME}-$(VERSION)/ $(TAG) > ${PKGNAME}-$(VERSION).tar
	bzip2 ${PKGNAME}-$(VERSION).tar
	@echo "The archive is in ${PKGNAME}-$(VERSION).tar.bz2"

local:
	@rm -rf ${PKGNAME}-$(VERSION).tar.bz2
	@rm -rf /tmp/${PKGNAME}-$(VERSION) /tmp/${PKGNAME}
	@dir=$$PWD; cp -a $$dir /tmp/${PKGNAME}-$(VERSION)
	@rm -rf /tmp/${PKGNAME}-$(VERSION)/.git
	@dir=$$PWD; cd /tmp; tar --bzip2 -cSpf $$dir/${PKGNAME}-$(VERSION).tar.bz2 ${PKGNAME}-$(VERSION)
	@rm -rf /tmp/${PKGNAME}-$(VERSION)
	@echo "The archive is in ${PKGNAME}-$(VERSION).tar.gz"

.PHONY: check clean install tag archive local

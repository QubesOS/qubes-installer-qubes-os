ANACONDADATADIR = /usr/share/anaconda
ANACONDARUNTIMEDIR = /usr/lib/anaconda-runtime

all: 
	@echo "Nothing to do."

splash.lss: syslinux-splash.png
	./splashtolss.sh syslinux-splash.png splash.lss

install: 
	@if [ "$(DESTDIR)" = "" ]; then \
		echo " "; \
		echo "ERROR: A destdir is required"; \
		exit 1; \
	fi

	mkdir -p $(DESTDIR)/$(ANACONDADATADIR)
	mkdir -p $(DESTDIR)/$(ANACONDADATADIR)/pixmaps
	install -m 644 *.png $(DESTDIR)/$(ANACONDADATADIR)/pixmaps
	install -m 644 splash.png $(DESTDIR)/$(ANACONDADATADIR)/pixmaps/progress_first.png
	install -m 644 splash.png $(DESTDIR)/$(ANACONDADATADIR)/pixmaps/progress_first-lowres.png

	mkdir -p $(DESTDIR)/$(ANACONDARUNTIMEDIR)
	install -m 644 syslinux-vesa-splash.jpg $(DESTDIR)/$(ANACONDARUNTIMEDIR)

clean:
	rm -f splash.lss


SPECFILE := livecd-tools.spec
URL := $(shell spectool --list-files --source 0 $(SPECFILE) 2> /dev/null| cut -d ' ' -f 2- )
ifndef SRC_FILE
ifdef URL
	SRC_FILE := $(notdir $(URL))
endif
endif

get-sources: $(SRC_FILE)

$(SRC_FILE):
ifneq ($(SRC_FILE), None)
	@wget -q $(URL)
endif

.PHONY: verify-sources

verify-sources:
ifneq ($(SRC_FILE), None)
	@sha256sum --quiet -c sources
endif


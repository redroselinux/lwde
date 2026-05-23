DESTDIR := /
BIN_PATH := /usr/bin
DOT_CONFIG_PATH := /home/$(or $(SUDO_USER),$(USER))/.config
ETC_SKEL_PATH := /etc/skel
CP := cp
INSTALL := install
D_COMPILER := ldc
D_BUILD := release
DFLAGS := -"-build=$(D_BUILD) --compiler=$(D_COMPILER)"

build-settings:
	cd src/lwde-settings && \
	dub build $(DFLAGS)
	strip --strip-unneeded src/lwde-settings/lwde-settings

build: build-settings

install:
	$(CP) ./.config/* $(DOT_CONFIG_PATH) -r
	$(CP) ./.config/* $(DESTDIR)/$(ETC_SKEL_PATH) -r
	$(CP) ./usr/* $(DESTDIR)/ -r
	$(INSTALL) -D -m 755 ./src/lwde-desktop-icons/main.py $(DESTDIR)/$(BIN_PATH)/lwde-desktop-icons
	$(INSTALL) -D -m 755 ./src/lwde-settings/lwde-settings $(DESTDIR)/$(BIN_PATH)/lwde-settings

all: build

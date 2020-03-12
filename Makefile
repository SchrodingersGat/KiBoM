#!/usr/bin/make

deb:
	fakeroot dpkg-buildpackage -uc -b

deb_clean:
	fakeroot debian/rules clean

.PHONY: deb deb_clean

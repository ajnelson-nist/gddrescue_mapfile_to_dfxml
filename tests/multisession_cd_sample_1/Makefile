#!/usr/bin/make -f

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

SHELL := /bin/bash

top_srcdir := ../..

all: \
  diskimage.report.html

.PHONY: \
  check-diskimage-report-html \
  check-diskimage-report-md \
  check-docs

# For 'check', just confirm the report builds.
check: \
  diskimage.report.html

check-diskimage-report-html: \
  diskimage.report.html
	git diff $<
	@if [ $$(git diff $< | wc -l) -gt 0 ] ; then exit 1 ; fi

check-diskimage-report-md: \
  diskimage.report.md
	git diff $<
	@if [ $$(git diff $< | wc -l) -gt 0 ] ; then exit 1 ; fi

check-docs: \
  check-diskimage-report-html \
  check-diskimage-report-md

# TODO See if .gfm works, to keep from clobbering README.md file.
clean:
	@rm -f *.dfxml diskimage.report.md

diskimage.dfxml: \
  $(top_srcdir)/gddrescue_mapfile_to_dfxml/cli.py \
  ../.check-dfxml-loads.done.log \
  disk.img.mapfile
	source $(top_srcdir)/tests/venv/bin/activate \
	  && gddrescue_mapfile_to_dfxml \
	    disk.img.mapfile \
	    __$@
	xmllint --format __$@ > _$@
	rm __$@
	mv _$@ $@

diskimage.report.html: \
  $(top_srcdir)/gddrescue_mapfile_to_dfxml/intact_byte_run_index.py \
  $(top_srcdir)/gddrescue_mapfile_to_dfxml/recoverability_report.py \
  diskimage.dfxml
	source $(top_srcdir)/tests/venv/bin/activate \
	  && gddrescue_dfxml_recoverability_report \
	    diskimage.dfxml \
	    > _$@
	mv _$@ $@

diskimage.report.md: \
  diskimage.report.html
	pandoc \
	  --from html \
	  --to gfm \
	  --output _$@ \
	  $<
	mv _$@ $@

docs: \
  diskimage.report.md

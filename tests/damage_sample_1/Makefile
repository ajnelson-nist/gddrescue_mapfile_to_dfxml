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
  diskimage.report.html \
  file_recoverability.report.html \
  non_recoverable_files.txt

.PHONY: \
  check-diskimage-report-html \
  check-docs \
  check-file_recoverability-report-html \
  check-file_recoverability-report-md \
  check-non_recoverable_files-txt \
  docs

# For 'check', confirm the reports build, AND confirm the expected results.
check: \
  check-non_recoverable_files-txt \
  diskimage.report.html \
  file_recoverability.report.html

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
  check-diskimage-report-md \
  check-file_recoverability-report-html \
  check-file_recoverability-report-md

check-file_recoverability-report-html: \
  file_recoverability.report.html
	git diff $<
	@if [ $$(git diff $< | wc -l) -gt 0 ] ; then exit 1 ; fi

check-file_recoverability-report-md: \
  file_recoverability.report.md
	git diff $<
	@if [ $$(git diff $< | wc -l) -gt 0 ] ; then exit 1 ; fi

check-non_recoverable_files-txt: \
  non_recoverable_files.txt
	git diff $<
	@if [ $$(git diff $< | wc -l) -gt 0 ] ; then echo "ERROR:Makefile:Computed list of non-recoverable files does not match expected list." >&2 ; exit 1 ; fi

# TODO See if .gfm works, to keep from clobbering README.md file.
clean:
	@rm -f *.dfxml *.html diskimage.report.md file_recoverability.report.md

diskimage.dfxml: \
  $(top_srcdir)/gddrescue_mapfile_to_dfxml/cli.py \
  ../.check-dfxml-loads.done.log \
  damage_sample.img.mapfile
	source $(top_srcdir)/venv/bin/activate \
	  && gddrescue_mapfile_to_dfxml \
	    damage_sample.img.mapfile \
	    __$@
	xmllint --format __$@ > _$@
	rm __$@
	mv _$@ $@

diskimage.report.html: \
  $(top_srcdir)/src/intact_byte_run_index.py \
  $(top_srcdir)/src/report_file_recoverability_html.py \
  diskimage.dfxml
	source $(top_srcdir)/venv/bin/activate ; \
	  python $(top_srcdir)/src/report_file_recoverability_html.py \
	    --debug \
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
  diskimage.report.md \
  file_recoverability.report.md

file_recoverability.dfxml: \
  $(top_srcdir)/src/intact_byte_run_index.py \
  $(top_srcdir)/src/make_file_recoverability_dfxml.py \
  diskimage.dfxml \
  sample_file_system.dfxml
	source $(top_srcdir)/venv/bin/activate ; \
	  python $(top_srcdir)/src/make_file_recoverability_dfxml.py \
	    --debug \
	    --disk-image-dfxml diskimage.dfxml \
	    sample_file_system.dfxml \
	    __$@
	xmllint --format __$@ > _$@
	rm __$@
	mv _$@ $@

file_recoverability.report.html: \
  $(top_srcdir)/src/intact_byte_run_index.py \
  $(top_srcdir)/src/report_file_recoverability_html.py \
  file_recoverability.dfxml
	source $(top_srcdir)/venv/bin/activate ; \
	  python $(top_srcdir)/src/report_file_recoverability_html.py \
	    --debug \
	    file_recoverability.dfxml \
	    > _$@
	mv _$@ $@

file_recoverability.report.md: \
  file_recoverability.report.html
	pandoc \
	  --from html \
	  --to gfm \
	  --output _$@ \
	  $<
	mv _$@ $@

non_recoverable_files.txt: \
  file_recoverability.dfxml \
  list_filenames.py
	source $(top_srcdir)/venv/bin/activate ; \
	  python list_filenames.py \
	    file_recoverability.dfxml \
	    > _$@
	mv _$@ $@

sample_file_system.dfxml: \
  sample_file_system_dfxml.py
	source $(top_srcdir)/venv/bin/activate ; \
	  python sample_file_system_dfxml.py \
	    | xmllint --format - \
	      > _$@
	mv _$@ $@

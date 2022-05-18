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

top_srcdir := ..

all:

.PHONY: \
  check-damage_sample_1 \
  check-docs \
  check-docs-damage_sample_1 \
  check-docs-multisession_cd_sample_1 \
  check-multisession_cd_sample_1 \
  docs-damage_sample_1 \
  docs-multisession_cd_sample_1

.check-dfxml-loads.done.log: \
  $(top_srcdir)/.venv.done.log \
  $(top_srcdir)/gddrescue_mapfile_to_dfxml/cli.py
	source $(top_srcdir)/venv/bin/activate \
	  && gddrescue_mapfile_to_dfxml \
	    --help \
	    > /dev/null
	touch $@

check: \
  check-damage_sample_1 \
  check-multisession_cd_sample_1

check-damage_sample_1: \
  .check-dfxml-loads.done.log
	$(MAKE) \
	  --directory damage_sample_1 \
	  check

check-docs: \
  check-docs-damage_sample_1 \
  check-docs-multisession_cd_sample_1

check-docs-damage_sample_1: \
  .check-dfxml-loads.done.log
	$(MAKE) \
	  --directory damage_sample_1 \
	  check-docs

check-docs-multisession_cd_sample_1: \
  .check-dfxml-loads.done.log
	$(MAKE) \
	  --directory multisession_cd_sample_1 \
	  check-docs

check-multisession_cd_sample_1: \
  .check-dfxml-loads.done.log
	$(MAKE) \
	  --directory multisession_cd_sample_1 \
	  check

clean:
	@rm -f .*.done.log
	@$(MAKE) --directory damage_sample_1 clean
	@$(MAKE) --directory multisession_cd_sample_1 clean

docs: \
  docs-damage_sample_1 \
  docs-multisession_cd_sample_1

docs-damage_sample_1: \
  .check-dfxml-loads.done.log
	$(MAKE) \
	  --directory damage_sample_1 \
	  docs

docs-multisession_cd_sample_1: \
  .check-dfxml-loads.done.log
	$(MAKE) \
	  --directory multisession_cd_sample_1 \
	  docs

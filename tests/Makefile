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

PYTHON3 ?= python3

all:

.PHONY: \
  check-damage_sample_1 \
  check-docs \
  check-docs-damage_sample_1 \
  check-docs-multisession_cd_sample_1 \
  check-multisession_cd_sample_1 \
  check-mypy \
  docs-damage_sample_1 \
  docs-multisession_cd_sample_1

.check-dfxml-loads.done.log: \
  $(top_srcdir)/gddrescue_mapfile_to_dfxml/cli.py \
  .venv.done.log
	source venv/bin/activate \
	  && gddrescue_mapfile_to_dfxml \
	    --help \
	    > /dev/null
	touch $@

.venv.done.log: \
  $(top_srcdir)/.git_submodule_init.done.log \
  $(top_srcdir)/setup.cfg \
  requirements.txt
	rm -rf \
	  venv
	$(PYTHON3) -m venv \
	  venv
	source venv/bin/activate \
	  && pip install \
	    --upgrade \
	    pip \
	    setuptools \
	    wheel
	source venv/bin/activate \
	  && pip install \
	    $(top_srcdir)/deps/dfxml
	source venv/bin/activate \
	  && pip install \
	    --editable \
	    $(top_srcdir)
	source venv/bin/activate \
	  && pip install \
	    --requirement requirements.txt
	touch $@

check: \
  check-damage_sample_1 \
  check-multisession_cd_sample_1 \
  check-mypy

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

check-mypy: \
  .venv.done.log
	source venv/bin/activate \
	  && mypy \
	    --strict \
	    $(top_srcdir)/gddrescue_mapfile_to_dfxml \
	    .

clean:
	@$(MAKE) --directory damage_sample_1 clean
	@$(MAKE) --directory multisession_cd_sample_1 clean
	@rm -f .*.done.log
	@rm -rf venv

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

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

PYTHON3 ?= python3

all:

.PHONY: \
  check-docs \
  docs \
  docs-figs \
  docs-tests

.git_submodule_init.done.log: \
  .git_submodule_init-dfxml.done.log
	touch $@

.git_submodule_init-dfxml.done.log:
	git submodule init deps/dfxml
	git submodule update deps/dfxml
	pushd deps/dfxml ; \
	  make schema-init
	touch $@

.venv.done.log: \
  .git_submodule_init.done.log \
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
	    -r requirements.txt
	touch $@

check: \
  .venv.done.log
	$(MAKE) \
	  --directory tests \
	  check

check-docs: \
  check-docs-figs \
  check-docs-tests

check-docs-figs:
	$(MAKE) \
	  --directory figs \
	  check

check-docs-tests: \
  .venv.done.log
	$(MAKE) \
	  --directory tests \
	  check-docs

clean:
	@rm -rf venv
	@rm -f .*.done.log
	@$(MAKE) --directory figs clean
	@$(MAKE) --directory tests clean

docs: \
  docs-figs \
  docs-tests

docs-figs:
	$(MAKE) \
	  --directory figs

docs-tests:
	$(MAKE) \
	  --directory tests \
	  docs

download: \
  .venv.done.log

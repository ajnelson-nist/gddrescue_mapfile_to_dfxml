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

# Tip for including SVG in Github READMEs c/o:
#   https://stackoverflow.com/a/16462143

all: \
  data_flow.svg

check:
	$(MAKE) clean
	$(MAKE)
	git diff data_flow.svg
	@if [ $$(git diff data_flow.svg | wc -l) -gt 0 ] ; then exit 1 ; fi

clean:
	@rm -f data_flow.svg

data_flow.svg: \
  data_flow.dot
	dot -T svg -o _$@ $<
	mv _$@ $@

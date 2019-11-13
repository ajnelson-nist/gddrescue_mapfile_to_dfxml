#!/usr/bin/env python3

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

"""
This is a quick utility script to emit all filenames from a DFXML file.
"""

__version__ = "0.1.0"

import sys

from dfxml import objects as Objects

for (event, obj) in Objects.iterparse(sys.argv[1]):
    if not isinstance(obj, Objects.FileObject):
        continue
    print(obj.filename)

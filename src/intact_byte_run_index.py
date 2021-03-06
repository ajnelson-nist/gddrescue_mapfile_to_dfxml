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

__version__ = "0.1.0"

import bisect
import collections
import logging
import os

# Following style guidance of documentation:
#   https://pypi.org/project/python-intervals
import intervals as I

from dfxml import objects as Objects

_logger = logging.getLogger(os.path.basename(__file__))

class IntactByteRunIndex(object):
    """
    This class helps analyze the intactness of byte run lists.  For convenience, functions are provided that expect either byte run DFXML objects, or the runs expressed as (offset, length) pairs.  The byte run function variants assume the disk image offset (img_offset) is to be used.
    """

    def __init__(self):
        self._intervals = None

    def filter_byte_run(self, input_byte_run):
        if input_byte_run.img_offset is None:
            return None
        if input_byte_run.len is None:
            return None
        return self.filter_run_pair((input_byte_run.img_offset, input_byte_run.len))

    def filter_run_pair(self, input_run_pair):
        """
        Returns a list of (offset, length) pairs that represent sub-intervals of input_interval, which are present in the index.
        """
        (input_offset, input_length) = input_run_pair
        if input_offset is None:
            return None
        if input_length is None:
            return None
        input_interval = I.closedopen(input_offset, input_offset + input_length)
        filtered_interval = self.intervals & input_interval
        retval = []
        if filtered_interval.is_empty():
            return retval
        try:
            for atomic_interval in filtered_interval:
                retval.append((atomic_interval.lower, atomic_interval.upper - atomic_interval.lower))
        except:
            _logger.debug("filtered_interval = %r." % filtered_interval)
            raise
        return retval

    def ingest_byte_runs(self, brs):
        """
        This function expects brs to be a dfxml.objects.ByteRuns object.
        """
        # Type safety.
        assert isinstance(brs, Objects.ByteRuns)
        # Input validation.
        if len(brs) == 0 \
          or brs[0].img_offset is None \
          or brs[0].len is None:
            raise ValueError("Byte run list not ingestable.")

        if not self.intervals is None:
            raise ValueError("Index can only be loaded once. (.ingest_byte_runs() method was called twice.)")

        # Prime intervals data structure with first byte run.
        self.intervals = I.closedopen(brs[0].img_offset, brs[0].img_offset + brs[0].len)

        # Append remaining runs.
        for br in brs[1:]:
            # TODO Make this a little more user-friendly.
            assert not br.img_offset is None
            assert not br.len is None
            self.intervals |= I.closedopen(br.img_offset, br.img_offset + br.len)
        #_logger.debug("self.intervals = %r." % self.intervals)

    def is_byte_run_contained(self, input_byte_run):
        if input_byte_run.img_offset is None:
            return None
        if input_byte_run.len is None:
            return None
        return self.is_run_pair_contained((input_byte_run.img_offset, input_byte_run.len))

    def is_run_pair_contained(self, input_run_pair):
        (input_offset, input_length) = input_run_pair
        if input_offset is None:
            return None
        if input_length is None:
            return None
        input_interval = I.closedopen(input_offset, input_offset + input_length)
        return input_interval in self.intervals

    @property
    def intervals(self):
        """
        This is a single intervals.Interval instance.  It is expected to frequently be a sequence of interval.AtomicInterval, so it will always be safe to iterate over this property and operate on each AtomicInterval.
        """
        return self._intervals

    @intervals.setter
    def intervals(self, value):
        assert value is None or \
          isinstance(value, I.Interval)
        self._intervals = value

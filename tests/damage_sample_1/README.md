# Damage Sample 1

This directory contains a hand-adjusted mapfile, representing a damaged 1 terabyte hard drive.

The imagined drive was given the imaging profile of being intact except for the first 512 bytes, and a 1GiB region starting at 400GiB.


## Source

The [mapfile](damage_sample.img.mapfile) in this directory was simplified from the mapfile of a disk that exhibited errors in imaging.  The current position marker might not reflect what an actual mapfile would state.


## Analysis results

The file [`diskimage.report.md`](diskimage.report.md) contains the results of analyzing the mapfile converter tool's generated DFXML.

The file [`file_recoverability.report.md`](file_recoverability.report.md) reports the data lost in a file system on that same sample damaged disk image.

# Multisession CD Sample 1

This directory contains a mapfile of a multisession CD, with two sessions.  The first session houses music, in eleven audio tracks.  The second session is a data session that houses a file system.  This type of storage medium is known to behave poorly with some acquisition methods that otherwise function for floppy disk, hard drive, or flash medium.  In particular, audio sessions do not image as data sessions do.  On this disc, the audio session appears to the imaging `ddrescue` process to be only erroneous sectors.


## Source

The MusicBrainz music metadata database contains a record of the audio portions of this sample CD, here:

[https://musicbrainz.org/release/09a07044-abed-4938-a41d-f8d1cd06b86c](https://musicbrainz.org/release/09a07044-abed-4938-a41d-f8d1cd06b86c)

This CD was selected simply by at-hand availability.


### Acquisition

`ddrescue` was set to run for a five hour acquisition, enforced by a Bash `timeout` call.


## Analysis results

The file [`diskimage.report.md`](diskimage.report.md) contains the results of analyzing the mapfile converter tool's generated DFXML.

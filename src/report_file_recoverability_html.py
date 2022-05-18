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
This script provides a HTML report reporting the impact of sectors not captured from the original file system, according to a byte run aware DFXML map.

Relies on image filesize being recorded in diskimageobject element (a feature under draft for DFXML version 1.3.0).

Assumes that, for the diskimageobject's byte runs, only byte runs listed in the input DFXML are present in the disk image.

If file objects are presented in the input DFXML file as well, tables will be emitted for the listed file systems and files.  These files are assumed to be in the supplied DFXML because of being at least partially non-recoverable according to unavailable disk image sectors.

Generally, this script expects to receive DFXML generated (or combined) by the script make_file_recoverability_dfxml.py.

Prints HTML5 report to stdout.
"""

__version__ = "0.1.0"

import os
import logging
import locale

HAVE_HUMANFRIENDLY = False
try:
    import humanfriendly

    HAVE_HUMANFRIENDLY = True
except:
    pass

from dfxml import objects as Objects

import intact_byte_run_index

_logger = logging.getLogger(os.path.basename(__file__))

# Comma separation c/o: https://stackoverflow.com/a/10742904
locale.setlocale(locale.LC_ALL, "")


def main():

    br_index = intact_byte_run_index.IntactByteRunIndex()

    original_disk_size = None
    disk_summary_message = None
    files_summary_message = None
    file_system_tuples = []
    fileobject_tally = 0

    for (event, obj) in Objects.iterparse(args.disk_image_dfxml):
        if isinstance(obj, Objects.DiskImageObject):
            if event != "end":
                continue
            original_disk_size = obj.filesize
            bytes_unread = original_disk_size
            for br in obj.byte_runs:
                bytes_unread -= br.len
            if HAVE_HUMANFRIENDLY:
                parenthetical_friendly_filesize = " (%s)" % humanfriendly.format_size(
                    obj.filesize
                )
                parenthetical_friendly_bytes_unread = (
                    " (%s)" % humanfriendly.format_size(bytes_unread)
                )
            else:
                parenthetical_friendly_filesize = ""
                parenthetical_friendly_bytes_unread = ""

            disk_summary_message = (
                "Of %s bytes%s of the original disk, %s bytes%s are not in the acquired disk image."
                % (
                    f"{obj.filesize:n}",
                    parenthetical_friendly_filesize,
                    f"{bytes_unread:n}",
                    parenthetical_friendly_bytes_unread,
                )
            )

            br_index.ingest_byte_runs(obj.byte_runs)
        elif isinstance(obj, Objects.VolumeObject):
            if event != "end":
                continue
            fs_tally = len(file_system_tuples) + 1  # (counting newly discovered self)
            # Determine file system geometry.
            if obj.byte_runs is None or len(obj.byte_runs) == 0:
                fs_img_offset = obj.partition_offset
                fs_len = obj.block_size * obj.block_count
            else:
                fs_img_offset = obj.byte_runs[0].img_offset
                fs_len = obj.byte_runs[0].len
            file_system_tuples.append((fs_tally, fs_img_offset, fs_len, obj.ftype_str))
        elif isinstance(obj, Objects.FileObject):
            fileobject_tally += 1

    if fileobject_tally == 0:
        files_summary_message = "No files were listed as affected."
    elif fileobject_tally == 1:
        files_summary_message = "1 file was affected."
    else:
        files_summary_message = "%d files were affected." % fileobject_tally

    print(
        """\
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style type="text/css">
      table {
        border-collapse: collapse;
      }
      td {
        border: 1px solid black;
      }
      th {
        border: 1px solid black;
      }
    </style>
  </head>
  <body>
    <h1>Report of file recoverability</h1>
    <p>%s</p>
    <p>%s</p>"""
        % (disk_summary_message, files_summary_message)
    )

    if fileobject_tally > 0:
        print(
            """\
    <table>
      <caption>Table 1. File systems</caption>
      <thead>
        <tr>
          <th>FS #</th>
          <th>Offset</th>
          <th>Length</th>
          <th>Type</th>
        </tr>
      </thead>
      <tbody>"""
        )
        for file_system_tuple in file_system_tuples:
            print(
                """\
        <tr>
          <td>%d</td>
          <td>%d</td>
          <td>%d</td>
          <td>%s</td>
        </tr>"""
                % file_system_tuple
            )
        print(
            """\
      </tbody>
    </table>
    <table>
      <caption>Table 2. Affected files</caption>
      <thead>
        <tr>
          <th>FS #</th>
          <th>Type</th>
          <th>Size (bytes)</th>
          <th>Missing bytes</th>
          <th>Path</th>
        </tr>
      </thead>
      <tbody>"""
        )

        last_fs_number = 0
        current_fs_number_str = ""
        for (event, obj) in Objects.iterparse(args.disk_image_dfxml):
            if isinstance(obj, Objects.VolumeObject):
                if event == "start":
                    last_fs_number += 1
                    current_fs_number_str = str(last_fs_number)
                else:
                    current_fs_number_str = ""
                continue
            elif not isinstance(obj, Objects.FileObject):
                continue

            # The remainder of this loop analyzes files.

            # TODO
            bytes_present = 0
            for byte_run in obj.data_brs:
                for filtered_run_pair in br_index.filter_byte_run(byte_run):
                    bytes_present += filtered_run_pair[1]
            bytes_missing = obj.filesize - bytes_present

            name_type = "" if obj.name_type is None else obj.name_type
            print(
                """\
        <tr>
          <td>%s</td>
          <td><code>%s</code></td>
          <td>%d</td>
          <td>%d</td>
          <td><code>%s</code></td>
        </tr>"""
                % (
                    current_fs_number_str,
                    name_type,
                    obj.filesize,
                    bytes_missing,
                    obj.filename,
                )
            )

        print(
            """\
      </tbody>
    </table>
    <p>Note that "FS #" is a simple incrementing integer defined only in this report.  A missing "FS #" indicates the input DFXML did not have the file associated with a file system.</p>
    <p>The file type code is the DFXML encoding of <code>name_type</code>.  <code>r</code> is a regular file; <code>d</code> a directory; and <code>v</code> a "virtual" file, a file that is not precisely a file in the file system, but is treated as a file by the tool that parsed the file system.</p>
    <p>The "Size" column is the size of the file according to the file system.  "Missing bytes" indicates how many bytes of the file were not captured in the disk image.</p>"""
        )
    print(
        """\
  </body>
</html>"""
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("disk_image_dfxml")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    main()

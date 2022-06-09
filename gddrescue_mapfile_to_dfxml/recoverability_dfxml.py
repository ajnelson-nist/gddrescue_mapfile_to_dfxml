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

import argparse
import logging
import os
import subprocess
import sys
import typing

import dfxml
from dfxml import objects as Objects

import gddrescue_mapfile_to_dfxml.intact_byte_run_index

_logger = logging.getLogger(os.path.basename(__file__))


def get_portion_version() -> str:
    """
    portion does not currently provide portion.__version__.  Rather than parse portion's setup.py, review pip output.
    """
    pip_list_stdout: bytes = subprocess.check_output(["pip", "list"])
    version_string: typing.Optional[str] = None
    for byte_line in pip_list_stdout.split(b"\n"):
        if not byte_line.startswith(b"portion "):
            continue
        version_part = byte_line[len("portion") :].strip()
        version_string = version_part.decode("ascii")
        break
    if version_string is None:
        raise ValueError("portion package not found from pip listing.")
    return version_string


def main() -> None:
    parser = argparse.ArgumentParser(
        description="This program takes DFXML representations of a disk image that may have damaged sectors, and a DFXML manifest of files with file-content byte runs.  It outputs a DFXML manifest of files that have file-content byte runs that are not in the disk image (e.g. due to damaged sectors encountered during imaging)."
    )
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument(
        "--disk-image-dfxml",
        help="If not provided, requires --files-dfxml to have a diskimageobject element with geometry information.",
    )
    parser.add_argument("files_dfxml")
    parser.add_argument("out_dfxml")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    command_parts: typing.List[str] = []
    command_name_basename = os.path.basename(sys.argv[0])
    command_parts.append(command_name_basename)
    command_parts.extend(sys.argv[1:])

    # Initialize output object.
    # TODO Upgrade to 1.3.0 on schema release.
    dobj = Objects.DFXMLObject(version="1.2.0+")
    dobj.program = command_name_basename
    dobj.program_version = __version__
    dobj.command_line = " ".join(command_parts)
    dobj.dc["type"] = "Recoverability report"
    dobj.add_creator_library(
        "Python", ".".join(map(str, sys.version_info[0:3]))
    )  # A bit of a bend, but gets the major version information out.
    dobj.add_creator_library("dfxml", dfxml.__version__)
    dobj.add_creator_library("dfxml.objects", Objects.__version__)
    dobj.add_creator_library("portion", get_portion_version())

    if args.disk_image_dfxml:
        disk_image_dfxml = args.disk_image_dfxml
    else:
        disk_image_dfxml = args.files_dfxml

    br_index = gddrescue_mapfile_to_dfxml.intact_byte_run_index.IntactByteRunIndex()

    diobj: typing.Optional[Objects.DiskImageObject] = None
    # Index the byte runs of the disk image.
    for (event, obj) in Objects.iterparse(disk_image_dfxml):
        if not isinstance(obj, Objects.DiskImageObject):
            continue
        if event != "start":
            continue
        if obj.byte_runs is None or len(obj.byte_runs) == 0:
            raise ValueError(
                "DFXML document %r does not have diskimageobject with byte runs.  Recoverability cannot be determined."
                % disk_image_dfxml
            )
        br_index.ingest_byte_runs(obj.byte_runs)
        diobj = obj
        break

    if diobj is None:
        raise ValueError(
            "Input DFXML document did not report a DiskImageObject: %r."
            % disk_image_dfxml
        )

    # Confirm initialization.
    if br_index.intervals is None:
        raise ValueError(
            "Disk image byte runs index not constructed after reading file that should have had disk image metadata: %r."
            % disk_image_dfxml
        )

    # Track diskimageobject.
    dobj.append(diobj)

    # The loop below will want to attach fileobjects to the closest/lowest parent in the object hierarchy.  Might be the disk image, might be the containing file system.
    appender_stack: typing.List[Objects.AbstractParentObject] = [diobj]

    file_count_encountered = 0
    file_count_missing_byte_runs = 0
    file_count_missing_byte_run_offset = 0
    file_count_missing_byte_run_length = 0
    file_count_containment_unknown = 0
    file_count_intact = 0
    file_count_not_fully_recoverable = 0

    # Filter fileobject list, picking up file systems along the way.
    for (event, obj) in Objects.iterparse(args.files_dfxml):
        if isinstance(obj, Objects.VolumeObject):
            if event == "start":
                appender_stack[-1].append(obj)
                appender_stack.append(obj)
                continue
            elif event == "end":
                appender_stack.pop()
                continue

        if not isinstance(obj, Objects.FileObject):
            continue
        file_count_encountered += 1

        if obj.data_brs is None:
            file_count_missing_byte_runs += 1
            continue

        if len(obj.data_brs) == 0:
            file_count_missing_byte_runs += 1
            continue

        # This variable might be set to None within the loop through the content byte runs.
        byte_runs_contained: typing.Optional[bool] = True
        for byte_run in obj.data_brs:
            if byte_run.img_offset is None:
                # TODO See if this can be computed from fs_offset.
                file_count_missing_byte_run_offset += 1
                byte_runs_contained = None
                break
            if byte_run.len is None:
                file_count_missing_byte_run_length += 1
                byte_runs_contained = None
                break
            byte_run_contained = br_index.is_byte_run_contained(byte_run)
            if byte_run_contained is None:
                file_count_containment_unknown += 1
                byte_runs_contained = None
                break
            elif byte_run_contained is False:
                byte_runs_contained = False
                break
        if byte_runs_contained:
            file_count_intact += 1
        if byte_runs_contained is False:
            file_count_not_fully_recoverable += 1
            # Record fileobject as child of diskimageobject.
            appender_stack[-1].append(obj)

    _logger.debug("file_count_encountered = %d." % file_count_encountered)
    _logger.debug("file_count_missing_byte_runs = %d." % file_count_missing_byte_runs)
    _logger.debug(
        "file_count_missing_byte_run_offset = %d." % file_count_missing_byte_run_offset
    )
    _logger.debug(
        "file_count_missing_byte_run_length = %d." % file_count_missing_byte_run_length
    )
    _logger.debug(
        "file_count_containment_unknown = %d." % file_count_containment_unknown
    )
    _logger.debug("file_count_intact = %d." % file_count_intact)
    _logger.debug(
        "file_count_not_fully_recoverable = %d." % file_count_not_fully_recoverable
    )

    with open(args.out_dfxml, "w") as out_fh:
        dobj.print_dfxml(out_fh)


if __name__ == "__main__":
    main()

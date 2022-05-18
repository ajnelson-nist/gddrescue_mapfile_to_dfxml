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
This script generates a manifest of an example file system, including file geometry.
"""

__version__ = "0.1.0"

import sys

from dfxml import objects as Objects

DISK_IMAGE_SIZE = 1000204886016  # Original disk size
FILE_SYSTEM_START = 10485760  # 10MiB
DAMAGE_REGION_START = 429496729600  # 400GiB
GOOD_REGION_START = 430570471424  # 401GiB


def main():
    dobj = Objects.DFXMLObject(version="1.2.0")
    dobj.program = sys.argv[0]
    dobj.program_version = __version__
    dobj.command_line = " ".join(sys.argv)
    dobj.dc["type"] = "Example"
    dobj.add_creator_library(
        "Python", ".".join(map(str, sys.version_info[0:3]))
    )  # A bit of a bend, but gets the major version information out.
    dobj.add_creator_library("Objects.py", Objects.__version__)
    dobj.add_creator_library("dfxml.py", Objects.dfxml.__version__)

    vobj = Objects.VolumeObject()
    dobj.append(vobj)

    vobj.ftype_str = "examplefs"

    # Define file system position.
    vobj.byte_runs = Objects.ByteRuns()
    vbr = Objects.ByteRun()
    vobj.byte_runs.append(vbr)
    vbr.img_offset = FILE_SYSTEM_START
    vbr.len = DISK_IMAGE_SIZE - FILE_SYSTEM_START

    fobj_specs = [
        ("first_sector.bin", [(0, 512)]),
        ("first_four_kilobytes.bin", [(0, 4000)]),
        ("contiguous_before_bad_region.dat", [(FILE_SYSTEM_START + 4096 * 1, 4096)]),
        (
            "contiguous_around_bad_region_left_edge.dat",
            [(DAMAGE_REGION_START - 4096, 8192)],
        ),
        ("contiguous_in_bad_region.dat", [(DAMAGE_REGION_START + 4096 * 1, 4096)]),
        (
            "contiguous_around_bad_region_right_edge.dat",
            [(GOOD_REGION_START - 4096 * 1, 8192)],
        ),
        ("contiguous_after_bad_region.dat", [(GOOD_REGION_START + 4096 * 2, 4096)]),
        (
            "fragmented_all_before_bad_region.dat",
            [
                (FILE_SYSTEM_START + 4096 * 10, 4096),
                (FILE_SYSTEM_START + 4096 * 20, 4096),
                (FILE_SYSTEM_START + 4096 * 30, 4096),
            ],
        ),
        (
            "fragmented_all_after_bad_region.dat",
            [
                (GOOD_REGION_START + 4096 * 10, 4096),
                (GOOD_REGION_START + 4096 * 20, 4096),
                (GOOD_REGION_START + 4096 * 30, 4096),
            ],
        ),
        (
            "fragmented_all_inside_bad_region.dat",
            [
                (DAMAGE_REGION_START + 4096 * 10, 4096),
                (DAMAGE_REGION_START + 4096 * 20, 4096),
                (DAMAGE_REGION_START + 4096 * 30, 4096),
            ],
        ),
        (
            "fragmented_beginning_inside_bad_region.dat",
            [
                (DAMAGE_REGION_START + 4096 * 40, 4096),
                (GOOD_REGION_START + 4096 * 40, 4096),
            ],
        ),
        (
            "fragmented_middle_inside_bad_region.dat",
            [
                (FILE_SYSTEM_START + 4096 * 50, 4096),
                (DAMAGE_REGION_START + 4096 * 50, 4096),
                (GOOD_REGION_START + 4096 * 50, 4096),
            ],
        ),
        (
            "fragmented_end_inside_bad_region.dat",
            [
                (FILE_SYSTEM_START + 4096 * 60, 4096),
                (DAMAGE_REGION_START + 4096 * 60, 4096),
            ],
        ),
        ("after_disk_image_end.dat", [(DISK_IMAGE_SIZE + 4096 * 1000, 4096)]),
        (
            "fragmented_partially_recoverable_directory",
            [
                (FILE_SYSTEM_START + 4096 * 170, 4096),
                (DAMAGE_REGION_START + 4096 * 170, 4096),
                (GOOD_REGION_START + 4096 * 170, 4096),
            ],
        ),
        (
            "fragmented_partially_recoverable_directory/child_file_1",
            [(FILE_SYSTEM_START + 4096 * 180, 4096)],
        ),
        (
            "fragmented_partially_recoverable_directory/child_file_2",
            [(FILE_SYSTEM_START + 4096 * 190, 4096)],
        ),
        (
            "fragmented_partially_recoverable_directory/child_file_3",
            [(FILE_SYSTEM_START + 4096 * 200, 4096)],
        ),
        (
            "fragmented_partially_recoverable_directory/child_file_4",
            [(FILE_SYSTEM_START + 4096 * 210, 4096)],
        ),
        (
            "fragmented_partially_recoverable_directory/child_file_9",
            [(GOOD_REGION_START + 4096 * 180, 4096)],
        ),
    ]
    for fobj_spec in fobj_specs:
        fobj = Objects.FileObject()
        vobj.append(fobj)

        fobj.filename = fobj_spec[0]
        fobj.alloc = True
        # Naming convention for this sample - the .bin files are virtual files that reference a region outside of the file system.
        if fobj.filename == "fragmented_partially_recoverable_directory":
            fobj.name_type = "d"
        elif fobj.filename.endswith(".bin"):
            fobj.name_type = "v"
        else:
            fobj.name_type = "r"

        fobj.data_brs = Objects.ByteRuns()
        for interval in fobj_spec[1]:
            br = Objects.ByteRun()
            fobj.data_brs.append(br)
            br.img_offset = interval[0]
            br.len = interval[1]
        fobj.filesize = sum([br.len for br in fobj.data_brs])

    dobj.print_dfxml()


if __name__ == "__main__":
    main()

#!/usr/bin/env/python3

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
The GNU ddrescue mapfile format reports a status character for every block in a disk image.  For the purposes of analyzing data in the disk image, the relevant status character is "+", indicating a "finished block" - an imaged block.  Everything else is effectively an unretrieved, or unretrievable, block.
"""

import argparse
import enum
import logging
import os
import sys
import typing

import dfxml
from dfxml import objects as Objects

import gddrescue_mapfile_to_dfxml

_logger = logging.getLogger(os.path.basename(__file__))


class ParseState(enum.Enum):
    FILE_OPENED = 0
    PRE_TABLE = 1
    CURRENT_POS_HEAD = 2
    CURRENT_POS_RECORD = 3
    TABLE_HEAD = 4
    IN_TABLE = 5
    STREAM_COMPLETE = 99


STATE_TRANSMISSION_MATRIX: typing.Dict[ParseState, typing.Set[ParseState]] = {
    ParseState.CURRENT_POS_HEAD: {ParseState.CURRENT_POS_RECORD},
    ParseState.CURRENT_POS_RECORD: {ParseState.TABLE_HEAD},
    ParseState.FILE_OPENED: {ParseState.PRE_TABLE},
    ParseState.IN_TABLE: {ParseState.IN_TABLE, ParseState.STREAM_COMPLETE},
    ParseState.PRE_TABLE: {ParseState.CURRENT_POS_HEAD, ParseState.PRE_TABLE},
    ParseState.STREAM_COMPLETE: set(),
    ParseState.TABLE_HEAD: {ParseState.IN_TABLE},
}


class MapfileParser(object):
    def __init__(self) -> None:
        self._disk_image_len: typing.Optional[int] = None
        self._state: typing.Optional[ParseState] = None
        self._line_no: typing.Optional[int] = None

    def parse(self, in_fh: typing.TextIO) -> Objects.DFXMLObject:
        """
        Returns a DFXMLObject.
        """
        command_parts = []
        command_name_basename = os.path.basename(sys.argv[0])
        command_parts.append(command_name_basename)
        command_parts.extend(sys.argv[1:])

        dobj = Objects.DFXMLObject(version="1.2.0+")
        dobj.program = command_name_basename
        dobj.program_version = gddrescue_mapfile_to_dfxml.__version__
        dobj.command_line = " ".join(command_parts)
        dobj.dc["type"] = "Disk image sector map"
        dobj.add_creator_library(
            "Python", ".".join(map(str, sys.version_info[0:3]))
        )  # A bit of a bend, but gets the major version information out.
        dobj.add_creator_library("Objects.py", Objects.__version__)
        dobj.add_creator_library("dfxml.py", dfxml.__version__)
        diobj = Objects.DiskImageObject()
        dobj.append(diobj)
        brs = Objects.ByteRuns()
        diobj.byte_runs = brs

        dobj.add_namespace("gddr", dfxml.XMLNS_DFXML + "#gddrescue")

        self._state = ParseState.FILE_OPENED
        self._disk_image_len = 0

        for (line_no, line) in enumerate(in_fh):
            self._line_no = line_no

            cleaned_line = line.strip()
            if cleaned_line.startswith("0x"):
                if self._state in (ParseState.TABLE_HEAD, ParseState.IN_TABLE):
                    self.transition(ParseState.IN_TABLE)
                else:
                    self.transition(ParseState.CURRENT_POS_RECORD)
            elif cleaned_line == "#      pos        size  status":
                self.transition(ParseState.TABLE_HEAD)
            elif cleaned_line == "# current_pos  current_status  current_pass":
                self.transition(ParseState.CURRENT_POS_HEAD)
            else:
                self.transition(ParseState.PRE_TABLE)

            if self._state != ParseState.IN_TABLE:
                continue

            br = Objects.ByteRun()

            line_parts = cleaned_line.split("  ")
            br.img_offset = int(line_parts[0], base=16)
            br.len = int(line_parts[1], base=16)

            self._disk_image_len = br.img_offset + br.len

            # TODO
            # Independent design decision, while awaiting a consensus design:
            #   Only report the byte runs ddrescue was able to collect.
            if line_parts[2] != "+":
                continue
            brs.append(br)

        diobj.filesize = self._disk_image_len
        _logger.info("diobj.filesize = %r." % diobj.filesize)

        self.transition(ParseState.STREAM_COMPLETE)
        return dobj

    def transition(self, to_state: ParseState) -> None:
        assert self._state is not None
        if to_state not in STATE_TRANSMISSION_MATRIX[self._state]:
            assert self._line_no is not None
            _logger.info("self._line_no = %d.", self._line_no)
            raise ValueError(
                "Unexpected state transition: %r -> %r." % (self._state, to_state)
            )
        self._state = to_state


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-d", "--debug", action="store_true")
    argument_parser.add_argument("in_mapfile")
    argument_parser.add_argument("out_dfxml")
    args = argument_parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    with open(args.out_dfxml, "w") as out_fh:
        with open(args.in_mapfile, "r") as in_fh:
            parser = MapfileParser()
            dobj = parser.parse(in_fh)
            dobj.print_dfxml(output_fh=out_fh)


if __name__ == "__main__":
    main()

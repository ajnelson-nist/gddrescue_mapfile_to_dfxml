# Report of file recoverability

Of 1,000,204,886,016 bytes (1 TB) of the original disk, 1,073,742,336
bytes (1.07 GB) are not in the acquired disk image.

11 files were affected.

| FS \# | Offset   | Length        | Type      |
| ----- | -------- | ------------- | --------- |
| 1     | 10485760 | 1000194400256 | examplefs |

Table 1. File systems

| FS \# | Type | Size (bytes) | Missing bytes | Path                                          |
| ----- | ---- | ------------ | ------------- | --------------------------------------------- |
| 1     | `v`  | 512          | 512           | `first_sector.bin`                            |
| 1     | `v`  | 4000         | 512           | `first_four_kilobytes.bin`                    |
| 1     | `r`  | 8192         | 4096          | `contiguous_around_bad_region_left_edge.dat`  |
| 1     | `r`  | 4096         | 4096          | `contiguous_in_bad_region.dat`                |
| 1     | `r`  | 8192         | 4096          | `contiguous_around_bad_region_right_edge.dat` |
| 1     | `r`  | 12288        | 12288         | `fragmented_all_inside_bad_region.dat`        |
| 1     | `r`  | 8192         | 4096          | `fragmented_beginning_inside_bad_region.dat`  |
| 1     | `r`  | 12288        | 4096          | `fragmented_middle_inside_bad_region.dat`     |
| 1     | `r`  | 8192         | 4096          | `fragmented_end_inside_bad_region.dat`        |
| 1     | `r`  | 4096         | 4096          | `after_disk_image_end.dat`                    |
| 1     | `d`  | 12288        | 4096          | `fragmented_partially_recoverable_directory`  |

Table 2. Affected files

Note that "FS \#" is a simple incrementing integer defined only in this
report. A missing "FS \#" indicates the input DFXML did not have the
file associated with a file system.

The file type code is the DFXML encoding of `name_type`. `r` is a
regular file; `d` a directory; and `v` a "virtual" file, a file that is
not precisely a file in the file system, but is treated as a file by the
tool that parsed the file system.

The "Size" column is the size of the file according to the file system.
"Missing bytes" indicates how many bytes of the file were not captured
in the disk image.

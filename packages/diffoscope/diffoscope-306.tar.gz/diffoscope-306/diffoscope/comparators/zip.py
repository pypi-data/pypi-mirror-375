#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2022, 2024-2025 Chris Lamb <lamby@debian.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.


import functools
import re
import sys
import shutil
import os.path
import zipfile

from diffoscope.config import Config
from diffoscope.tools import tool_required
from diffoscope.difference import Difference
from diffoscope.exc import ContainerExtractionError, RequiredToolNotFound
from diffoscope.tempfiles import get_named_temporary_file

from .utils.file import File
from .directory import Directory
from .utils.archive import Archive, ArchiveMember
from .utils.command import Command, our_check_output


@functools.lru_cache()
def zipdetails_version():
    return our_check_output(["zipdetails", "--version"]).decode("UTF-8")


class Zipinfo(Command):
    # zipinfo returns with an exit code of 1 or 2 when reading
    # Mozilla-optimized or Java "jmod" ZIPs as they have non-standard headers
    # which are safe to ignore.
    VALID_RETURNCODES = {0, 1, 2}

    re_strip_path = re.compile(r"^(warning|error) \[[^\]]+\]:\s+(.*)$")

    @tool_required("zipinfo")
    def cmdline(self):
        return ["zipinfo", self.path]

    def filter(self, line):
        # we don't care about the archive file path
        if line.startswith(b"Archive:"):
            return b""

        # Strip paths from errors and warnings
        # eg: "warning [/full/path]: 472 extra bytes at beginning or within zipfile"
        m = self.re_strip_path.match(line.decode("utf-8", "surrogateescape"))
        if m is not None:
            return "{}: {}\n".format(m.group(1), m.group(2)).encode("utf-8")

        return line


class ZipinfoVerbose(Zipinfo):
    @tool_required("zipinfo")
    def cmdline(self):
        return ["zipinfo", "-v", self.path]


class Zipnote(Command):
    # zipnote returns with an exit code of 3 for invalid archives
    VALID_RETURNCODES = {0, 3}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.flag = False

    @tool_required("zipnote")
    def cmdline(self):
        path = self.path
        if not path.endswith(".zip"):
            path = get_named_temporary_file(suffix=".zip").name
            shutil.copy(self.path, path)
        return ["zipnote", path]

    def filter(self, line):
        """
        Example output from zipnote(1):

            @ foo
            hello
            @ (comment above this line)
            @ (zip file comment below this line)
            goodbye
        """

        if line == b"@ (zip file comment below this line)\n":
            self.flag = True
            return b"Zip file comment: "

        if line == b"@ (comment above this line)\n":
            self.flag = False
            return b"\n\n"  # spacer

        if line.startswith(b"@ "):
            filename = line[2:-1].decode()
            self.flag = True
            return f"Filename: {filename}\nComment: ".encode()

        return line[:-1] if self.flag else b""


class BsdtarVerbose(Command):
    @tool_required("bsdtar")
    def cmdline(self):
        return ["bsdtar", "-tvf", self.path]


def zipinfo_differences(file, other):
    """
    Run all our zipinfo variants.
    """

    # We need to run both "zipinfo" and "zipinfo -v" in all code paths, so just
    # run them both first.
    zipinfo = Difference.from_operation(Zipinfo, file.path, other.path)
    verbose = Difference.from_operation(ZipinfoVerbose, file.path, other.path)

    # First try and prefer "zipinfo"...
    if zipinfo is not None:
        # ... but if "zipinfo -v" indicates we have differences in .zip
        # directory "extra fields", add a comment and prefer that output.
        if re.search(
            r"[-+]  The central-directory extra field contains:",
            verbose.unified_diff,
        ):
            verbose.add_comment(
                "Differences in extra fields detected; using output from zipinfo -v"
            )
            return [verbose]

        return [zipinfo]

    # If none of this was detected, fallback to "zipinfo -v"...
    if verbose is not None:
        return [verbose]

    # ... and, finally, "bsdtar -tvz"
    bsdtar = Difference.from_operation(BsdtarVerbose, file.path, other.path)
    if bsdtar is not None:
        return [bsdtar]

    return []


class Zipdetails(Command):
    @tool_required("zipdetails")
    def cmdline(self):
        # See <https://salsa.debian.org/reproducible-builds/diffoscope/-/issues/406>
        # for discussion of zipdetails command line arguments.
        #
        # Older zipdetails does not support --walk; added in Debian
        # 5.40.0~rc1-1, but "zipdetails --version" shipped in, say, perl
        # 5.36.0-7+deb12u1 returns "2.104".
        #
        # See <https://salsa.debian.org/reproducible-builds/diffoscope/-/issues/408>
        #
        if float(zipdetails_version()) < 4.0:
            return ["zipdetails", "--redact", "--utc", self.path]

        return ["zipdetails", "--redact", "--walk", "--utc", self.path]


class ZipDirectory(Directory, ArchiveMember):
    def __init__(self, archive, member_name):
        ArchiveMember.__init__(self, archive, member_name)

    def compare(self, other, source=None):
        return None

    def has_same_content_as(self, other):
        return False

    def is_directory(self):
        return True

    def get_member_names(self):
        raise ValueError("Zip archives are compared as a whole.")  # noqa

    def get_member(self, member_name):
        raise ValueError("Zip archives are compared as a whole.")  # noqa


class ZipContainer(Archive):
    def open_archive(self):
        zf = zipfile.ZipFile(self.source.path, "r")
        self.name_to_info = {}
        self.duplicate_entries = 0
        for info in zf.infolist():
            if info.filename not in self.name_to_info:
                self.name_to_info[info.filename] = info
            else:
                self.duplicate_entries += 1
        return zf

    def close_archive(self):
        self.archive.close()

    def get_member_names(self):
        return self.archive.namelist()

    def extract(self, member_name, dest_dir):
        # We don't really want to crash if the filename in the zip archive
        # can't be encoded using the filesystem encoding. So let's replace
        # any weird character so we can get to the bytes.
        targetpath = os.path.join(
            dest_dir, os.path.basename(member_name)
        ).encode(sys.getfilesystemencoding(), errors="replace")

        try:
            info = self.name_to_info[member_name]
            with self.archive.open(info) as source, open(
                targetpath, "wb"
            ) as target:
                shutil.copyfileobj(source, target)
            return targetpath.decode(sys.getfilesystemencoding())
        except zipfile.BadZipFile as e:
            raise ContainerExtractionError(member_name, e)
        except RuntimeError as e:
            # Handle encrypted files see line 1292 of zipfile.py
            is_encrypted = self.archive.getinfo(member_name).flag_bits & 0x1
            if is_encrypted:
                raise ContainerExtractionError(member_name, e)
            raise

    def get_member(self, member_name):
        zipinfo = self.archive.getinfo(member_name)
        if zipinfo.filename[-1] == "/":
            return ZipDirectory(self, member_name)
        return ArchiveMember(self, member_name)


class ZipFileBase(File):
    def compare(self, other, source=None):
        x = super().compare(other, source)

        if x is None:
            return None

        # If we have at least one differences, then we have observed
        # differences within a nested file. If not, there is likely some
        # difference in the metadata that zipinfo cannot discover, so we
        # manually fallback to a binary diff.
        if len(x.details) >= 1:
            return x

        x.add_comment(
            "Archive contents identical but files differ, possibly due "
            "to different compression levels. Falling back to binary "
            "comparison."
        )

        details = self.compare_bytes(other, source=source)
        if details is not None:
            x.add_details([details])

        return x


class ZipFile(ZipFileBase):
    DESCRIPTION = "ZIP archives"
    CONTAINER_CLASSES = [ZipContainer]
    FILE_TYPE_RE = re.compile(
        r"^((?:iOS App )?Zip archive|Java archive|EPUB document|OpenDocument (Text|Spreadsheet|Presentation|Drawing|Formula|Template|Text Template)|Google Chrome extension)\b"
    )

    def compare(self, other, source=None):
        x = super().compare(other, source)

        if x is None:
            return None

        self_dups = getattr(self.as_container, "duplicate_entries", 0)
        other_dups = getattr(other.as_container, "duplicate_entries", 0)
        if self_dups:
            x.add_comment(f"{self.name!r} has {self_dups} duplicate entries")
        if other_dups:
            x.add_comment(f"{other.name!r} has {other_dups} duplicate entries")

        return x

    def compare_details(self, other, source=None):
        differences = []
        if Config().exclude_directory_metadata != "recursive":
            differences.extend(zipinfo_differences(self, other))

        for op in (Zipnote, Zipdetails):
            try:
                differences.append(
                    Difference.from_operation(op, self.path, other.path)
                )
            except RequiredToolNotFound:  # noqa
                pass

        return differences


class MozillaZipContainer(ZipContainer):
    def open_archive(self):
        # This is gross: Monkeypatch zipfile._EndRecData to work with
        # Mozilla-optimized ZIPs
        _orig_EndRecData = zipfile._EndRecData
        eocd_offset = None

        def _EndRecData(fh):
            endrec = _orig_EndRecData(fh)
            if endrec:
                nonlocal eocd_offset
                eocd_offset = endrec[zipfile._ECD_LOCATION]
                endrec[zipfile._ECD_LOCATION] = (
                    endrec[zipfile._ECD_OFFSET] + endrec[zipfile._ECD_SIZE]
                )
            return endrec

        zipfile._EndRecData = _EndRecData
        result = super(MozillaZipContainer, self).open_archive()
        zipfile._EndRecData = _orig_EndRecData
        # fix _end_offset after https://github.com/python/cpython/pull/110016
        # added a check that fails because the central directory comes before
        # the entries in these files
        zinfos = sorted(
            result.filelist,
            key=lambda zinfo: zinfo.header_offset,
            reverse=True,
        )
        if zinfos:
            if hasattr(zinfos[0], "_end_offset"):
                zinfos[0]._end_offset = eocd_offset
        return result


class MozillaZipFile(ZipFile):
    DESCRIPTION = "Mozilla-optimized .ZIP archives"
    CONTAINER_CLASSES = [MozillaZipContainer]

    @classmethod
    def recognizes(cls, file):
        # Mozilla-optimized ZIPs start with a 32-bit little endian integer
        # indicating the amount of data to preload, followed by the ZIP
        # central directory (with a PK\x01\x02 signature)
        return file.file_header[4:8] == b"PK\x01\x02"


class NuGetPackageFile(ZipFile):
    DESCRIPTION = "NuGet packages"
    CONTAINER_CLASSES = [ZipContainer]
    FILE_TYPE_HEADER_PREFIX = b"PK\x03\x04"
    FILE_EXTENSION_SUFFIX = {".nupkg"}


class JmodJavaModule(ZipFile):
    DESCRIPTION = "Java .jmod modules"
    FILE_TYPE_RE = re.compile(r"^(Zip archive data|Java jmod module)")

    @classmethod
    def recognizes(cls, file):
        # Not all versions of file(1) support the detection of these
        # modules yet so we perform our own manual check for a "JM" prefix.
        return file.file_header[:2] == b"JM"

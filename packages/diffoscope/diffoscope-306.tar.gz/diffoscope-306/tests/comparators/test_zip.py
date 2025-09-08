#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2020, 2022, 2024-2025 Chris Lamb <lamby@debian.org>
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

import pytest
import subprocess

from diffoscope.comparators.zip import (
    ZipFile,
    MozillaZipFile,
    NuGetPackageFile,
    JmodJavaModule,
    zipdetails_version,
)

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import skip_unless_tools_exist, skip_unless_tool_is_at_least
from ..utils.nonexisting import assert_non_existing


zip1 = load_fixture("test1.zip")
zip2 = load_fixture("test2.zip")
zip3 = load_fixture("test3.zip")
encrypted_zip1 = load_fixture("encrypted1.zip")
encrypted_zip2 = load_fixture("encrypted2.zip")
mozzip1 = load_fixture("test1.mozzip")
mozzip2 = load_fixture("test2.mozzip")
nupkg1 = load_fixture("test1.nupkg")
nupkg2 = load_fixture("test2.nupkg")
jmod1 = load_fixture("test1.jmod")
jmod2 = load_fixture("test2.jmod")
test_comment1 = load_fixture("test_comment1.zip")
test_comment2 = load_fixture("test_comment2.zip")


def io_compress_zip_version():
    try:
        return subprocess.check_output(
            [
                "perl",
                "-MIO::Compress::Zip",
                "-e",
                "print $IO::Compress::Zip::VERSION",
            ]
        ).decode("UTF-8")
    except subprocess.CalledProcessError:
        return "-1"


def test_identification(zip1):
    assert isinstance(zip1, ZipFile)


def test_no_differences(zip1):
    difference = zip1.compare(zip1)
    assert difference is None


@pytest.fixture
def differences(zip1, zip2):
    return zip1.compare(zip2).details


@pytest.fixture
def differences2(zip1, zip3):
    return zip1.compare(zip3).details


@skip_unless_tools_exist("zipinfo", "zipdetails")
@skip_unless_tool_is_at_least("zipdetails", zipdetails_version, "4.004")
@skip_unless_tool_is_at_least("perl", io_compress_zip_version, "2.212")
def test_metadata(differences):
    assert_diff(differences[0], "zip_zipinfo_expected_diff")
    assert_diff(differences[1], "zip_zipdetails_expected_diff")


@skip_unless_tools_exist("zipinfo", "zipdetails")
def test_compressed_files(differences):
    assert differences[2].source1 == "dir/text"
    assert differences[2].source2 == "dir/text"
    assert_diff(differences[2], "text_ascii_expected_diff")


@skip_unless_tools_exist("zipinfo", "bsdtar", "zipdetails")
@skip_unless_tool_is_at_least("perl", io_compress_zip_version, "2.212")
def test_extra_fields(differences2):
    assert_diff(differences2[0], "zip_bsdtar_expected_diff")
    assert_diff(differences2[1], "zip2_zipdetails_expected_diff")


@skip_unless_tools_exist("zipinfo")
def test_compare_non_existing(monkeypatch, zip1):
    assert_non_existing(monkeypatch, zip1)


def test_mozzip_identification(mozzip1):
    assert isinstance(mozzip1, MozillaZipFile)


def test_mozzip_no_differences(mozzip1):
    difference = mozzip1.compare(mozzip1)
    assert difference is None


@pytest.fixture
def mozzip_differences(mozzip1, mozzip2):
    return mozzip1.compare(mozzip2).details


@skip_unless_tools_exist("zipinfo")
def test_mozzip_metadata(mozzip_differences, mozzip1, mozzip2):
    assert_diff(mozzip_differences[0], "mozzip_zipinfo_expected_diff")


@skip_unless_tools_exist("zipinfo")
def test_mozzip_compressed_files(mozzip_differences):
    assert mozzip_differences[-1].source1 == "dir/text"
    assert mozzip_differences[-1].source2 == "dir/text"
    assert_diff(mozzip_differences[-1], "text_ascii_expected_diff")


@skip_unless_tools_exist("zipinfo")
def test_mozzip_compare_non_existing(monkeypatch, mozzip1):
    assert_non_existing(monkeypatch, mozzip1)


def test_nupkg_identification(nupkg1):
    assert isinstance(nupkg1, NuGetPackageFile)


def test_nupkg_no_differences(nupkg1):
    difference = nupkg1.compare(nupkg1)
    assert difference is None


@pytest.fixture
def nupkg_differences(nupkg1, nupkg2):
    return nupkg1.compare(nupkg2).details


@skip_unless_tools_exist("zipinfo")
def test_nupkg_metadata(nupkg_differences, nupkg1, nupkg2):
    assert_diff(nupkg_differences[0], "nupkg_expected_diff")


@skip_unless_tools_exist("zipinfo")
def test_nupkg_compressed_files(nupkg_differences):
    assert (
        nupkg_differences[-1].source1
        == "package/services/metadata/core-properties/b44ebb537bbf4983b9527f9e3820fda6.psmdcp"
    )
    assert (
        nupkg_differences[-1].source2
        == "package/services/metadata/core-properties/08f1f9d8789a4668a128f78560bd0107.psmdcp"
    )


@skip_unless_tools_exist("zipinfo")
def test_nupkg_compare_non_existing(monkeypatch, nupkg1):
    assert_non_existing(monkeypatch, nupkg1)


def test_jmod_identification(jmod1):
    assert isinstance(jmod1, JmodJavaModule)


def test_jmod_no_differences(jmod1):
    difference = jmod1.compare(jmod1)
    assert difference is None


@pytest.fixture
def jmod_differences(jmod1, jmod2):
    return jmod1.compare(jmod2).details


@skip_unless_tools_exist("zipinfo", "zipdetails", "zipnote")
@skip_unless_tool_is_at_least("perl", io_compress_zip_version, "2.212")
def test_jmod_metadata(jmod_differences, jmod1, jmod2):
    assert jmod_differences[0].source1 == "zipinfo {}"
    assert jmod_differences[1].source1.startswith("zipnote")
    assert jmod_differences[2].source1.startswith("zipdetails")
    assert_diff(jmod_differences[0], "jmod_zipinfo_expected_diff")
    assert_diff(jmod_differences[2], "jmod_zipdetails_expected_diff")


def test_encrypted(encrypted_zip1, encrypted_zip2):
    difference = encrypted_zip1.compare(encrypted_zip2)
    assert difference is not None


@pytest.fixture
def comment_differences(test_comment1, test_comment2):
    return test_comment1.compare(test_comment2).details


@skip_unless_tools_exist("zipnote", "zipdetails")
@skip_unless_tool_is_at_least("zipdetails", zipdetails_version, "4.004")
def test_commented(comment_differences):
    assert_diff(comment_differences[1], "comment_zipinfo_expected_diff")
    assert_diff(comment_differences[2], "comment_zipdetails_expected_diff")

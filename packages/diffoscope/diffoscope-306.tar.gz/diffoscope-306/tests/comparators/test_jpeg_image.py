#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017, 2020, 2023-2024 Chris Lamb <lamby@debian.org>
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

from diffoscope.config import Config
from diffoscope.comparators.image import JPEGImageFile
from diffoscope.comparators.missing_file import MissingFile

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import skip_unless_tools_exist, skip_unless_tool_is_between


image1 = load_fixture("test1.jpg")
image2 = load_fixture("test2.jpg")
image1_meta = load_fixture("test1_meta.jpg")
image2_meta = load_fixture("test2_meta.jpg")


def imagemagick_version(command):
    out = subprocess.check_output([command, "-version"]).decode("utf-8")
    # First line is expected to look like
    # "Version: ImageMagick 6.9.6-6 Q16 x86_64 20161125 ..."
    if not out.startswith("Version: ImageMagick "):
        return "0.0.0"
    return out.splitlines()[0].split()[2].strip()


def test_identification(image1):
    assert isinstance(image1, JPEGImageFile)


def test_no_differences(image1):
    difference = image1.compare(image1)
    assert difference is None


@pytest.fixture
def differences(image1, image2):
    return image1.compare(image2).details


@skip_unless_tools_exist("img2txt", "identify")
def test_diff(differences):
    assert_diff(differences[0], "jpeg_image_expected_diff")


@skip_unless_tools_exist("img2txt", "identify")
def test_compare_non_existing(monkeypatch, image1):
    monkeypatch.setattr(Config(), "new_file", True)
    difference = image1.compare(MissingFile("/nonexisting", image1))
    assert difference.source2 == "/nonexisting"
    assert len(difference.details) > 0


@pytest.fixture
def differences_meta(image1_meta, image2_meta):
    return image1_meta.compare(image2_meta).details


@skip_unless_tools_exist("img2txt", "identify")
@skip_unless_tool_is_between(
    "identify", lambda: imagemagick_version("identify"), "6.9.6", "7.0.0"
)
def test_diff_meta(differences_meta):
    assert_diff(differences_meta[-1], "jpeg_image_meta_expected_diff")


@skip_unless_tool_is_between(
    "convert", lambda: imagemagick_version("convert"), "6.9.6", "7.0.0"
)
@skip_unless_tools_exist("img2txt", "convert", "identify")
def test_has_visuals(monkeypatch, image1, image2):
    monkeypatch.setattr(Config(), "compute_visual_diffs", True)
    jpg_diff = image1.compare(image2)
    assert len(jpg_diff.details) == 2
    assert len(jpg_diff.details[0].visuals) == 2
    assert jpg_diff.details[0].visuals[0].data_type == "image/png;base64"
    assert jpg_diff.details[0].visuals[1].data_type == "image/gif;base64"

#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017 Juliana Rodrigues <juliana.orod@gmail.com>
# Copyright © 2017-2022, 2025 Chris Lamb <lamby@debian.org>
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

import re
import pyexpat
import logging

from xml.parsers.expat import ExpatError

from diffoscope.comparators.utils.file import File
from diffoscope.difference import Difference
from diffoscope.tools import python_module_missing

from .missing_file import MissingFile

try:
    defusedxml = True
    from defusedxml import minidom
except ImportError:
    defusedxml = False
    python_module_missing("defusedxml")
    from xml.dom import minidom


def is_vulnerable_xml_parser():
    # We assume defusedxml is safe
    if defusedxml:
        return False

    """
    As described in Pythons module documentation versions of expat <= 2.4.1
    (released on 2021-05-23) are vulnerable to exponential/quadratic entity
    expansion while versions <= 2.6.0 (released on 2024-02-06) are vulnerable to
    large tokens. Since expat is usually provided by the system and not
    directly bundled with Python, even recent Python installations can still be
    vulnerable due to old expat versions.

        <https://salsa.debian.org/reproducible-builds/diffoscope/-/issues/397>
    """

    pyexpat_version = tuple(
        int(x) for x in pyexpat.EXPAT_VERSION.split("_", 1)[1].split(".")
    )

    return pyexpat_version < (2, 6, 0)


logger = logging.getLogger(__name__)
if is_vulnerable_xml_parser():
    logger.warning(
        "Vulnerable version of pyexpat detected; disabling comparison of XML documents. Install defusedxml or upgrade your pyexpat."
    )


def _format(node):
    """
    Removes *inplace* spaces from minidom.Document

    Args:
        node -- A xml.dom.minidom.Document object

    Returns:
        void
    """
    for n in node.childNodes:
        if n.nodeType == n.TEXT_NODE:
            if n.nodeValue:
                n.nodeValue = n.nodeValue.strip()
        elif n.nodeType == n.ELEMENT_NODE:
            _format(n)


def _parse(file):
    """
    Formats a minidom.Document file and returns XML as string.

    Args:
        file -- An io.TextIOWrapper object

    Returns:
        str: formated string object
    """

    if defusedxml:
        xml = minidom.parse(file, forbid_entities=False, forbid_external=False)
    else:
        xml = minidom.parse(file)

    _format(xml)
    xml.normalize()

    return xml.toprettyxml(indent=2 * " ", encoding="utf-8").decode("utf-8")


class XMLFile(File):
    """
    XML Files Comparison class

    Attributes:
        FILE_EXTENSION_SUFFIX (str): xml file extension suffix
    """

    DESCRIPTION = "XML files"
    FILE_TYPE_RE = re.compile(
        r"^(XML \S+ document|GnuCash file|XHTML document)"
    )

    @classmethod
    def recognizes(cls, file):
        """
        Identifies if a given file has XML extension

        Args:
            file - a diffoscope.comparators.utils.file.File object

        Returns:
            False if file is not a XML File, True otherwise
        """

        # Emulate FALLBACK_FILE_EXTENSION_SUFFIX = {".xml"}
        if not super().recognizes(file) and not file.name.endswith(".xml"):
            return False

        # Check that we aren't about to open an untrusted file with an old, and
        # potentially vulnerable, version of pyexpat.
        if is_vulnerable_xml_parser():
            return False

        with open(file.path) as f:
            try:
                file.parsed = _parse(f)
            except (ExpatError, UnicodeDecodeError):
                return False

        return True

    def compare_details(self, other, source=None):
        """
        Compares self.object with another, returning a Difference object

        Args:
            other    -- A XMLFile object
            source

        Returns:
            A diffoscope.difference.Difference object
        """
        if isinstance(other, MissingFile):
            return [
                Difference(
                    self.name,
                    other.name,
                    comment="Trying to compare two non-existing files.",
                )
            ]

        difference = Difference.from_text(
            self.dumps(self), self.dumps(other), self.name, other.name
        )

        if difference:
            difference.check_for_ordering_differences()

        return [difference]

    def dumps(self, file):
        """
        Opens a XMLFile and returns its parsed content

        Args:
            file -- XMLFile object

        Returns:
            str -- Formatted XML content from file
        """
        if file.parsed:
            return file.parsed

        with open(file.path) as f:
            return _parse(f)

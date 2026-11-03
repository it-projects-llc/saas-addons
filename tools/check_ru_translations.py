# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
"""Validate Russian catalogs; requires polib and GNU gettext's msgfmt."""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

import polib

PERCENT = re.compile(
    r"%(?:\([^)]+\))?[#0 +\-]*(?:\d+|\*)?(?:\.(?:\d+|\*))?"
    r"[hlL]?[diouxXeEfFgGcrsa%]"
)
BRACES = re.compile(r"\{(?:\w+)?\}")
URLS = re.compile(r'https?://[^\s<>"`]+')


def markup_structure(value):
    """Allow prose to move while preserving every QWeb node and attribute."""
    tree = ElementTree.fromstring("<root>" + value + "</root>")
    return [(node.tag, sorted(node.attrib.items())) for node in tree.iter()]


def validate_catalog(path):
    catalog = polib.pofile(str(path))
    template = polib.pofile(str(path.with_name(path.parts[-3] + ".pot")))
    assert len(catalog) == len(template), path
    assert not catalog.fuzzy_entries(), path
    assert not catalog.obsolete_entries(), path
    assert catalog.metadata["Language"] == "ru", path
    assert "nplurals=3;" in catalog.metadata["Plural-Forms"], path
    keys = {(entry.msgctxt, entry.msgid) for entry in catalog}
    assert len(keys) == len(catalog), (path, "duplicate entries")
    assert keys == {(entry.msgctxt, entry.msgid) for entry in template}, path

    for entry in catalog:
        context = (path, entry.msgid)
        assert entry.msgstr, (context, "empty translation")
        for pattern in (PERCENT, BRACES):
            assert Counter(pattern.findall(entry.msgid)) == Counter(
                pattern.findall(entry.msgstr)
            ), (context, "placeholders")
        if entry.msgid.startswith("<"):
            assert markup_structure(entry.msgid) == markup_structure(
                entry.msgstr
            ), (context, "markup")
        assert URLS.findall(entry.msgid) == URLS.findall(entry.msgstr), (context, "URLs")
        assert entry.occurrences, (context, "missing source references")

    subprocess.run(
        ["msgfmt", "--check", "--check-format", "-o", "/dev/null", str(path)],
        check=True,
    )
    return len(catalog)


def main():
    root = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parents[1]
    )
    report = {
        path.parts[-3]: validate_catalog(path)
        for path in sorted(root.glob("*/i18n/ru.po"))
    }
    modules = {path.parent.name for path in root.glob("*/__manifest__.py")}
    assert set(report) == modules, (
        "Missing or unexpected catalogs", modules ^ set(report)
    )
    print(json.dumps(
        {
            "modules": len(report),
            "translated_entries": sum(report.values()),
            "per_module": report,
        },
        ensure_ascii=False,
        indent=2,
    ))


if __name__ == "__main__":
    main()

"""Проверки формата APKINDEX и извлечения зависимостей."""

import io
import tarfile
import unittest

from apk_index import dependency_name, extract_index, index_url
from apk_index import package_record, parse_index


INDEX_TEXT = """P:demo
D:libc>=1 so:libz.so.1 !old-demo
p:cmd:demo=2

P:zlib
p:so:libz.so.1=1
"""


class IndexTests(unittest.TestCase):
    def test_metadata(self):
        packages = parse_index(INDEX_TEXT)
        record = package_record(packages, "demo")
        self.assertEqual(record.dependencies, ("libc>=1", "so:libz.so.1"))
        self.assertEqual(record.conflicts, ("!old-demo",))
        self.assertEqual(packages["zlib"].provides, ("so:libz.so.1=1",))

    def test_tar_archive(self):
        content = INDEX_TEXT.encode()
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            member = tarfile.TarInfo("APKINDEX")
            member.size = len(content)
            tar.addfile(member, io.BytesIO(content))
        self.assertEqual(extract_index(buffer.getvalue()), INDEX_TEXT)

    def test_bad_archive_or_index(self):
        with self.assertRaises(ValueError):
            extract_index(b"invalid")
        with self.assertRaises(ValueError):
            parse_index("not an index")

    def test_unknown_package(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            package_record(parse_index(INDEX_TEXT), "missing")

    def test_url_and_expression(self):
        url = "https://example.org/main/x86_64"
        expected = url + "/APKINDEX.tar.gz"
        self.assertEqual(index_url(url), expected)
        self.assertEqual(index_url(expected), expected)
        self.assertEqual(dependency_name("so:libz.so.1>=1"), "so:libz.so.1")

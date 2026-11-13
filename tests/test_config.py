"""Проверки всех параметров TOML."""

import json
import tempfile
import unittest
from pathlib import Path

from config import load_config


class ConfigTests(unittest.TestCase):
    def set_up(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "config.toml"
        self.path.with_name("graph.toml").write_text("A = []\n")
        self.data = dict(package="A", repository="graph.toml",
                         test_mode=True, filter="")

    # Ссылка для unittest, чтобы он вызывал метод перед каждым тестом
    setUp = set_up

    def load(self, **changes):
        """Записать TOML с изменёнными полями."""
        data = self.data | changes
        lines = [f"{key} = {json.dumps(value)}"
                 for key, value in data.items()]
        self.path.write_text("\n".join(lines))
        return load_config(self.path)

    def test_valid_configuration(self):
        config = self.load()
        self.assertEqual(config.package, "A")
        self.assertEqual(config.repository,
                         str(self.path.with_name("graph.toml")))
        self.assertTrue(config.test_mode)
        self.assertEqual(config.filter, "")

    def test_invalid_fields(self):
        for name, value in [("package", "a"), ("repository", "missing"),
                            ("test_mode", "true"), ("filter", 1)]:
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, name):
                    self.load(**{name: value})

    def test_invalid_url(self):
        with self.assertRaisesRegex(ValueError, "repository"):
            self.load(package="zlib", test_mode=False, repository="ftp://a")

    def test_invalid_syntax(self):
        self.path.write_text("package = [")
        with self.assertRaises(ValueError):
            load_config(self.path)

    def test_missing_key(self):
        self.data.pop("filter")
        with self.assertRaisesRegex(ValueError, "filter"):
            self.load()

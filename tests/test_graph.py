"""Проверки порядка BFS, циклов, фильтра и виртуальных имён."""

import unittest
from pathlib import Path
from unittest.mock import patch

from apk_index import parse_index
from config import load_config
from graph import alpine_graph, breadth_first, load_adjacency, test_graph


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


class GraphTests(unittest.TestCase):
    def example(self, filename):
        """Построить граф из конфигурации примера."""
        config = load_config(EXAMPLES / filename)
        return breadth_first(config.package, load_adjacency(config),
                             config.filter)

    def test_shared_dependency(self):
        graph = self.example("test.toml")
        self.assertEqual(list(graph), ["A", "B", "C", "D", "E"])
        self.assertEqual(graph["B"], ["D"])
        self.assertEqual(graph["C"], ["D", "E"])

    def test_cycle(self):
        graph = self.example("test-cycle.toml")
        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(graph["C"], ["A"])

    def test_filter(self):
        self.assertEqual(self.example("test-filter.toml"),
                         {"A": ["B"], "B": ["D"], "D": []})

    def test_long_chain(self):
        length = 1500
        graph = {i: [i + 1] for i in range(length)}
        self.assertEqual(list(breadth_first(0, graph)),
                         list(range(length + 1)))

    def test_virtual_name_and_missing_package(self):
        records = parse_index("P:a\nD:so:x cmd:y so:x !b\n\nP:b\np:so:x=1")
        graph = breadth_first("a", alpine_graph(records))
        self.assertEqual(graph, {"a": ["b", "cmd:y"], "b": [], "cmd:y": []})

    def test_undefined_test_package(self):
        with patch("graph.read_toml", return_value={"A": ["B"]}):
            with self.assertRaisesRegex(ValueError, "неизвестный пакет"):
                test_graph("unused")

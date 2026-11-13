"""Проверки обратных зависимостей в разных топологиях."""

import unittest

from reverse import reverse_dependencies


class ReverseTests(unittest.TestCase):
    def test_direct_and_transitive(self):
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        self.assertEqual(reverse_dependencies("D", graph, ""),
                         (["B", "C"], ["B", "C", "A"]))

    def test_cycle_excludes_root(self):
        graph = {"A": ["B"], "B": ["C"], "C": ["A"], "D": ["C"]}
        self.assertEqual(reverse_dependencies("A", graph, ""),
                         (["C"], ["C", "B", "D"]))

    def test_filter_and_empty(self):
        graph = {"A": ["B"], "B": ["C"], "C": []}
        self.assertEqual(reverse_dependencies("C", graph, "B"), ([], []))
        self.assertEqual(reverse_dependencies("A", graph, ""), ([], []))

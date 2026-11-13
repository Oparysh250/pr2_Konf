"""Проверки формата PlantUML, ошибок и открытия SVG."""

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from visualize import open_image, plantuml_source, render_command, render_svg


class VisualizeTests(unittest.TestCase):
    def test_edges_and_isolated_vertex(self):
        graph = {"zlib": ["musl"], "musl": ["zlib"], "empty": []}
        source = plantuml_source(graph, "zlib")
        self.assertIn('rectangle "zlib" as p0 #DCEEFF', source)
        self.assertIn('rectangle "empty" as p2', source)
        self.assertIn("p0 --> p1\np1 --> p0\n", source)

    def test_missing_renderer(self):
        with patch.dict("os.environ", {"PLANTUML_JAR": ""}):
            with patch("visualize.shutil.which", return_value=None):
                with self.assertRaisesRegex(ValueError, "PLANTUML_JAR"):
                    render_command()

    def test_render_error(self):
        error = subprocess.CalledProcessError(1, "plantuml", stderr=b"bad")
        with patch("visualize.render_command", return_value=["plantuml"]):
            with patch("visualize.subprocess.run", side_effect=error):
                with self.assertRaisesRegex(ValueError, "bad"):
                    render_svg(Path(__file__), Path("unused.svg"))

    def test_browser_uri(self):
        image = Path("out/a.svg")
        with patch("visualize.webbrowser.open", return_value=True) as browser:
            self.assertTrue(open_image(image))
        browser.assert_called_once_with(image.resolve().as_uri(), new=2)

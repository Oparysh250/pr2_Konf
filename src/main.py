"""Точка входа CLI."""

import argparse
import sys
from pathlib import Path

from config import load_config
from graph import breadth_first, load_adjacency
from visualize import open_image, plantuml_source, render_svg


def run(config, show_image):
    """Записать PlantUML и показать полученную диаграмму."""
    graph = breadth_first(config.package, load_adjacency(config),
                          config.filter)
    output = Path("out")
    output.mkdir(exist_ok=True)
    source = output / f"{config.package}.puml"
    image = output / f"{config.package}.svg"
    source.write_text(plantuml_source(graph, config.package), encoding="utf-8")
    render_svg(source, image)
    print(f"PlantUML: {source}")
    print(f"Изображение: {image}")
    if show_image and not open_image(image):
        print("Браузер недоступен. Откройте SVG вручную.", file=sys.stderr)


def main():
    """Обработать аргументы CLI и ошибки пользователя."""
    parser = argparse.ArgumentParser(
        description="Граф зависимостей Alpine Linux"
    )
    parser.add_argument("--config", required=True, help="путь к файлу TOML")
    parser.add_argument("--no-open", action="store_true",
                        help="сохранить PlantUML и SVG без открытия браузера")
    args = parser.parse_args()
    try:
        run(load_config(args.config), not args.no_open)
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Точка входа CLI."""

import argparse
import sys

from config import load_config
from graph import breadth_first, load_adjacency


def run(config):
    """Вывести список смежности в порядке BFS."""
    graph = breadth_first(config.package, load_adjacency(config),
                          config.filter)
    for name, dependencies in graph.items():
        print(f"{name}: " + (", ".join(dependencies) or "—"))


def main():
    """Обработать аргументы CLI и ошибки пользователя."""
    parser = argparse.ArgumentParser(description="Граф зависимостей Alpine Linux")
    parser.add_argument("--config", required=True, help="путь к файлу TOML")
    args = parser.parse_args()
    try:
        run(load_config(args.config))
    except (ValueError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Точка входа CLI."""

import argparse
import sys

from config import load_config
from graph import load_adjacency
from reverse import reverse_dependencies


def run(config):
    """Показать пакеты, которые зависят от указанного пакета."""
    direct, all_dependents = reverse_dependencies(
        config.package, load_adjacency(config), config.filter
    )
    print(f"Обратные зависимости {config.package}:")
    print("Прямые: " + (", ".join(direct) or "нет"))
    print("Прямые и транзитивные: " + (", ".join(all_dependents) or "нет"))


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

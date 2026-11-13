"""Точка входа CLI."""

import argparse
import sys

from apk_index import package_record, read_packages
from config import load_config


def run(config):
    """Вывести прямые зависимости как они записаны в метаданных."""
    if config.test_mode:
        raise ValueError("На этапе 2 требуется URL индекса Alpine")
    record = package_record(read_packages(config.repository), config.package)
    print(f"Прямые зависимости {config.package}:")
    print("\n".join(record.dependencies) or "нет")
    if record.conflicts:
        print("Конфликты: " + ", ".join(record.conflicts))


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

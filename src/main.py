"""Точка входа CLI."""

import argparse
import sys

from config import load_config


def run(config):
    """Напечатать все параметры прототипа в формате ключ=значение."""
    print(f"package={config.package}")
    print(f"repository={config.repository}")
    print(f"test_mode={str(config.test_mode).lower()}")
    print(f"filter={config.filter}")


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

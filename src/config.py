"""Загрузка и проверка конфигурации."""

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import tomllib


PACKAGE_NAME = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9+_.-]*")
TEST_NAME = re.compile(r"[A-Z]+")
KEYS = {"package", "repository", "test_mode", "filter"}


@dataclass(frozen=True)
class Config:
    """Настройки CLI после проверки."""

    package: str
    repository: str
    test_mode: bool
    filter: str


def read_toml(path):
    """Загрузить TOML в безопасном режиме."""
    try:
        return tomllib.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"{path}: {error}") from error


def validate_keys(data):
    """Убедиться, что присутствуют ровно четыре нужных ключа."""
    if not isinstance(data, dict):
        raise ValueError("Конфигурация должна быть словарём TOML")
    missing = KEYS - data.keys()
    extra = data.keys() - KEYS
    if missing:
        raise ValueError("Отсутствуют ключи: " + ", ".join(sorted(missing)))
    if extra:
        names = ", ".join(sorted(map(str, extra)))
        raise ValueError(f"Неизвестные ключи: {names}")


def repository_location(value, test_mode, config_path):
    """Вернуть путь к тестовому файлу либо корректный HTTP(S) URL."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("repository: укажите непустую строку")
    if test_mode:
        path = config_path.parent / value
        if not path.is_file():
            raise ValueError(f"repository: файл не найден: {path}")
        return str(path)
    try:
        url = urlsplit(value)
        valid = url.scheme in {"http", "https"} and url.hostname and (
            url.port is None or url.port
        )
    except ValueError:
        valid = False
    if not valid or re.search(r"\s", value):
        raise ValueError("repository: требуется корректный HTTP(S) URL")
    return value


def _validate_types_and_package(data):
    """Проверить типы данных и имя пакета."""
    test_mode = data["test_mode"]
    if type(test_mode) is not bool:
        raise ValueError("test_mode: требуется логическое true или false")
    
    package = data["package"]
    pattern = TEST_NAME if test_mode else PACKAGE_NAME
    if not isinstance(package, str) or not pattern.fullmatch(package):
        raise ValueError("package: недопустимое имя пакета для этого режима")
    
    substring = data["filter"]
    if not isinstance(substring, str):
        raise ValueError("filter: требуется строка, допустима пустая")
        
    return test_mode, package, substring


def _check_and_validate(data):
    """Внутренняя проверка конфигурации."""
    validate_keys(data)
    return _validate_types_and_package(data)


def load_config(path):
    """Проверить типы, имя пакета и местоположение репозитория."""
    path = Path(path)
    data = read_toml(path)
    
    test_mode, package, substring = _check_and_validate(data)
    repository = repository_location(data["repository"], test_mode, path)
    
    return Config(package, repository, test_mode, substring)

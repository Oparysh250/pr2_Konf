"""Загрузка и разбор APKINDEX без менеджера пакетов."""

import io
import re
import tarfile
from dataclasses import dataclass
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen


INDEX = "APKINDEX.tar.gz"
TIMEOUT = 30
VERSION_OPERATOR = re.compile(r"[<>=~]")


@dataclass(frozen=True)
class Package:
    """Обязательные зависимости, конфликты и предоставляемые имена."""

    dependencies: tuple[str, ...]
    conflicts: tuple[str, ...]
    provides: tuple[str, ...]


def index_url(repository):
    """Добавить имя архива к URL каталога архитектуры."""
    url = urlsplit(repository)
    if url.path.endswith("/" + INDEX):
        return repository
    path = url.path.rstrip("/") + "/" + INDEX
    return url._replace(path=path).geturl()


def extract_index(payload):
    """Прочитать только запись APKINDEX, без распаковки файлов на диск."""
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as tar:
            member = tar.getmember("APKINDEX")
            if not member.isfile():
                raise ValueError("APKINDEX должен быть обычным файлом")
            with tar.extractfile(member) as source:
                return source.read().decode("utf-8")
    except (tarfile.TarError, KeyError, EOFError, UnicodeError) as error:
        raise ValueError(f"Некорректный архив {INDEX}: {error}") from error


def download_index(repository):
    """Скачать метаданные из официального каталога или совместимого зеркала."""
    url = index_url(repository)
    try:
        with urlopen(url, timeout=TIMEOUT) as response:
            return extract_index(response.read())
    except (URLError, OSError) as error:
        raise ValueError(f"Ошибка загрузки {url}: {error}") from error


def _parse_record(record):
    """Разобрать одну запись APKINDEX и вернуть имя пакета и его данные."""
    fields = {}
    for line in record.splitlines():
        if len(line) > 1 and line[1] == ":":
            key, value = line.split(":", 1)
            fields[key] = value

    if "P" not in fields:
        return None, None

    dependencies = fields.get("D", "").split()
    deps = tuple(item for item in dependencies if not item.startswith("!"))
    conflicts = tuple(item for item in dependencies if item.startswith("!"))
    provides = tuple(fields.get("p", "").split())

    return fields["P"], Package(deps, conflicts, provides)


def parse_index(text):
    """Разобрать P, D и p из записей APKINDEX."""
    packages = {}
    records = text.replace("\r\n", "\n").split("\n\n")
    
    for record in records:
        name, package = _parse_record(record)
        if name is not None:
            packages.setdefault(name, package)

    if not packages:
        raise ValueError("В APKINDEX нет записей о пакетах")
    return packages


def read_packages(repository):
    """Получить словарь пакетов из индекса по URL."""
    return parse_index(download_index(repository))


def dependency_name(expression):
    """Извлечь имя пакета или виртуальной зависимости."""
    return VERSION_OPERATOR.split(expression, maxsplit=1)[0]


def package_record(packages, name):
    """Найти целевой пакет или сообщить об ошибке."""
    if name not in packages:
        raise ValueError(f"Пакет {name} отсутствует в APKINDEX")
    return packages[name]

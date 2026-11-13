"""Рекурсивный BFS и источники рёбер графа."""

from collections import deque

from apk_index import dependency_name, package_record, read_packages
from config import TEST_NAME, read_toml


BFS_BATCH = 128


def valid_test_name(value):
    """Проверить имя пакета тестового репозитория."""
    return isinstance(value, str) and TEST_NAME.fullmatch(value) is not None


def test_graph(path):
    """Прочитать TOML со списком смежности и проверить ссылки."""
    graph = read_toml(path)
    for name, dependencies in graph.items():
        if not valid_test_name(name):
            raise ValueError(f"Недопустимое имя тестового пакета: {name}")
        if not isinstance(dependencies, list):
            raise ValueError(f"{name}: требуется список зависимостей")
        for dependency in dependencies:
            if not valid_test_name(dependency) or dependency not in graph:
                raise ValueError(f"{name}: неизвестный пакет {dependency!r}")
    return graph


def provider_map(packages):
    """Сопоставить виртуальные имена пакетам, которые их предоставляют."""
    providers = {}
    for name, record in sorted(packages.items()):
        for expression in record.provides:
            providers.setdefault(dependency_name(expression), name)
    return providers


def alpine_graph(packages):
    """Разрешить зависимости по имени пакета или предоставляемому имени."""
    providers = provider_map(packages)
    graph = {}
    for name, record in packages.items():
        dependencies = []
        for expression in record.dependencies:
            target = dependency_name(expression)
            if target not in packages:
                target = providers.get(target, target)
            dependencies.append(target)
        graph[name] = dependencies
    return graph


def load_adjacency(config):
    """Получить исходный граф и проверить наличие целевого пакета."""
    if config.test_mode:
        graph = test_graph(config.repository)
        if config.package not in graph:
            raise ValueError(f"Пакет {config.package} отсутствует в графе")
        return graph
    packages = read_packages(config.repository)
    package_record(packages, config.package)
    return alpine_graph(packages)


def visit_queue(queue, visited, result, adjacency, substring, budget):
    """Рекурсивно обработать до budget элементов одной FIFO-очереди."""
    if not queue or not budget:
        return
    package = queue.popleft()
    dependencies = dict.fromkeys(adjacency.get(package, ()))
    result[package] = []
    for dependency in dependencies:
        if substring and substring in dependency:
            continue
        result[package].append(dependency)
        if dependency not in visited:
            visited.add(dependency)
            queue.append(dependency)
    visit_queue(queue, visited, result, adjacency, substring, budget - 1)


def breadth_first(root, adjacency, substring=""):
    """Обойти граф по уровням с ограниченной глубиной стека."""
    queue = deque([root])
    visited = {root}
    result = {}
    while queue:
        visit_queue(queue, visited, result, adjacency, substring, BFS_BATCH)
    return result

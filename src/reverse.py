"""Поиск прямых и транзитивных обратных зависимостей."""

from graph import breadth_first


def reverse_edges(adjacency):
    """Построить список пакетов, ссылающихся на каждую вершину."""
    reversed_graph = {name: [] for name in adjacency}
    for package, dependencies in adjacency.items():
        for dependency in dict.fromkeys(dependencies):
            reversed_graph.setdefault(dependency, []).append(package)
    return reversed_graph


def reverse_dependencies(root, adjacency, substring):
    """Вернуть прямых потребителей и всех потребителей в порядке BFS."""
    graph = breadth_first(root, reverse_edges(adjacency), substring)
    direct = [name for name in graph[root] if name != root]
    all_dependents = [name for name in graph if name != root]
    return direct, all_dependents

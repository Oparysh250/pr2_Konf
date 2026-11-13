"""Генерация PlantUML, рендеринг SVG и открытие в браузере."""

import html
import os
import shutil
import subprocess
import webbrowser


RENDER_TIMEOUT = 60


def plantuml_source(graph, root):
    """Сформировать диаграмму с нейтральными идентификаторами вершин."""
    ids = {name: f"p{index}" for index, name in enumerate(graph)}
    lines = [
        "@startuml", "left to right direction", "skinparam shadowing false",
    ]
    for name, node in ids.items():
        label = html.escape(name, quote=True).replace("\n", " ")
        color = " #DCEEFF" if name == root else ""
        lines.append(f'rectangle "{label}" as {node}{color}')
    for name, dependencies in graph.items():
        lines.extend(f"{ids[name]} --> {ids[dep]}" for dep in dependencies)
    return "\n".join(lines + ["@enduml", ""])


def render_command():
    """Найти установленный PlantUML или использовать JAR из окружения."""
    jar = os.environ.get("PLANTUML_JAR")
    if jar:
        return ["java", "-Djava.awt.headless=true", "-jar", jar]
    binary = shutil.which("plantuml")
    if not binary:
        raise ValueError("Установите plantuml или задайте PLANTUML_JAR")
    return [binary]


def render_svg(source, image):
    """Отрисовать исходник в SVG через локальный PlantUML."""
    command = render_command() + ["-charset", "UTF-8", "-tsvg", "-pipe"]
    try:
        result = subprocess.run(command, input=source.read_bytes(),
                                capture_output=True, check=True,
                                timeout=RENDER_TIMEOUT)
    except FileNotFoundError as error:
        raise ValueError("Не найдена Java или команда PlantUML") from error
    except subprocess.TimeoutExpired as error:
        raise ValueError("PlantUML не завершился за 60 секунд") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode(errors="replace").strip()
        raise ValueError(f"Ошибка PlantUML: {detail}") from error
    if b"<svg" not in result.stdout:
        raise ValueError("PlantUML не вернул SVG")
    image.write_bytes(result.stdout)


def open_image(image):
    """Открыть локальный файл изображения в браузере."""
    try:
        return webbrowser.open(image.resolve().as_uri(), new=2)
    except (OSError, webbrowser.Error):
        return False

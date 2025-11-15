depvis — Dependency Visualizer (minimal prototype)
================================================

Коротко:
- Проект реализует CLI-инструмент для парсинга XML-конфигурации, извлечения
  зависимостей пакетов (в тестовом режиме — из файла; для реального PyPI — через JSON API),
  построения графа зависимостей (BFS), вывода обратных зависимостей, ASCII-дерева
  и Graphviz DOT-описания.

Запуск:
- Примеры:
    python -m depvis --config config_example.xml
    python -m depvis --config config_example.xml --show-direct
    python -m depvis --config config_example.xml --show-reverse

Структура:
- depvis/__main__.py  — CLI и основной сценарий
- depvis/config.py    — чтение и валидация XML-конфига
- depvis/repo_fetch.py — получение зависимостей (PyPI JSON API + тестовый файл)
- depvis/graph.py     — построение графа, детекция циклов, ASCII-дерево, Graphviz DOT
- depvis/utils.py     — вспомогательные утилиты

Примечания:
- Для реального PyPI нужно в конфиге указать repository_url https://pypi.org/pypi
  и test_repo_mode=false, а package_name/package_version соответствуют реальному пакету.
- Инструмент не использует pip или сторонние библиотеки для получения зависимостей.

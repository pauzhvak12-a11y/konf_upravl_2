# Entry point for the depvis package.
# Run with: python -m depvis --config config_example.xml
from .config import read_config, ConfigError
from .repo_fetch import RepoFetchError
from .graph import DepGraph, GraphError
from .utils import eprint
import argparse, sys

def print_kv(config):
    d = {
        'package_name': config.package_name,
        'repository_url': config.repository_url,
        'test_repo_mode': config.test_repo_mode,
        'package_version': config.package_version,
        'ascii_tree_output': config.ascii_tree_output,
        'max_depth': config.max_depth,
        'timeout_seconds': config.timeout_seconds
    }
    print("Параметры конфигурации (ключ = значение):")
    for k,v in d.items():
        print(f"{k} = {v}")

def main(argv=None):
    parser = argparse.ArgumentParser(description="depvis — визуализация графа зависимостей (стандартная библиотека)")
    parser.add_argument('-c','--config', default='config_example.xml', help='путь к XML конфигу')
    parser.add_argument('--show-direct', action='store_true', help='только вывести прямые зависимости указанного пакета (этап 2)')
    parser.add_argument('--show-reverse', action='store_true', help='вывести обратные зависимости для пакета (этап 4)')
    args = parser.parse_args(argv)

    try:
        cfg = read_config(args.config)
    except ConfigError as e:
        eprint(f"Ошибка конфигурации: {e}")
        sys.exit(2)

    # Этап 1: вывести все параметры
    print_kv(cfg)

    graph = DepGraph(cfg)
    if cfg.test_repo_mode:
        try:
            graph.load_test_repo(cfg.repository_url)
        except RepoFetchError as e:
            eprint(f"Ошибка загрузки тестового репозитория: {e}")
            sys.exit(3)

    # Этап 2: вывести прямые зависимости
    try:
        direct = graph.get_direct_deps(cfg.package_name)
    except RepoFetchError as e:
        eprint(f"Ошибка получения прямых зависимостей: {e}")
        sys.exit(4)

    if args.show_direct:
        print(f"\nПрямые зависимости пакета {cfg.package_name}=={cfg.package_version} :")
        if direct:
            for d in direct:
                print(f" - {d}")
        else:
            print(" (нет прямых зависимостей)")
        # пока останавливаемся (этап 2)
        return

    # Этап 3: построить граф (BFS с рекурсией)
    try:
        graph.build_graph_bfs_recursive(cfg.package_name)
    except GraphError as e:
        eprint(f"Ошибка построения графа: {e}")
        sys.exit(5)

    # показать циклы, если есть
    cycles = graph.detect_cycles()
    if cycles:
        print("\nОбнаружены циклы зависимостей:")
        for c in cycles:
            print(" -> ".join(c))
    else:
        print("\nЦиклических зависимостей не обнаружено.")

    # Этап 4: обратные зависимости (если запрошено)
    if args.show_reverse:
        inv = graph.inverse_graph()
        target = cfg.package_name
        rev = inv.get(target, [])
        print(f"\nОбратные зависимости (кто зависит от {target}):")
        if rev:
            for r in rev:
                print(f" - {r}")
        else:
            print(" (никто не зависит)")

    # Этап 5: визуализация
    print("\nGraphviz DOT представление:")
    dot = graph.to_graphviz_dot()
    print(dot)

    if cfg.ascii_tree_output:
        print("\nASCII-дерево зависимостей:")
        print(graph.ascii_tree(cfg.package_name, max_levels=cfg.max_depth))


if __name__ == '__main__':
    main()

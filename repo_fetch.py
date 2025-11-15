import json
import urllib.request
import urllib.error
from typing import List, Dict

class RepoFetchError(Exception):
    pass

def fetch_direct_dependencies_from_pypi(package: str, version: str, base_url: str, timeout=10) -> List[str]:
    """

    Ожидает base_url вида https://pypi.org/pypi (без завершающего слеша)
    и делает запрос {base_url}/{package}/{version}/json
    Из JSON извлекает список зависимостей из info.requires_dist (PEP 345 style entries)
    Возвращает список строк зависимостей в виде 'package_name (specifier?)' — но парсим только имена.
    """
    if base_url.endswith('/'):
        base_url = base_url[:-1]
    url = f"{base_url}/{package}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            if getattr(resp, 'status', None) not in (None, 200):
                # Some urllib responses expose status, some don't; handle generically.
                status = getattr(resp, 'status', None)
                raise RepoFetchError(f"HTTP {status} при запросе {url}")
            raw = resp.read().decode('utf-8')
            data = json.loads(raw)
    except urllib.error.HTTPError as e:
        raise RepoFetchError(f"HTTPError: {e.code} {e.reason} for {url}")
    except urllib.error.URLError as e:
        raise RepoFetchError(f"URLError: {e.reason} for {url}")
    except RepoFetchError:
        raise
    except Exception as e:
        raise RepoFetchError(f"Ошибка при получении метаданных: {e}")

    info = data.get('info', {})
    requires = info.get('requires_dist') or []
    # requires_dist items look like: "urllib3 (<1.27,>=1.21.1)" or "certifi ; python_version >= '3.6'"
    deps = []
    for r in requires:
        # отрезаем часть после ';' (environment markers) и берем первый токен в описании
        r_main = r.split(';', 1)[0].strip()
        if not r_main:
            continue
        # первый токен — имя (иногда имя содержит '-' vs '_', оставляем как есть)
        name = r_main.split()[0]
        # иногда name имеет extras: 'package[extra]' — отбросим [...]:
        if '[' in name:
            name = name.split('[', 1)[0]
        deps.append(name)
    return deps

def fetch_dependencies_test_repo(path: str) -> Dict[str, List[str]]:
    """

    Ожидает файл, где каждая строка:
      PACKAGE: DEP1 DEP2 DEP3
    Пакеты именуются заглавными латинскими буквами (по условию этапа 3)
    Возвращает словарь {package: [deps...]}
    """
    d = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' not in line:
                    raise RepoFetchError(f"Неправильный формат на строке {lineno}: '{line}'")
                left, right = line.split(':', 1)
                pkg = left.strip()
                deps = [p for p in right.strip().split() if p]
                d[pkg] = deps
    except FileNotFoundError:
        raise RepoFetchError(f"Файл тестового репозитория не найден: {path}")
    except Exception as e:
        raise RepoFetchError(f"Ошибка при чтении тестового репозитория: {e}")
    return d

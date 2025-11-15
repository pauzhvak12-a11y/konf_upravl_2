import xml.etree.ElementTree as ET

class ConfigError(Exception):
    pass

class Config:
    def __init__(self, package_name, repository_url, test_repo_mode,
                 package_version, ascii_tree_output, max_depth=10, timeout_seconds=10):
        self.package_name = package_name
        self.repository_url = repository_url
        self.test_repo_mode = test_repo_mode
        self.package_version = package_version
        self.ascii_tree_output = ascii_tree_output
        self.max_depth = max_depth
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def parse_bool(text, default=False):
        if text is None:
            return default
        t = text.strip().lower()
        if t in ('1', 'true', 'yes', 'on'):
            return True
        if t in ('0', 'false', 'no', 'off'):
            return False
        raise ConfigError(f"Invalid boolean value: {text}")

def read_config(path):
    try:
        tree = ET.parse(path)
    except Exception as e:
        raise ConfigError(f"Не могу прочитать XML-файл: {e}")

    root = tree.getroot()
    def get(tag):
        node = root.find(tag)
        return node.text.strip() if (node is not None and node.text is not None) else None

    package_name = get('package_name')
    if not package_name:
        raise ConfigError("Отсутствует обязательный элемент <package_name>")

    repository_url = get('repository_url')
    if not repository_url:
        raise ConfigError("Отсутствует обязательный элемент <repository_url>")

    test_repo_mode = Config.parse_bool(get('test_repo_mode'), default=False)
    package_version = get('package_version')
    if not package_version:
        raise ConfigError("Отсутствует обязательный элемент <package_version>")

    ascii_tree_output = Config.parse_bool(get('ascii_tree_output'), default=False)

    max_depth = get('max_depth')
    if max_depth:
        try:
            max_depth = int(max_depth)
            if max_depth < 1:
                raise ValueError()
        except ValueError:
            raise ConfigError("max_depth должен быть положительным целым числом")
    else:
        max_depth = 10

    timeout_seconds = get('timeout_seconds')
    if timeout_seconds:
        try:
            timeout_seconds = int(timeout_seconds)
            if timeout_seconds < 1:
                raise ValueError()
        except ValueError:
            raise ConfigError("timeout_seconds должен быть положительным целым числом")
    else:
        timeout_seconds = 10

    return Config(package_name, repository_url, test_repo_mode,
                  package_version, ascii_tree_output, max_depth, timeout_seconds)

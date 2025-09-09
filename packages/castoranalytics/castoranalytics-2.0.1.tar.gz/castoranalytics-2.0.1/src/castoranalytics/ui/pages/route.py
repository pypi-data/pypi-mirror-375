import re


class Route:
    def __init__(self, page, path_pattern):
        self._page = page
        self._path_pattern = path_pattern
        self._param_names = []
        self._regex = self.compile_pattern(path_pattern)

    def get_page(self):
        return self._page

    def compile_pattern(self, path_pattern):
        pattern = re.sub(r":(\w+)", r"(?P<\1>[^/]+)", path_pattern)
        self._param_names = re.findall(r":(\w+)", path_pattern)
        return re.compile(f"^{pattern}$")

    def match(self, path):
        match = self._regex.match(path)
        if match:
            return match.groupdict()
        return None
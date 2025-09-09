from PySide6.QtWidgets import QStackedWidget

from castoranalytics.ui.pages.route import Route


class Router(QStackedWidget):
    def __init__(self):
        super(Router, self).__init__()
        self._pages = {}
        self._routes = []
        self._prev_path = None
        self._curr_path = None

    def add_page(self, page, path_pattern):
        route = Route(page, path_pattern)
        self._routes.append(route)
        page.set_router(self)
        self.addWidget(page)

    def back(self):
        self.navigate(self._prev_path)

    def navigate(self, path):
        for route in self._routes:
            params = route.match(path)
            if params is not None:
                if path != self._curr_path:
                    self._prev_path = self._curr_path
                    self._curr_path = path
                    self.setCurrentWidget(route.get_page())
                    route.get_page().on_navigate(params)
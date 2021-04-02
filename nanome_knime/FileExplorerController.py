import tempfile
from .FileExplorer import FileExplorer


class FileExplorerController:
    def __init__(self, plugin):
        self.plugin = plugin
        self.explorers = {}

    def get_explorer(self, name, mode, on_close):
        if name in self.explorers:
            self.explorers[name].open_menu()
            return

        self.plugin.menu_count = index = self.plugin.menu_count + 1
        self.explorers[name] = FileExplorer(self.plugin, mode, on_close, index)
        self.explorers[name].open_menu(name, mode)

    def update(self):
        for name in self.explorers:
            self.explorers[name].update()

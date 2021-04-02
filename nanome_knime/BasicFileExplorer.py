from nanome._internal._structure._io._mmcif.structure import structure
import nanome
import os
import tempfile
import ntpath
from nanome.api.ui import Menu
from nanome.api.ui import LayoutNode
from nanome.util.logs import Logs
from nanome.util.file import FileError
from .FileExplorer import FileExplorer

NAME = "Basic File Explorer"
DESCRIPTION = "Allows you to browse your files"
CATEGORY = ""
HAS_ADVANCED_OPTIONS = False


class BasicFileExplorer(nanome.PluginInstance):
    def start(self):
        self.FileExplorer = FileExplorer("File Explorer")
        self.FileExplorer.on_up_pressed = self.on_up_pressed
        self.FileExplorer.on_directory_pressed = self.on_directory_pressed
        self.FileExplorer.on_select_pressed = self.on_select_pressed
        self.FileExplorer.on_quick_access = self.on_quick_access
        self.FileExplorer.set_quick_access_list([])

        self.temp_dir = tempfile.mkdtemp()
        self.quick_locations = {
            "Desktop": "~/Desktop",
            "Documents": "~/Documents",
            "Downloads": "~/Downloads",
            "Pictures": "~/Pictures",
            "Workspaces": "~/Documents/Nanome/Sessions",
            "Recordings": "~/Documents/Nanome/Recordings",
        }

    def on_run(self):
        self.files.cd(".", self.directory_changed)
        self.__setup_quick_access()
        self.FileExplorer.open(self)

    def update(self):
        self.FileExplorer.update(self)

    def on_up_pressed(self):
        self.files.cd("..", self.directory_changed)

    def on_directory_pressed(self, entry):
        self.files.cd(entry.name, self.directory_changed)

    def on_select_pressed(self, entry):
        self.files.get(entry.name, os.path.join(self.temp_dir, str(
            self.__path_leaf(entry.name))), self.file_fetched)

    def file_fetched(self, error, path):
        if error == nanome.util.FileError.no_error:
            Logs.debug("loaded", path)
            self.send_files_to_load(path)
        else:
            Logs.debug(error)

    def on_quick_access(self, name):
        path = self.quick_locations[name]
        self.files.cd(path, self.directory_changed)

    def directory_changed(self, *args):
        if FileError.no_error == args[0]:
            self.files.pwd(self.FileExplorer.set_working_directory)
            self.files.ls(".", self.FileExplorer.set_directory_contents)
        else:
            Logs.error(args[0])

    def __path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def __setup_quick_access(self):
        location_count = len(self.quick_locations)
        self.__ql_responses = 0
        for location in self.quick_locations.items():
            def filter_result(error, _):
                if (error != nanome.util.FileError.no_error):
                    del self.quick_locations[location[0]]
                self.__ql_responses += 1
                if self.__ql_responses == location_count:
                    self.FileExplorer.set_quick_access_list(
                        self.quick_locations.keys())
            self.files.ls(location[1], filter_result)


nanome.Plugin.setup(NAME, DESCRIPTION, CATEGORY,
                    HAS_ADVANCED_OPTIONS, BasicFileExplorer)

import os
from os.path import splitext, basename, dirname, join as pathjoin, split as pathsplit
import tempfile

from nanome.api.ui import LayoutNode
from nanome.util.file import FileMeta, FileError
from nanome.util.logs import Logs
import nanome
menu_to_json = nanome.ui.Menu.io.from_json
ln_to_json = nanome.api.ui.LayoutNode.io.from_json

ASSETS_PATH = pathjoin(dirname(__file__), 'assets')
ICONS_PATH = pathjoin(ASSETS_PATH, 'icons')
MENUS_PATH = pathjoin(ASSETS_PATH, 'menus')
COMPONENTS_PATH = pathjoin(ASSETS_PATH, 'components')


class Icon():
    up = pathjoin(ICONS_PATH, "Up.png")
    folder = pathjoin(ICONS_PATH, "Folder.png")
    image = pathjoin(ICONS_PATH, "Image.png")
    pdf = pathjoin(ICONS_PATH, "PDF.png")
    structure = pathjoin(ICONS_PATH, "Structures.png")
    workspace = pathjoin(ICONS_PATH, "Workspace.png")
    unknown = pathjoin(ICONS_PATH, "Unknown.png")


class FileExplorer():
    def __init__(self, plugin, mode, on_close, index):
        self.plugin = plugin
        self.mode = mode
        self.item_prefab = ln_to_json(pathjoin(COMPONENTS_PATH, 'File.json'))
        self.menu = menu_to_json(pathjoin(MENUS_PATH, 'FileExplorer.json'))
        self.menu.index = index
        self.menu.register_closed_callback(self.__on_close)
        self.close = on_close

        # Setup quick access panel
        find_node = self.menu.root.find_node
        self.quick_access_prefab = find_node("QuickAccess1", True)
        self.file_source_node = self.quick_access_prefab.parent
        self.file_source_node.remove_child(self.quick_access_prefab)

        self.grid = find_node("Grid", True).get_content()
        self.path = ''
        self.path_text = find_node("BreadCrumbText", True).get_content()
        self.select_button = find_node("SelectButton", True).get_content()
        self.select_button.register_pressed_callback(self.__select_pressed)
        self.up_button = find_node("Up", True).get_content()
        self.up_button.icon.value.set_all(Icon.up)
        self.up_button.register_pressed_callback(self.__up_pressed)
        self.selected_button = None
        self.temp_dir = tempfile.TemporaryDirectory(dir=pathjoin('/', 'tmp'))

        self.dirty_content = []
        self.dirty_nodes = []
        self.running = False

        self.set_quick_access_list([])
        self.quick_locations = {
            "/tmp": "/tmp",
            "Plugin": f"{dirname(__file__)}",
            "/root": "/root",
            "/bin": "/bin",
        }
        self.__setup_quick_access()

    def open_menu(self, var_name=None, explorer_type=None):
        self.running = True
        self.dirty_content = []
        self.dirty_nodes = []

        self.directory_changed(FileError.no_error)
        self.menu.title = f'Select {var_name}'
        self.menu.enabled = True
        self.plugin.update_menu(self.menu)

    def on_up_pressed(self):
        self.cd("..", self.directory_changed)

    def on_directory_pressed(self, entry):
        self.cd(entry.name, self.directory_changed)

    def on_select_pressed(self, entry):
        path = pathjoin(self.temp_dir.name, str(self.__path_leaf(entry.name)))
        self.get(entry.name, self.file_fetched)

    def on_quick_access(self, name):
        self.on_directory_pressed(MemoryObject(name=name))

    def directory_changed(self, *args):
        if FileError.no_error == args[0]:
            self.pwd(
                self.set_working_directory)
            self.ls(
                ".", self.set_directory_contents)
        else:
            Logs.error(args[0])

    def cd(self, path, callback):
        if self.mode == 'Host File':
            self.plugin.files.cd(path, callback)
        elif self.mode == 'Plugin File':
            try:
                os.chdir(path)
                err = FileError.no_error
            except:
                err = FileError.invalid_path
            callback(err, None)

    def get(self, arg, callback):
        if self.mode == 'Host File':
            self.plugin.files.get(arg, callback)
        elif self.mode == 'Plugin File':
            file_path = pathjoin(os.getcwd(), arg)
            file = ''
            with open(file_path, 'r+') as f:
                file = f.read()
            callback(FileError.no_error, file_path, file)

    def pwd(self, callback):
        if self.mode == 'Host File':
            self.plugin.files.pwd(arg, callback)
        elif self.mode == 'Plugin File':
            callback(FileError.no_error, os.getcwd())

    def ls(self, arg, callback):
        if self.mode == 'Host File':
            self.plugin.files.ls(arg, callback)
        elif self.mode == 'Plugin File':
            metas = []
            try:
                with os.scandir(arg) as it:
                    for entry in it:
                        meta = FileMeta()
                        meta.name = entry.name
                        if entry.is_file():
                            meta.size = entry.stat().st_size
                        else:
                            meta.is_directory = True
                        metas.append(meta)
                    err = FileError.no_error
            except:
                err = FileError.invalid_path
            callback(err, metas)

    def file_fetched(self, error, path, content):
        if error != nanome.util.FileError.no_error:
            Logs.debug(error)
            return

        Logs.debug("loaded", path)
        if self.mode == 'Host File':
            self.send_files_to_load(path)
        elif self.mode == 'Plugin File':
            self.path = path
            self.menu.enabled = False
            self.plugin.update_menu(self.menu)
            self.__on_close(self.menu)

    def update(self):
        if (self.running):
            if len(self.dirty_content) > 0:
                self.plugin.update_content(self.dirty_content)
                self.dirty_content = []
            if len(self.dirty_nodes) > 0:
                self.plugin.update_node(self.dirty_nodes)
                self.dirty_nodes = []

    def set_quick_access_list(self, names):
        padding = self.file_source_node.find_node("Padding", True)
        self.file_source_node.clear_children()
        for name in names:
            new_node = self.quick_access_prefab.clone()
            button = new_node.get_content()
            button.name = name
            button.text.value.set_all(name)
            button.register_pressed_callback(self.__quick_access_pressed)
            self.file_source_node.add_child(new_node)
        self.file_source_node.add_child(padding)
        self.dirty_nodes.append(self.file_source_node)

    def set_working_directory(self, error, path):
        self.path_text.text_value = path
        self.dirty_content.append(self.path_text)

    def set_directory_contents(self, error, files):
        if error != nanome.util.FileError.no_error:  # If API couldn't access directory, display error
            nanome.util.Logs.error("Directory request error:", str(error))
            return
        self.grid.items = []
        for file in files:
            item = self.__create_file_rep(file)
            if item != None:
                self.grid.items.append(item)
        self.dirty_content.append(self.grid)

    def __on_close(self, menu):
        self.running = False
        self.close(self.path)

    def __quick_access_pressed(self, button):
        self.on_quick_access(button.name)

    def __up_pressed(self, button):
        self.on_up_pressed()

    def __select_pressed(self, button):
        self.on_select_pressed(self.selected_button.entry)

    def __entry_pressed(self, button):
        # deselecting a node
        if self.selected_button == button:
            self.selected_button = None
            button.selected = False
            self.dirty_content.append(button)
            self.select_button.unusable = True
            self.dirty_content.append(self.select_button)
        # selecting a node
        else:
            # deselecting the old node
            if self.selected_button is not None:
                self.selected_button.selected = False
                self.dirty_content.append(self.selected_button)
            else:
                self.select_button.unusable = False
                self.dirty_content.append(self.select_button)
            button.selected = True
            self.dirty_content.append(button)
            self.selected_button = button

    def __directory_pressed(self, button):
        self.on_directory_pressed(button.entry)

    def __get_prefab_parts(self, prefab):
        selection_button = prefab.find_node("Selection", True).get_content()
        icon = prefab.find_node("Icon", True).get_content()
        text = prefab.find_node("Name", True).get_content()

        favorite_node = prefab.find_node("Favorite", True)
        favorite_button = favorite_node.get_content()

        date_and_size_node = prefab.find_node("DateAndSize", True)
        date = prefab.find_node("Date", True).get_content()
        size = prefab.find_node("Size", True).get_content()
        return selection_button, icon, text, favorite_node, favorite_button, date_and_size_node, date, size

    def __create_file_rep(self, entry):
        extension = splitext(entry.name)[1].lower()
        image = self.__get_icon(extension)
        if (image == None):
            return None

        item = self.item_prefab.clone()
        selection_button, icon, text, favorite_node, favorite_button, date_and_size_node, date, size = self.__get_prefab_parts(
            item)

        selection_button.entry = entry

        icon.file_path = image
        text.text_value = self.__format_file_name(entry.name)

        if entry.is_directory:
            selection_button.register_pressed_callback(
                self.__directory_pressed)
            favorite_node.enabled = False  # Disabling favorite behaviour for now
            date_and_size_node.enabled = False
        else:
            selection_button.register_pressed_callback(self.__entry_pressed)
            favorite_node.enabled = False
            date_and_size_node.enabled = True
            date.text_value = entry.date_modified
            size.text_value = self.__format_size(entry.size)
        return item

    def __format_file_name(self, name):
        name = self.__path_leaf(name)
        if len(name) > 30:
            return "..." + name[-27:]
        return name

    def __format_size(self, size):
        if (size < 1000):
            return str(int(size)) + "B"
        size = size/1000
        if (size < 1000):
            return str(int(size)) + "KB"
        size = size/1000
        if (size < 1000):
            return str(int(size)) + "MB"
        size = size/1000
        if (size < 1000):
            return str(int(size)) + "GB"

    def __path_leaf(self, path):
        head, tail = pathsplit(path)
        return tail or basename(head)

    def __setup_quick_access(self):
        location_count = len(self.quick_locations)
        self.__ql_responses = 0
        for location in self.quick_locations.copy().items():
            def filter_result(error, _):
                if (error != nanome.util.FileError.no_error):
                    del self.quick_locations[location[0]]
                self.__ql_responses += 1
                if self.__ql_responses == location_count:
                    self.set_quick_access_list(
                        self.quick_locations.keys())
            self.ls(location[1], filter_result)

    def __get_icon(self, extension):
        if extension == "":
            return Icon.folder
        elif extension == ".pdf":
            return Icon.pdf
        elif extension == ".jpeg" or extension == ".jpg" or extension == ".png":
            return Icon.image
        elif extension == ".nanome":
            return Icon.workspace
# region structure formats
        elif extension == ".pdb" or extension == ".pdb1" or extension == ".pdb2" or extension == ".pdb3" or extension == ".pdb4" or extension == ".pdb5":
            return Icon.structure
        elif extension == ".sd" or extension == ".sdf" or extension == ".mol" or extension == ".mol2":
            return Icon.structure
        elif extension == ".cif" or extension == ".mmcif" or extension == ".pdbx":
            return Icon.structure
        elif extension == ".smiles" or extension == ".smi":
            return Icon.structure
        elif extension == ".xyz" or extension == ".pqr" or extension == ".gro":
            return Icon.structure
        elif extension == ".moe" or extension == ".mae" or extension == ".pse":
            return Icon.structure
# endregion
# region misc formats
        elif extension == ".dcd" or extension == ".xtc" or extension == ".trr" or extension == ".psf":
            return Icon.structure
        elif extension == ".ccp4" or extension == ".dsn6":
            return Icon.structure
        elif extension == ".dx" or extension == ".map":
            return Icon.structure
        else:
            return Icon.unknown
# endregion


class MemoryObject():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

import nanome
from os.path import basename, dirname, join as pathjoin
from pathlib import Path

ASSETS_PATH = pathjoin(dirname(__file__), 'assets')
MENU_PATH = pathjoin(ASSETS_PATH, 'menus', 'workflows.json')


class Workspace():
    def __init__(self, plugin, path):
        self.menu = nanome.ui.Menu.io.from_json(MENU_PATH)
        self.path = path
        self.plugin = plugin
        self.workflows = {}
        self.lst_workflow = self.menu.root.find_node(
            'Workflow List').get_content()

        self.draw_menu()

    def draw_menu(self):
        self.refresh_workflows()
        for name, path in self.workflows.items():
            ln = self.workflow_item(name, path)
            self.lst_workflow.items.append(ln)

    def open_menu(self):
        self.menu.enabled = True
        self.plugin.update_menu(self.menu)

    def workflow_paths(self, index):
        if not len(self.workflows.keys()):
            self.refresh_workflows()
        return list(self.workflows.values())[index]

    def refresh_workflows(self):
        self.workflows.clear()
        for path in Path(self.path).rglob('*.knime'):
            self.workflows[basename(dirname(path))] = dirname(path)

    def workflow_item(self, name, path):
        ln = nanome.ui.LayoutNode()
        btn = ln.add_new_button(name)
        btn.path = path

        def open_workflow(btn):
            self.plugin.workflow.path = btn.path
            self.menu.enabled = False
            self.plugin.workflow.open_menu()
        btn.register_pressed_callback(open_workflow)
        return ln

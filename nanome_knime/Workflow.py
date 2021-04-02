from functools import partial
from os.path import basename, dirname, join as pathjoin
from xmltodict import parse as xmlparse

import nanome
from nanome.util import Logs
ddi = nanome.ui.DropdownItem

ASSETS_PATH = pathjoin(dirname(__file__), 'assets')
MENU_PATH = pathjoin(ASSETS_PATH, 'menus', 'workflow.json')
PDBOPTIONS = nanome.api.structure.Complex.io.PDBSaveOptions()
PDBOPTIONS.write_bonds = True


class Workflow:
    def __init__(self, plugin, path):
        self.plugin = plugin
        self.path = path
        self.menu = nanome.ui.Menu.io.from_json(MENU_PATH)
        root = self.menu.root
        self.lst_variables = root.find_node('Variables').get_content()
        self.prefab = root.find_node('Variable')  # Label, Value, Type
        self.variables = self.get_variables()

    def get_args(self):
        return self.variables

    def get_name(self):
        return basename(self.path)

    def get_variables(self):
        variables = {}
        knime_file = pathjoin(self.path, 'workflow.knime')
        xml = None
        with open(knime_file, 'r') as f:
            xml = xmlparse(f.read())
        configs = xml['config']['config']
        for index in range(len(configs)):
            config = configs[index]
            if config['@key'] == 'workflow_variables':
                for var in config['config']:
                    vname, vclass, vvalue = [attr['@value']
                                             for attr in var['entry']]
                    variables[vname] = (vvalue, vclass)
        return variables

    def draw_menu(self):
        self.menu.title = self.get_name()
        if not self.variables:
            self.get_variables()
        for varname in self.variables:
            value, var_type = self.variables[varname]
            prefab = self.var_prefab(varname, value, var_type)
            self.lst_variables.items.append(prefab)
        self.plugin.update_content(self.lst_variables)

    def open_menu(self):
        if not self.lst_variables.items and self.variables:
            self.draw_menu()
        self.menu.enabled = True
        self.plugin.update_menu(self.menu)

    def save_complex(self, complex_id, callback):
        def save(complexes):
            # order matches workflow's inputs
            paths = []
            for complex in complexes:
                paths.append(
                    pathjoin(self.plugin.inputs, f'{complex.name}.pdb'))
                complex.io.to_pdb(paths[-1], PDBOPTIONS)
                complex.locked = True
            self.update_structures_shallow([complex_id])
            callback(paths)

        self.plugin.request_complexes([complex_id], save)

    def var_prefab(self, name, value, var_type):
        prefab = self.prefab.clone()
        ln_label, ln_value, ln_type = [c for c in prefab.get_children()]
        ln_label.add_new_label().text_value = name
        inp = ln_value.add_new_text_input()
        inp.input_text, inp.text_size = value, 0.3

        dd = ln_type.add_new_dropdown()

        def open_file_explorer(var_name, var_type, button=None):
            def set_value(path):
                Logs.debug('setting value...')
                inp = ln_value.add_new_text_input()
                inp.text_size = 0.3
                inp.input_text = path
                self.plugin.update_content(self.lst_variables)

            self.plugin.explorer_controller.get_explorer(
                var_name, var_type, set_value)

        def switch_var_type(dropdown, ddi_var_type):
            if ddi_var_type.name in ['Host File', 'Plugin File']:
                btn = ln_value.add_new_button('Select File')
                explore_files = partial(
                    open_file_explorer, name, ddi_var_type.name)
                explore_files()
                btn.register_pressed_callback(explore_files)
            else:
                dd = ln_value.add_new_dropdown()
                dd.items = [ddi(c.name)
                            for c in self.plugin.shallow_structures]
                # make save_complexes save_complex
                dd.register_item_clicked_callback(self.save_complex)
                self.plugin.update_node(ln_value)

            self.plugin.update_content(self.lst_variables)

        # file explorer button or complex dropdown
        dd.register_item_clicked_callback(switch_var_type)
        dd.items = [
            # ddi('Host File'),
            ddi('Plugin File'),
            ddi('Workspace Complex')
        ]
        ln_type.get_content().items[1].selected = True
        return prefab

import argparse
import nanome
from nanome.util import Logs
import os
from os.path import join as pathjoin
import tempfile
from .FileExplorerController import FileExplorerController as ExplorerController
from .Workspace import Workspace
from .Workflow import Workflow
from .KnimeRunner import KnimeRunner
import shutil
from functools import partial

SDFOPTIONS = nanome.api.structure.Complex.io.SDFSaveOptions()


class KnimePlugin(nanome.PluginInstance):

    def start(self):
        # command line arguments
        self.complex_updated_callbacks = []
        self.explorer_controller = ExplorerController(self)
        self.knime_dir = os.path.join('/', 'app', 'knime')
        self.inputs = tempfile.TemporaryDirectory(dir=os.getcwd())
        self.outputs = tempfile.TemporaryDirectory(dir=os.getcwd())
        workspace_dir, = self._custom_data[0]['workspace_dir']
        self.workspace = Workspace(self, workspace_dir)
        self.workflow = Workflow(self, self.workspace.workflow_paths(0))
        self.runner = KnimeRunner(self)
        self.preferences_path = pathjoin(workspace_dir, 'preferences.epf')
        self.running = False
        self.shallow_structures = []
        self.deep_structures = {}
        self.request_complex_list(self.on_complex_list_received)
        self.menu_count = 0
        self.workspace.open_menu()

        self.workflow.get_variables()

    def on_stop(self):
        self.cleanup()

    def test_ls(self, *args):
        Logs.debug(args)

    def on_complex_list_received(self, complexes):
        self.shallow_structures = []
        for complex in complexes:
            self.shallow_structures.append(complex)
            for complex_callback in self.complex_updated_callbacks:
                complex.register_complex_updated_callback(complex_callback)

    def on_complex_added(self):
        self.request_complex_list(self.on_complex_list_received)

    def on_complex_removed(self):
        self.request_complex_list(self.on_complex_list_received)

    def on_run(self):
        self.workspace.open_menu()

    # This function is called by the KNIME_menu.py class's callback for the
    #   "Run Docking" button - activates knime with the run_knime function in the
    #   KnimeRunner.py script.
    # ##
    def run_workflow(self):
        self.running = True
        self.workspace.disable()
        self.workflow.disable()
        args = self.workflow.get_args()
        self.workflow.save_complexes()
        self.request_list = [protein.index, ligands.index]
        self.request_complexes(self.request_list, self.save_files)

    def get_and_call(self, structure, callback):
        self.request_complexes([structure.index], callback)

    def cleanup(self):
        shutil.rmtree(self.inputs.name, ignore_errors=True)
        shutil.rmtree(self.outputs.name, ignore_errors=True)

    # Called every update tick of the Plugin
    def update(self):
        self.runner.update()
        self.explorer_controller.update()


def main():

    base_arg_dict = {
        '-a': 'connects to a NTS at the specified IP address',
        '--address': 'connects to a NTS at the specified IP address',
        '-p': 'connects to a NTS at the specified port',
        '--port': 'connects to a NTS at the specified port',
        '-k': 'specifies a key file to use to connect to NTS',
        '--keyfile': 'specifies a key file to use to connect to NTS',
        '-n': 'name to display for this plugin in Nanome',
        '--name': 'name to display for this plugin in Nanome',
        '-v': 'enable verbose mode, to display Logs.debug',
        '--verbose': 'enable verbose mode, to display Logs.debug',
        '-r': 'restart plugin automatically if a .py or .json file in current directory changes',
        '--restart': 'restart plugin automatically if a .py or .json file in current directory changes',
        '--auto-reload': 'same as -r',
        '--ignore': 'to use with auto-reload. All paths matching this pattern will be ignored, use commas to specify several. Supports */?/[seq]/[!seq]'}

    parser = argparse.ArgumentParser()

    for arg in base_arg_dict:
        parser.add_argument(arg, nargs='?', help=base_arg_dict[arg])

    parser.add_argument('--workspace_dir', nargs=1,
                        help='enter the path to your knime workspace')
    args = parser.parse_args()
    arg_dict = vars(args)

    plugin = nanome.Plugin('Knime Workspace Viewer',
                           'View and run Knime workflows', 'test', False)
    plugin.set_custom_data(arg_dict)
    plugin.set_plugin_class(KnimePlugin)
    plugin.run('plugins.nanome.ai', 9999)


if __name__ == '__main__':
    main()

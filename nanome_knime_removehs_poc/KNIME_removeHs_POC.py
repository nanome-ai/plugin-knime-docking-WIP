import nanome
from nanome.util import Logs, complex_save_options
import os
import tempfile
from pathlib import PureWindowsPath
import subprocess
from ._KNIMEMenu_POC import KNIMEmenu
from ._KNIMErunner_POC import knime_runner
import sys
import argparse
import shutil
from functools import partial

SDFOPTIONS = nanome.api.structure.Complex.io.SDFSaveOptions()


class KNIME_removeHs_POC(nanome.PluginInstance):

    def start(self):
        # intake command line arguments
        arg_dict = self._custom_data[0]
        self._workflow_dir = arg_dict['wkflw_dir'][0]
        self._grid_dir = arg_dict['grid_dir'][0]
        self._save_location = arg_dict['output_dir'][0]
        self._knime_dir = arg_dict['knime_dir'][0]
        self._preferences_dir = arg_dict['preferences_dir'][0]
        Logs.debug(self._save_location, self._grid_dir,
                   self._workflow_dir, self._knime_dir)

        # instantiate and build knime driver and menu
        self._menu = KNIMEmenu(self)
        self._runner = knime_runner(self)
        self._menu.build_menu()
        # populate menu
        self.request_complex_list(self.on_complex_list_received)
        self._menu.populate_grid_dropdown()
        Logs.debug("I requested the complex list")

        # variables
        self._protein = None
        self._ligands = None
        self._structures = {}
        self._running = False
        self._ran = False

    # callback function for the request_complex_list method - runs
    # the menu's method for updating/populating menu with workspace data

    def refresh_structure_dropdowns(self, updated_complex=None):
        if updated_complex is not None:
            if updated_complex.name != self._structures.get(update_complex.id):
                self.request_complex_list(self.on_complex_list_received)
        else:
            self.request_complex_list(self.on_complex_list_received)

    def on_complex_list_received(self, complexes):
        for complex in complexes:
            complex.register_updated_callback(self.refresh_structure_dropdowns)
            self._structures[complex.id] = complex.name
        self._menu.populate_protein_ligand_dropdown(complexes)

    # Called when a complex is added to the workspace in Nanome
    def on_complex_added(self):
        self.refresh_structure_dropdowns()

    # Called when a complex is removed from the workspace in Nanome
    def on_complex_removed(self):
        self.refresh_structure_dropdowns()

    # does basically nothing, should be removed or made to restart/refresh
    # the plugin.
    def on_run(self):
        # Displays a message in the console
        Logs.message("Connected to a new session!")
        self._menu.enabled = True
        self.update_menu(self.menu)

    def request_refresh(self):
        self._menu._selected_mobile = []
        self._menu._selected_target = None
        self.request_complex_list(self.on_complex_list_received)
        nanome.util.Logs.debug("Complex list requested")

    # This function is called by the KNIME_menu.py class's callback for the
    #   "Run Docking" button - activates knime with the run_knime function in the
    #   _KNIMErunner.py script.
    # ##
    def run_workflow(self):
        self.make_temp_files()
        self._running = True
        self._menu.make_plugin_usable(False)
        ligands = self._menu.get_ligands()
        Logs.debug("\n", ligands)
        protein = self._menu.get_protein()
        Logs.debug(protein, "\n")
        self.request_list = [protein.index, ligands.index]
        Logs.debug("\n ************ \nrequest list:",
                   self.request_list, "\n**************")
        # self.save_files is the callback function, activated when complexes are received
        self.request_complexes(self.request_list, self.save_files)

    # This function is used in _KNIMErunner_POC's _workflow_finished method to
    # "align" modified complexes with source complexes
    # The `align_callback(self)` method in the `_KNIMErunner` class is passed to
    # this method - the `finish_workflow_runner` parameter - which passes it as
    # the callback function for `on_complexes_received`, which is itself a callback function
    # for `self.request_complexes`. Phew.
    def align(self, structure, finish_workflow_runner):

        Logs.debug('\n\n STARTING ALIGN getting updated complex\n*************')

        ligand = self._menu.get_ligands()
        request_list = [ligand.index]

        # Request a deep copy of ligand in order to get updated position + rotation value
        self.request_complexes(self.request_list, partial(
            self.on_complex_received, finish_workflow_runner=finish_workflow_runner))

    # Callback function for when complexes are received
    def on_complex_received(self, complexes, finish_workflow_runner):
        complex = complexes[1]
        self._runner._structure.position = complex.position
        self._runner._structure.rotation = complex.rotation
        self._runner._structure.name = complex.name + " (Docked)"
        self._runner._structure.locked = True

        # toggle visibility of original ligand
        complex.visible = False
        # complex.locked = True
        self.update_structures_shallow([complex])

        finish_workflow_runner()

    def make_temp_files(self):
        # input_name = os.path.join(os.getcwd(), 'nanome_input_temp')
        # output_name = os.path.join(os.getcwd(), 'nanome_output_temp')
        self._input_directory = tempfile.TemporaryDirectory(dir=os.getcwd())
        self._output_directory = tempfile.TemporaryDirectory(dir=os.getcwd())
        self._ligands_input = tempfile.NamedTemporaryFile(
            delete=False, prefix="ligands", suffix=".sdf", dir=self._input_directory.name)
        # self._protein_input = tempfile.NamedTemporaryFile(
        #     delete=False, prefix="protein", suffix=".sdf", dir=self._input_directory.name)

    # Originally written to cleanup multiple TemporaryNamedFiles, leaving structure for now in case this
    # becomes a desired feature down the road
    def cleanup_temp_files(self):
        for file in [self._ligands_input]:
            try:
                os.close(file.fileno())
            except OSError:
                Logs.debug('\nfile already closed')

        shutil.rmtree(self._input_directory.name, ignore_errors=True)
        shutil.rmtree(self._output_directory.name, ignore_errors=True)

    # This method expects only one ligand for now
    def save_files(self, complexes):
        # we expect this order based on the request list defined in run_workflow method
        self._protein, self._ligands = complexes[0], complexes[1]
        self._protein.locked = True
        self._ligands.locked = True
        self.update_structures_shallow([self._protein, self._ligands])
        self._ligands.io.to_sdf(self._ligands_input.name, SDFOPTIONS)
        # self._protein.io.to_sdf(self._protein_input.name, SDFOPTIONS)

        self._runner.run_knime()

    # Called every update tick of the Plugin
    def update(self):
        self._runner.update()


def main():

    base_arg_dict = {
        '-a': 'connects to a NTS at the specified IP address',
        '-p': 'connects to a NTS at the specified port',
        '-k': 'specifies a key file to use to connect to NTS',
        '-n': 'name to display for this plugin in Nanome',
        '-v': 'enable verbose mode, to display Logs.debug',
        '-r': 'restart plugin automatically if a .py or .json file in current directory changes',
        '--auto-reload': 'same as -r',
        '--ignore': 'to use with auto-reload. All paths matching this pattern will be ignored, use commas to specify several. Supports */?/[seq]/[!seq]'}

    parser = argparse.ArgumentParser()

    for arg in base_arg_dict:
        parser.add_argument(arg, nargs='?', help=base_arg_dict[arg])

    parser.add_argument('--wkflw_dir', nargs=1,
                        help='enter the path to the knime worklfow')
    parser.add_argument('--grid_dir', nargs=1,
                        help='enter the path to the docking grid folder')
    parser.add_argument('--output_dir', nargs=1,
                        help='enter the path to the desired output folder, where data generated by the plugin will be written')
    parser.add_argument('--knime_dir', nargs=1,
                        help='enter the path to the host machine\'s knime.exe file')
    parser.add_argument('--preferences_dir', nargs=1,
                        help='enter the path to the desired preferences.epf')
    args = parser.parse_args()
    arg_dict = vars(args)

    plugin = nanome.Plugin('KNIME_removeHs_POC_Windows',
                           'Removes hydrogen atoms using KNIME', 'test', False)
    plugin.set_custom_data(arg_dict)
    plugin.set_plugin_class(KNIME_removeHs_POC)
    plugin.run('plugins.nanome.ai', 9999)


if __name__ == '__main__':
    main()

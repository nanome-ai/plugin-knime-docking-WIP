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

SDFOPTIONS = nanome.api.structure.Complex.io.SDFSaveOptions()


class KNIME_removeHs_POC(nanome.PluginInstance):

    def start(self):
        arg_dict = self._custom_data[0]
        self._workflow_dir = arg_dict['wkflw_dir'][0]
        self._grid_dir = arg_dict['grid_dir'][0]
        self._save_location = arg_dict['output_dir'][0]
        Logs.debug(self._save_location, self._grid_dir, self._workflow_dir)

        
        # self._ligands_output = tempfile.NamedTemporaryFile(delete=False, prefix="ligands", suffix=".sdf", dir=self._output_directory.name)
        # self._protein_output = tempfile.NamedTemporaryFile(delete=False, prefix="protein", suffix=".sdf", dir=self._output_directory.name)
        # self.sdf_test = r"D:\knime-workspace\data\sdf_test\{}"
        # self._input_directory = r"D:\knime-workspace\data\sdf_test"
        # self._output_directory = r"D:\knime-workspace\data\sdf_test"
        # self._ligands_output = r"D:\knime-workspace\data\sdf_test\structure_0.sdf"
        # self._protein_output = r"D:\knime-workspace\data\sdf_test\structure_1.sdf"

        self._menu = KNIMEmenu(self)
        self._runner = knime_runner(self)
        self._menu.build_menu()  # The build_menu method from _KNIMEMenu_POC.py
        self.request_complex_list(self.on_complex_list_received)
        self._menu.populate_grid_dropdown()
        Logs.debug("I requested the complex list")

        self._protein, self._ligands = None, None

        self._running = False
        self._ran = False
        

    def on_complex_list_received(self, complexes):
        self._menu.populate_protein_ligand_dropdown(complexes)
        Logs.debug("I ran the change_complex_list function")

    # Called when a complex is added to the workspace in Nanome
    def on_complex_added(self):
        self.request_complex_list(self.on_complex_list_received)

    # Called when a complex is removed from the workspace in Nanome
    def on_complex_removed(self):
        self.request_complex_list(self.on_complex_list_received)

    def on_run(self):
        # menu = self._menu
        # Displays a message in the console
        Logs.message("Connected to a new session!")
        self._menu.enabled = True
        self.update_menu(self.menu)
        # self.request_workspace(self.on_workspace_received) # Request the entire workspace, in "deep" mode

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
        request_list = [protein.index, ligands.index]
        self.request_complexes(request_list, self.save_files) #self.save_files is the callback function, activated when complexes are received

    def on_stop(self):
        Logs.debug("I STOPPED")

    def make_temp_files(self):
        self._input_directory = tempfile.TemporaryDirectory()
        self._output_directory = tempfile.TemporaryDirectory()
        self._ligands_input = tempfile.NamedTemporaryFile(
            delete=False, prefix="ligands", suffix=".sdf", dir=self._input_directory.name)
        Logs.debug('\nfile descriptor ligand is', self._ligands_input.fileno(), '\n')
        self._protein_input = tempfile.NamedTemporaryFile(
            delete=False, prefix="protein", suffix=".sdf", dir=self._input_directory.name)
        Logs.debug('\nfile descriptor protein is', self._protein_input.fileno(), '\n')

    def cleanup_temp_files(self):
        for file in [self._protein_input, self._ligands_input]:
            try:
                Logs.debug('\nfile descriptor is', file.fileno())
                os.close(file.fileno())
            except OSError:
                Logs.debug('\nfile already closed')
        
        shutil.rmtree(self._input_directory.name, ignore_errors=True)
        shutil.rmtree(self._output_directory.name, ignore_errors= True)

# This method expects only one ligand for now
    def save_files(self, complexes):
        self._protein, self._ligands = complexes[0], complexes[1] # we expect this order based on the request list defined in run_workflow method
        Logs.debug("ligand - positon:", self._ligands.position, "rotation,", self._ligands.rotation)
        Logs.debug("protein - positon:", self._protein.position, "rotation,", self._protein.rotation)
        self._ligands.io.to_sdf(self._ligands_input.name, SDFOPTIONS)
        Logs.debug("Saved ligands SDF", self._ligands_input.name)
        self._protein.io.to_sdf(self._protein_input.name, SDFOPTIONS) 
        Logs.debug("Saved protein SDF", self._protein_input.name)
        Logs.debug("\ncomplexes saved as .pdb files to the destination %s \n" %
                   self._input_directory.name)

        Logs.message("I made it to the run_knime function!")

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
    
    args = parser.parse_args()
    arg_dict = vars(args)

    plugin = nanome.Plugin('KNIME_removeHs_POC_Windows',
                           'Removes hydrogen atoms using KNIME', 'test', False)
    plugin.set_custom_data(arg_dict)
    plugin.set_plugin_class(KNIME_removeHs_POC)
    plugin.run('plugins.nanome.ai', 9999)


    
 

if __name__ == '__main__':
    main()

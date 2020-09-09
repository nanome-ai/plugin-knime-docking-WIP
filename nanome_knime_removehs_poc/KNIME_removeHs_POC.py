import nanome
from nanome.util import Logs, complex_save_options
import os
import tempfile
from pathlib import PureWindowsPath
import subprocess
from ._KNIMEMenu_POC import KNIMEmenu
from ._KNIMErunner_POC import knime_runner

SDFOPTIONS = nanome.api.structure.Complex.io.SDFSaveOptions()

class KNIME_removeHs_POC(nanome.PluginInstance):
        
    def start(self):
        Logs.debug("I started")
        # self._input_directory = tempfile.TemporaryDirectory()
        # self._output_directory = tempfile.TemporaryDirectory()\
        self.sdf_test = r"D:\knime-workspace\data\sdf_test\{}"
        self._input_directory = r"D:\knime-workspace\data\sdf_test"
        self._output_directory = r"D:\knime-workspace\data\sdf_test"
        self._ligands_output = r"D:\knime-workspace\data\sdf_test\structure_0.sdf"
        self._protein_output = r"D:\knime-workspace\data\sdf_test\structure_1.sdf"
        # self._ligands_input = tempfile.NamedTemporaryFile(delete=False, prefix="ligands", suffix=".sdf", dir=self._input_directory.name)
        # self._protein_input = tempfile.NamedTemporaryFile(delete=False, prefix="protein", suffix=".sdf", dir=self._input_directory.name)
        self._menu = KNIMEmenu(self)
        self._runner = knime_runner(self)
        self._menu.build_menu() # The build_menu method from _KNIMEMenu_POC.py
        self.request_complex_list(self.on_complex_list_received)
        self._menu.populate_grid_dropdown()
        Logs.debug("I requested the complex list")
        
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
        Logs.message("Connected to a new session!") # Displays a message in the console
        self._menu.enabled = True
        self.update_menu(self.menu)
        # self.request_workspace(self.on_workspace_received) # Request the entire workspace, in "deep" mode

    def request_refresh(self):
        self._menu._selected_mobile = []
        self._menu._selected_target = None
        self.request_complex_list(self.on_complex_list_received)
        nanome.util.Logs.debug("Complex list requested")

## This function is called by the KNIME_menu.py class's callback for the 
#   "Run Docking" button - activates knime with the run_knime function in the
#   _KNIMErunner.py script.
# ##
    def run_workflow(self):
        ligands = self._menu.get_ligands()
        Logs.debug("\n", ligands)
        protein = self._menu.get_protein()
        Logs.debug(protein, "\n")
        request_list = [protein.index, ligands.index]
        self.request_complexes(request_list, self.save_files)

## This method expects only one ligand for now
    def save_files(self, complexes):
        protein, ligands = complexes[0], complexes[1]
        protein.io.to_sdf(self.sdf_test.format("protein.sdf"), SDFOPTIONS)
        ligands.io.to_sdf(self.sdf_test.format("ligand.sdf"), SDFOPTIONS)
        # Logs.debug("complexes saved as .pdb files to the destination %s" % self._input_directory.name)
        # Logs.debug("\n\n", self._ligands_input.name, self._protein_input.name, "\n\n")
        Logs.message("I made it to the run_knime function!")
        self._runner.run_knime()

    # def on_workspace_received(self, workspace):
    #     count = 0
    #     for complex in workspace.complexes:
    #         save_location = self.input_directory.name + ("/%s.pdb" % complex.name)
    #         complex.io.to_pdb(save_location, PDBOPTIONS)
    #         Logs.message(complex.name, "complex registered")
    #         count += 1
    #     Logs.debug(count, "complexes saved as .pdb files to the destination %s" % save_location)
    #     pass
   
    # Called every update tick of the Plugin
    def update(self):
        self._runner.update()

def main():
    plugin = nanome.Plugin('KNIME_removeHs_POC_Windows', 'Removes hydrogen atoms using KNIME', 'test', False)
    plugin.set_plugin_class(KNIME_removeHs_POC)
    plugin.run('127.0.0.1', 8888)


if __name__ == '__main__':
    main()

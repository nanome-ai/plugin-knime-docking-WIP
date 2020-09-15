import subprocess
from nanome.util import Logs
import nanome
import os
import shutil

class knime_runner():
    def __init__(self, plugin):
        self._plugin = plugin
        self._running = False
        self._structures_written = False
        self._knime_process = None

    def run_knime(self):
        Logs.message("I made it to the knime_runner file!")
        #Logs.message(self._plugin._protein_input.name)
        
        ##VARIABLES FOR KNIME RUN##
        #must enter the path to computer's knime.exe file below#
        knime_exe = r'D:\KNIME\knime.exe' #UPDATE!!
        BATCH = "org.knime.product.KNIME_BATCH_APPLICATION"
        workflowDir = r'-workflowDir="{}"'.format(self._plugin._workflow_dir) 
        preferences = r'-preferences="D:\knime-workspace\preferences.epf"' 
        input_folder = r'-workflow.variable=input_folder,"{}",String'.format(self._plugin._input_directory.name)
        Logs.debug(input_folder)
        output_folder = r'-workflow.variable=output_folder,"{}",String'.format(self._plugin._output_directory.name)
        Logs.debug(output_folder) 
        bashCommand = [knime_exe, "-nosave", "-consoleLog", "-reset", "-nosplash", "-application", BATCH, workflowDir, preferences, input_folder, output_folder]
        # bashCommand = [knime_exe, "-nosave", "-reset", "-nosplash", "-application", batch, workflowDir, preferences, input_folder, output_folder]
        bC = ' '.join(bashCommand)

        
        self._knime_process = subprocess.Popen(bC, shell = True)

    def _check_knime(self):
        return self._knime_process.poll() != None
    
    def _workflow_finished(self):
        self.workflow_results = []
        ligand = True
        for item in os.listdir(self._plugin._output_directory.name):
            Logs.debug(item)
            if item.lower().endswith('.sdf'):
                Logs.debug("we got one boys")
                source = os.path.join(self._plugin._output_directory.name, item)
                destination = os.path.join(self._plugin._save_location, item)
                if self._plugin._save_location:
                    shutil.copyfile(source, destination)
                structure = nanome.structure.Complex.io.from_sdf(path=source)
                Logs.debug("structure - positon:", structure.position, "rotation,", structure.rotation)
                if ligand:
                    structure.position = self._plugin._ligands.position
                    structure.rotation = self._plugin._ligands.rotation
                    self._plugin._ligands.visible = False
                    self._plugin.update_structures_shallow([self._plugin._ligands])
                else:
                    structure.position = self._plugin._protein.position
                    structure.rotation = self._plugin._protein.rotation
                    self._plugin._protein.visible = False
                    self._plugin.update_structures_shallow([self._plugin._protein])
                self.workflow_results.append(structure)
                Logs.debug("structure updated - positon:", structure.position, "rotation,", structure.rotation)
                ligand = False
        self._plugin._running = False

        Logs.debug(len(self.workflow_results))
        self._plugin.add_to_workspace(self.workflow_results)
        self._plugin.cleanup_temp_files()
 
    def update(self):
        if self._knime_process and self._check_knime():
            Logs.debug("The KNIME process has finished")
            self._knime_process = False
            self._workflow_finished()
            self._plugin._menu.set_all_dropdowns_to_none()
        else:
            return
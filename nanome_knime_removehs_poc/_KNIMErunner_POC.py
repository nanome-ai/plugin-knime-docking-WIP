import subprocess
from nanome.util import Logs
import nanome



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
        batch = "org.knime.product.KNIME_BATCH_APPLICATION" #constant
        workflowDir = r'-workflowDir="D:\knime-workspace\KNIME_remove_hydrogens"' #UPDATE!!
        preferences = r'-preferences="D:\knime-workspace\preferences.epf"' 
        input_folder = r'-workflow.variable=input_folder,"{}",String'.format(self._plugin._input_directory)
        Logs.debug(input_folder)
        output_folder = r'-workflow.variable=output_file,"{}",String'.format(self._plugin._output_directory)
        Logs.debug(output_folder) 
        # bashCommand = [knime_exe, "-consoleLog", "-reset", "-nosplash", "-application", batch, workflowDir, preferences, input_folder, output_folder]
        bashCommand = [knime_exe, "-nosave", "-reset", "-nosplash", "-application", batch, workflowDir, preferences, input_folder, output_folder]
        bC = ' '.join(bashCommand)

        
        self._knime_process = subprocess.Popen(bC, shell = True)

    def _check_knime(self):
        return self._knime_process.poll() != None
    
    def _workflow_finished(self):
        ligand_results = nanome.structure.Complex.io.from_sdf(path=self._plugin._ligands_output)
        protein_results = nanome.structure.Complex.io.from_sdf(path=self._plugin._protein_output)
        self._plugin.add_to_workspace([ligand_results, protein_results])

    def update(self):
        if self._knime_process and self._check_knime():
            Logs.debug("The KNIME process has finished")
            self._knime_process = False
            self._workflow_finished()
        else:
            return
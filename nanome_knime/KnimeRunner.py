import subprocess
from nanome.util import Logs
import nanome
from_sdf = nanome.structure.Complex.io.from_sdf
from os import listdir
from os.path import join as pathjoin
import shutil


class KnimeRunner():
    def __init__(self, plugin):
        self.plugin = plugin
        self.running = False
        self.structures_written = False
        self.knime_process = None

    def run_knime(self):
        ## VARIABLES FOR KNIME RUN ##
        # must enter the path to computer's knime executable below
        knime_exe = pathjoin(self.plugin._knime_dir, 'knime')
        input_folder = self.plugin.inputs.name
        output_folder = self.plugin.outputs.name
        batch_arg = "org.knime.product.KNIME_BATCH_APPLICATION"
        grid_dir_arg = f'-workflow.variable=grid_dir,"{self.plugin._grid_dir}",String'
        worflow_dir = pathjoin(self.plugin.workspace__dir, self.plugin.workflow)
        workflowDir_arg = f'-workflowDir="{worflow_dir}"'
        preferences = pathjoin(self.plugin._preferences_dir, 'preferences.epf')
        preferences_arg = f'-preferences="{preferences}"'
        input_folder_arg = f'-workflow.variable=input_folder,"{input_folder}",String'
        output_folder_arg = f'-workflow.variable=output_folder,"{output_folder}",String'
        Logs.debug('input_folder arg:', input_folder_arg)
        Logs.debug('output_folder arg:', output_folder_arg)
        # bashCommand = [knime_exe, "-nosave", "-consoleLog", "-reset", "-nosplash", "-application", BATCH, workflowDir, preferences, input_folder, output_folder]
        bashCommand = [knime_exe, "-nosave", "-reset", "-nosplash", "-application",
                       batch_arg, grid_dir_arg, workflowDir_arg, preferences_arg, input_folder_arg, output_folder_arg]
        bC = ' '.join(bashCommand)

        self.knime_process = subprocess.Popen(bC, shell=True)

    def knime_done(self):
        return self.knime_process and self.knime_process.poll() != None

    def workflow_finished(self):
        self.workflow_results = []
        ligand = True
        for item in listdir(self.plugin.outputs.name):
            if item.lower().endswith('.sdf') and ligand:
                source = pathjoin(self.plugin.outputs.name, item)
                self.structure = from_sdf(path=source)
                if ligand:
                    ligand = False
                    self.plugin.get_and_call(self.structure, self.align_callback)

    def align_callback(self, complexes):
        structure, = complexes
        structure.visible = False
        self.update_structures_shallow([structure])

        self.structure.position = structure.position
        self.structure.rotation = structure.rotation
        self.structure.name = structure.name + " (Output)"
        self.structure.locked = True

        self.workflow_results.append(self.structure)
        self.plugin.add_to_workspace(self.workflow_results)
        self.plugin.running = False

    def update(self):
        if self.knime_done():
            Logs.debug("The KNIME process has finished")
            self.knime_process = None
            self.workflow_finished()
        else:
            return

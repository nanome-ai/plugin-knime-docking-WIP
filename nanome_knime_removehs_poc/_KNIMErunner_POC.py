import subprocess
from nanome.util import Logs
import nanome
from os import listdir
from os.path import join as pathjoin
import shutil


class knime_runner():
    def __init__(self, plugin):
        self._plugin = plugin
        self._running = False
        self._structures_written = False
        self._knime_process = None

    def run_knime(self):
        ## VARIABLES FOR KNIME RUN ##
        # must enter the path to computer's knime executable below
        knime_exe = pathjoin(self._plugin._knime_dir, 'knime')
        input_folder = self._plugin._input_directory.name
        output_folder = self._plugin._output_directory.name
        batch_arg = "org.knime.product.KNIME_BATCH_APPLICATION"
        grid_dir_arg = f'-workflow.variable=grid_dir,"{self._plugin._grid_dir}",String'
        workflowDir_arg = f'-workflowDir="{self._plugin._workflow_dir}"'
        preferences = pathjoin(self._plugin._preferences_dir, 'preferences.epf')
        preferences_arg = f'-preferences="{preferences}"'
        input_folder_arg = f'-workflow.variable=input_folder,"{input_folder}",String'
        output_folder_arg = f'-workflow.variable=output_folder,"{output_folder}",String'
        Logs.debug('input_folder arg:', input_folder_arg)
        Logs.debug('output_folder arg:', output_folder_arg)
        # bashCommand = [knime_exe, "-nosave", "-consoleLog", "-reset", "-nosplash", "-application", BATCH, workflowDir, preferences, input_folder, output_folder]
        bashCommand = [knime_exe, "-nosave", "-reset", "-nosplash", "-application",
                       batch_arg, grid_dir_arg, workflowDir_arg, preferences_arg, input_folder_arg, output_folder_arg]
        bC = ' '.join(bashCommand)

        self._knime_process = subprocess.Popen(bC, shell=True)

    def _check_knime(self):
        return self._knime_process.poll() != None

    """
    This method is called by the plugin's update function once the plugin registers that
    execution of the KNIME workflow has completed. It looks for files ending in .sdf in the
    plugin's temporary output directory. Currently, the plugin is built such that the only
    file in the output directory is the ligand. It loads the ligand into Nanome as a complex.

    The loading process is complicated by the need to align the new, processed or "docked" ligand
    with the original ligand. We need to set the docked ligand's position and rotation equal to
    those of the original ligand at the moment of loading, which requires an asynchronous call to
    the Plugin.request_complexes(complexes, callback) function. Due to the difficulties of
    async actions and i/o, the _workflow_finished function is split into two. The first (_workflow_finished) finds, validates,
    and then loads the file for the docked ligand into Nanome (*not* the workspace) as a Complex object.
    The second function (align_callback) is then passed off to the plugin's align method as a callback. After the plugin's
    methods finish retrieving the necessary data from the Nanome workspace, the align_callback

    """

    def _workflow_finished(self):
        self.workflow_results = []
        ligand = True
        for item in listdir(self._plugin._output_directory.name):
            if item.lower().endswith('.sdf') and ligand:
                source = pathjoin(
                    self._plugin._output_directory.name, item)
                destination = pathjoin(self._plugin._save_location, item)
                if self._plugin._save_location:
                    shutil.copyfile(source, destination)
                self._structure = nanome.structure.Complex.io.from_sdf(
                    path=source)
                Logs.debug("structure - positon:", self._structure.position,
                           "rotation,", self._structure.rotation)
                if ligand:
                    ligand = False
                    self._plugin.align(self._structure, self.align_callback)

    # Originally the second half of the _workflow_fini
    def align_callback(self):
        self.workflow_results.append(self._structure)
        Logs.debug('\nName of complex is: ', self._structure.name)
        Logs.debug("structure updated - positon:",
                   self._structure.position, "rotation,", self._structure.rotation)
        Logs.debug(len(self.workflow_results))
        self._plugin.add_to_workspace(self.workflow_results)
        self._plugin.cleanup_temp_files()
        self._plugin._running = False

    def update(self):
        if self._knime_process and self._check_knime():
            Logs.debug("The KNIME process has finished")
            self._knime_process = False
            self._workflow_finished()
            self._plugin._menu.set_all_dropdowns_to_none()
        else:
            return

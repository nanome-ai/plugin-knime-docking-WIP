import nanome
from nanome.util import Logs
from nanome.util import Color
from nanome.api.ui import Dropdown,DropdownItem
from functools import partial
import pathlib
import os

class KNIMEmenu():
    def __init__(self, knime_plugin):
        self.menu = knime_plugin.menu
        self._plugin = knime_plugin
        self._selected_protein = None
        self._selected_ligands = []
        self._selected_grid = None
        self._run_button = None
        self._grid_folder = self._plugin._grid_dir
        self._run_button = None
        self._no_reset = False
    
    def _request_refresh(self):
        self._plugin.request_refresh()

# Call back to the KNIMEExamplePlugin.py plugin class and run the workflow
    def _run_workflow(self):
        self._plugin.run_workflow()


## Appropriating functions from Muzhou's docking plugin ##

# Get complex data from Nanome workspace
    def populate_protein_ligand_dropdown(self, complex_list):

        Logs.debug("calling reset from change_complex_list")

        if self._no_reset:
            self._no_reset = False
        else:
            self.reset(update_menu=False)


        ## Populate the ligand and protein dropdown lists with loaded complexes ##
        ligand_list = []
        protein_list = []

        for complex in complex_list:
            dd_item1 = DropdownItem()
            dd_item2 = DropdownItem()
            dd_item1.complex = complex
            dd_item2.complex = complex
            dd_item1._name = complex.full_name
            dd_item2._name = complex.full_name
            ligand_list.append(dd_item1)
            protein_list.append(dd_item2)
            
        # pass the complex lists to the dropdown menus, handle selection behavior
        self._ligand_dropdown.items = ligand_list
        self._protein_dropdown.items = protein_list
        self._ligand_dropdown.register_item_clicked_callback(partial(self.handle_dropdown_pressed,self._selected_ligands,'ligand'))
        self._protein_dropdown.register_item_clicked_callback(partial(self.handle_dropdown_pressed,self._selected_protein,'protein'))

        self._plugin.update_menu(self._menu)

# Get grid data from specified location in plugin machine's filesystem
    def populate_grid_dropdown(self):
        ## Update the Docking Grid dropdown with files from grid folder ##
        grid_list = []
        for filename in os.listdir(self._grid_folder):
            grid_dd_item = DropdownItem()
            grid_dd_item._name = os.path.splitext(filename)[0]
            grid_list.append(grid_dd_item)
        
        self._grid_dropdown.items = grid_list
        self._grid_dropdown.register_item_clicked_callback(partial(self.handle_dropdown_pressed,self._selected_grid,'grid'))

        self._plugin.update_menu(self._menu)

# Control selection behavior upon interaction with dropdowns
    def handle_dropdown_pressed(self,docking_component,component_name,dropdown,item):
        Logs.debug("I made it to handle_dropdown_pressed function!")
        Logs.debug(item._name, "is the value of the item")
        if component_name == 'ligand':
            #cur_index = item.complex.index
            #if cur_index not in [x.complex.index for x in self._selected_ligands]:
            if not self._selected_ligands:
                self._selected_ligands.append(item)
                item.selected = True
            else:
                # for x in self._selected_ligands:
                #     if x.complex.index == cur_index:
                #         self._selected_ligands.remove(x)
                #         break
                if (len(self._selected_ligands) > 1) or\
                   (len(self._selected_ligands) == 1 and self._selected_ligands[0].complex.index != item.complex.index):
                    self._selected_ligands = [item]
                    item.selected = True
                else:
                    self._selected_ligands = []
                    item.selected = False

            # if len(self._selected_ligands) > 1:
            #     self._ligand_txt._text_value = 'Multiple'
            #     self._ligand_dropdown.use_permanent_title = True
            #     self._ligand_dropdown.permanent_title = "Multiple"
            if len(self._selected_ligands) == 1:
                #self._ligand_txt._text_value = item.complex.full_name if len(item.complex.full_name) <= 4 else item.complex.full_name[:8]+'...'
                self._ligand_dropdown.use_permanent_title = False
            elif len(self._selected_ligands) == 0:
                self._ligand_dropdown.use_permanent_title = True
                self._ligand_dropdown.permanent_title = "None"
                #self._ligand_txt._text_value = "Ligand"

        elif component_name == 'protein':

            if self._selected_protein and self._selected_protein.index == item.complex.index:
                self._selected_protein = None
            else:
                self._selected_protein = item.complex

            if self._selected_protein: 
                self._protein_dropdown.use_permanent_title = False
                #self._protein_txt._text_value = item.complex.full_name if len(item.complex.full_name) <= 4 else item.complex.full_name[:8]+'...'
            else:
                #self._protein_txt._text_value = "protein"
                self._protein_dropdown.use_permanent_title = True
                self._protein_dropdown.permanent_title = "None"
                
        elif component_name == 'grid':
            if not self._selected_grid or self._selected_grid != item:
                self._selected_grid = item
            else:
                self._selected_grid = None
                item.selected = False
            if self._selected_grid:
                Logs.debug(self._selected_grid)
                self._grid_dropdown.use_permanent_title = False
                self._grid_dropdown.permanent_title = item._name
            else:
                self._grid_dropdown.use_permanent_title = True
                self._grid_dropdown.permanent_title = "None"

        #self.update_icons()
        self.refresh_run_btn_unusable()
        self._plugin.update_menu(self._menu)
 
# Only handles one ligand for now. For implementations of KNIME plugins with multiple ligands, the
# self._selected_ligands variable will need to be changed to an array, and the plugin.run_workflow  
# and KNIMErunner.run_knime methods will probably also need to be adjusted.
    def get_ligands(self):
        # ligands = []
        # for item in self._selected_ligands:
        #     ligands.append(item.complex)
        # return ligands
        if self._selected_ligands == []:
            return None
        return self._selected_ligands[0].complex

    def get_protein(self):
        if self._selected_protein == None:
            return None
        return self._selected_protein

    def make_plugin_usable(self, state=True):
        self._run_button.unusable = (not state) | self.refresh_run_btn_unusable(update = False)
        self._plugin.update_content(self._run_button)
        
    def refresh_run_btn_unusable(self, update=True,after = False):
        grid_requirement_met = self._selected_grid != None 
        Logs.debug("selected protein is: ",self._selected_protein)
        Logs.debug("selected ligand is: ",self._selected_ligands)
        Logs.debug("selected grid is: ",self._selected_grid)
        Logs.debug("after is: ",after)
        if self._selected_protein != None and len(self._selected_ligands) > 0 and grid_requirement_met and self._plugin._running:
            Logs.debug("run button unusable case 1")
            self._grid_dropdown.use_permanent_title = True
            self._run_button.text.value_unusable = "Running..."
            self._run_button.unusable = False
        elif self._selected_protein != None and len(self._selected_ligands) > 0 and grid_requirement_met and not self._plugin._running:
            Logs.debug("run button unusable case 3")
            self._grid_dropdown.use_permanent_title = True
            self._run_button.text.value_unusable = "Run"
            self._run_button.unusable = False
        else:
            Logs.debug('run button unusable case 2')
            self._grid_dropdown.use_permanent_title = True
            self._run_button.text.value_unusable = "Run"
            self._run_button.unusable = True
        if update:
            self._plugin.update_content(self._run_button)

        return self._run_button.unusable

    def reset(self, update_menu=True):
        Logs.debug('reset called')
        self._selected_grid = None
        self._selected_ligands = []
        self._selected_protein = None
        
        self.make_plugin_usable()
        self._plugin.update_menu(self._menu)

    def clear_dropdown(self, dropdown):
        dropdown.use_permanent_title = True
        dropdown.permanent_title = "None"
    
    def set_all_dropdowns_to_none(self):
        dropdown_list = [self._ligand_dropdown, self._protein_dropdown, self._grid_dropdown]
        for dropdown in dropdown_list:
            self.clear_dropdown(dropdown)
    
# I guess everything that happens (interactions w/menu) are handled in this function
    def build_menu(self):
        # import the json file of the new UI
        menu = nanome.ui.Menu.io.from_json(os.path.join(os.path.dirname(__file__), 'KNIME_menu_POC_dropdown.json'))
        self._plugin.menu = menu

        # defining callbacks
        # what to do when the run button (in secondary menu) is pressed
        def run_button_pressed_callback(button):
            self._run_workflow()

        # Populate the empty dropdown nodes on the menu with /dropdown/ content
        # Needed because stack studio currently does not support dropdown content
        #Ligand dropdown
        self._ligand_dropdown = menu.root.find_node("LigandDropdown").add_new_dropdown()
        self._ligand_dropdown.use_permanent_title = True
        self._ligand_dropdown.permanent_title = "None"
        #Protein dropdown
        self._protein_dropdown = menu.root.find_node("ComplexDropdown").add_new_dropdown()
        self._protein_dropdown.use_permanent_title = True
        self._protein_dropdown.permanent_title = "None"
        #GLIDE grid dropdown
        self._grid_dropdown = menu._root.find_node("GridDropdown").add_new_dropdown()
        self._grid_dropdown.use_permanent_title = True
        self._grid_dropdown.permanent_title = "None"

        # run button
        self.ln_run_button = menu.root.find_node("RunButton")
        run_button = self.ln_run_button.get_content()
        run_button.register_pressed_callback(run_button_pressed_callback)
        self._run_button = run_button
        self._run_button.enabled = False
        self.refresh_run_btn_unusable()

        # Update the menu
        self._menu = menu
        self._plugin.update_menu(menu)
        Logs.debug("Constructed plugin menu")
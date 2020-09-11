def main():
    output_dir = None
    grid_dir = None
    workflow_dir = None
    parser = argparse.ArgumentParser()
    parser.add_argument('--wkflw_dir', nargs=1, help='enter the path to the knime worklfow')
    parser.add_argument('--grid_dir', nargs=1, help='enter the path to the docking grid folder')
    parser.add_argument('--output_dir', nargs=1, help='enter the path to the desired output folder, where data generated by the plugin will be written')
    args = parser.parse_args()
    arg_dict = vars(args)
    
    Logs.debug(arg_dict)
       
    plugin = nanome.Plugin('KNIME_removeHs_POC_Windows', 'Removes hydrogen atoms using KNIME', 'test', False)
    plugin.set_plugin_class(KNIME_removeHs_POC)
    plugin.run('plugins.nanome.ai', 9999)

    python run.py -a plugins.nanome.ai -p 9999 -r -v --wkflw_dir=test --grid_dir=test --output_dir test
# Nanome - KNIME_removeHs_POC

Removes hydrogen atoms using KNIME

### Preparation

Install the latest version of [Python 3](https://www.python.org/downloads/)

| NOTE for Windows: replace `python3` in the following commands with `python` |
| --------------------------------------------------------------------------- |


Install the latest `nanome` lib:

```sh
$ python3 -m pip install nanome --upgrade
```

### Dependencies

- KNIME
- Microsoft Visual C++ 2015 Redistributable
- Miniconda3
- Python3 (In PATH)
- Nanome pip package (pip install nanome)

### Installation

To install KNIME-Docking:

- From KNIME, navigate to File > Install KNIME Extensions
- Select the RDKit, Vernalis Nodes, and KNIME Python integrations
- Install the extensions and restart KNIME when prompted
- Navigate to File > Preferences > KNIME > Python and point the 'Conda path' option to your installation of Conda
- Then, select Python 3 as the default version
- Click "New Environment" under Python 3 and use the default py3_knime option
- Once finished, click 'Apply'
- Navigate to File > Export Preferences, and enter your desired path for the preferences file. Make note of this path.

### Usage

- Close KNIME. The KNIME App must be closed in order for the plugin to work.
- Navigate to the this repository locally and review the arguments in run_command.txt. It should look something like this:
```sh
$ python run.py -a plugins.nanome.ai -p 9999 -v --wkflw_dir=C:\Users\Administrator\Github\plugin-knime-docking\knime-workspace\knime-workflow --grid_dir=C:\Users\Administrator\Github\plugin-knime-docking\knime-workspace\docking_grids --output_dir=C:\Users\Administrator\Github\plugin-knime-docking\knime-workspace\data\sdf_test
--preferences_path=C:\Users\Administrator\Github\plugin-knime-docking\knime-workspace\preferences.epf
```
- All flags are required:
- `wkflw_dir` is the directory to your workflow. By default, there is one located in ${repo}/knime-workspace
- `grid_dir` is the directory to your KNIME grid files. By default, there is one located in ${repo}/knime-workspace
- `output_dir` is the directory you want the output of your workflow to be saved to
- `preferences_path` is (above) where you exported your KNIME preferences to

### Docker Usage

Please refer to run_commands.txt to best match the environment you would like to run this plugin in.

### Development
This section of the readme is incomplete. Please check back later.

To run KNIME-Docking with autoreload:

```sh
$ python run.py -a plugins.nanome.ai -p 9999 -v -r ... [KNIME ARGS]
```

### License

MIT

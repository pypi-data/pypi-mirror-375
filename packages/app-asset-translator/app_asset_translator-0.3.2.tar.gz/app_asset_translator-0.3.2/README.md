# Translation Manager

## Getting started
To install the package, a simple command can be used within the desired python environment:
`pipx install app_asset_translator`

## Preparation
To ensure the package can be used properly, some files should be prepared beforehand. 

A critical file for the software to work is the `config.yaml` file.

This config file should be placed in the directory of specific projects you'd like to apply the translation manager to.

Within this config file, specific paths can be defined, such as the paths to string.xml files, or the iOS counterpart. The path to the output (and input) CSV file should also be configured here.

An example of this `config.yaml` file can be found within this project.
## Usage
Using the terminal, with the desired Python environment activated, the following commands can be used;
````commandline
app-asset-translator csv
app-asset-translator resources
app-asset-translator -h
````

# Libraries
- Written using [Python](https://www.python.org/).
- [Pandas](https://pypi.org/project/pandas/): Used to generate/manipulate CSV data.
- [PyYAML](https://pypi.org/project/PyYAML/): Used to parse YAML files.
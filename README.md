# Source Hunter
A convinient tool for analysing the dependency and calling relationship of source code.

## Installation
### Prerequisite
1. `Graphviz` is needed for rendering
2. The python wrapper named `graphviz`
#### How to install Graphviz
```bash
# On Ubuntu/Debian
sudo apt install graphviz

# On mac
brew install graphviz 

# On Centos/Fedora
sudo yum install graphviz

```

#### How to install graphviz the python package
If you install source_hunter using pip, you don't need to install this package manually. Otherwise, you may install
`graphviz` by `pip install graphviz`

### Install using pip:
```bash
pip install source_hunter
```
 
### Install from source code:
```bash
git clone https://github.com/pyeprog/source_hunter.git
cd source_hunter
python setup.py install
```

## Usage
```bash
# for help
hunt -h

# basic usage 
hunt [project_root_path] [target_module_file] [function_or_class]

# example
# search Usage of `YourModel` of `target_model.py` in current path
# and save the output pdf file at `~/saving/dir/saving_file_name.pdf`
# while ignoring all files with `test`, `pb2` or `migration` in its names.
cd ~/example_project
hunt . ./model/target_model.py YourModel \
    --path ~/saving/dir \
    --name saving_file_name \
    --ignore test --ignore pb2 --ignore migration
    
# output only to stdout
hunt . ./model/target_model.py YourModel --stdout

```

## Output


## limitation
1. Support only python3 project (will support more language soon)
2. Only understand absolute import (on schedule)


## Change log
- v0.33: add python parser and graphviz for pdf output

# Source Hunter
A convinient tool for analysing the dependency and calling relationship of source code.

while coding on large project, one may sometimes face the embarrassing situation to change the very base data models 
or interfaces which may have chance to break a lot of things.
There are some tools like [pydeps](https://pydeps.readthedocs.io/en/latest/) which gives you clue about what other modules
your current module depends on(dependency graph), but it won't tell which modules will be affected if you change your
module(calling graph). Source hunter is aiming at providing both calling and dependency graph at the same time.

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
Parse [flask_reddit](https://github.com/codelucas/flask_reddit)
```bash
cd flask_reddit
hunt . ./flask_reddit/users/models.py User
hunt . ./flask_reddit/users/models.py User --stdout

```
![pdf](https://github.com/pyeprog/source_hunter/blob/master/imgs/screen.png)


```bash
cd flask_reddit
hunt . ./flask_reddit/users/models.py User --stdout

```
![shell](https://github.com/pyeprog/source_hunter/blob/master/imgs/shell.png)

## limitation
1. Support only python3 project (will support more language soon)
2. python import should on same line and not support \ sign for now
3. Not Support dependency analysis for now


## Change log
- v0.33: 
    - Add python parser and graphviz for pdf output
- v0.34: 
    - Add support for parsing relative import of python project
- v0.35: 
    - Add support for png and pdf output format
    - fix stdout mal-format
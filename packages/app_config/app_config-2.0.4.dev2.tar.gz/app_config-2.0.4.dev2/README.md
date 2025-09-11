# app_config
[![image](https://img.shields.io/pypi/v/app_config.svg)](https://python.org/pypi/app_config)
[![image](https://img.shields.io/pypi/l/app_config.svg)](https://python.org/pypi/app_config)
[![image](https://img.shields.io/pypi/pyversions/app_config.svg)](https://python.org/pypi/app_config)

[![image](https://img.shields.io/pypi/dm/app_config?style=flat-square)](https://pypistats.org/packages/app_config)
![Pipeline](https://gitlab.com/tpgllc/app_config/badges/main/pipeline.svg)
![Coverage](https://gitlab.com/tpgllc/app_config/badges/main/coverage.svg)



## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Implementation](#implementation)
 - <a href="https://gitlab.com/tpgllc/app_config/-/blob/main/doc/customizing.md" target="_blank">Customization</a>

## Overview

This is a utility module which reads a configurate file and builds a configuration namespace module which can be passed throughout an application.  If the configuration file does not exist, a file is created with default values from the config module.  The values in the confiuration module are updated from the variables in the config file.  The config module can be imported into each python application program which permits the passing of varibles between programs. Reading and writing of the config file is based upon the standard library configparser module.

  The variables can be references as `cfg.varname` as shown in the example below.  This example lists the variables in the cfg module.

myapp.py

```
    from src import config as cfg

    for s, v in cfg.cfg_values.items():
        print(f"{s}: {v}")
        for var in v:
            print(f"   {var[0]}: {getattr(cfg, var[0])}")

     print(f"version: {cfg.sys_cfg_version}")
```

### Features

* Allow values to be changed in a config file and passed into the system - no changing of source code
* Manage the config file, reading parameters into the application, creating the initial file with defaults, updating existing config file if parameters are added or names change in the config module.  Pre-defined comments and config file values are preserved.
* Creates a config module that can be used to pass paramters to other modules.  The values in this module are updated from the values in the config file and can be modified by the application.
* Internal variables/objects can be added to the config module and passed to each module in application.

## Requirements

This module requires python 3.10 due to use of case statement.

Standard Python packages are utilized and no special packages are needed.

## Project structure

The default implementation assumes the following project structure ***(but this can be altered, see customization)***:

```
proj_name/
    data/
    src/
        __init__.py           (an empty file)
        config.py
        configparms_ext.py (if used)
    proj_main.py
```

If you have a different project structure, then the configparms_ext.py method ```set_directrories``` can be modified to set the path to the data folder and src folder of your project.  

## Setup

From a terminal window:

1. Install the package in your environment:

    ```pip install app_config```

1. Change directories to your src folder:

    ```cd src```

1. Copy the config file into the src directory.

    - create an empty `__init__.py` file in the source directory with your favorite editor

    - enter the following command:

        ```app_config-init```
    
    This command copies two file into the current directory: config.py and configparms_ext.py

    Rerunning ```app_config-init``` will not overwrite existing files, but will receate the `configparms_ext.py` file if it has been deleted.

1. Modify the config file to meet your application needs. Be sure to change the value of the variable *cfg_flnm* to the name of your config file.

1. In each module, add the import for the config.  This should be the first application import, after the standard python module imports, 
    ```
    import os
    import sys
    from src import config as cfg
    from src import my_other_application_modules
    ```
1. In ```config.py``` set the autorun flag or call the run method `cfg.run()` in your application.  See the comments at the bottom of the config file.

1. The first time you run a program with the config import, it will look for a config file in the data directory and if does not exist, it will create one.

All set!


## Implementation

In each of your application programs, the ```src.config``` module should be imported as the first application import in each application module.

*`import src.config as cfg`*

The first import reads the config file (`data/xxxxx.cfg`) and loads the runtime values.  If the cfg file, as named in the variable *cfg.cfg_flnm*, does not exist, it is created with the default values.

The config module creates a module as a namespace so variables can be referenced as cfg.var.  Each variable is defined with its default value in the namespace, unless overridden by the config file.  A config file, *`xxxxx.cfg`* is created on the first import of config if it does not exist, where *xxxxx* is name as set in the variable `cfg.cfg_flnm`.

Any changes to the cfg file in the data folder are local and override the defaults.

### Version (`sys_cfg_version`)

If a new variable is added in the *`src.config`* module or if the variable name changes in the config module, then the version number (`sys_cfg_version`) should be updated in the config module (not the config file).  When the cfg module version and the config file version differ, a rewrite the local cfg file will be triggered with the new changes, perserving any values previously set in the file.

### Modifying config.py ###

Two programs from this repo are provided for use by your application:
* scr/config.py
* src/configparms_ext.py   (for customization)

#### config.py

It is intended for the *`config.py`* file to be modified for the application.  Parameters unique to the application are defined with their defaults.  Replace the *var1-3* and *m1-2* variables with the variables needed by the application.  Also set the cfg filename (*cfg_flnm*).

The *`sys_cfg_version`* variable must not be deleted, it will be updated as new parameters are added to the config file and the change in this value triggers the rewrite of the file.

##### Variables

The *`cfg_values`* is a dictionary that defines the sections and variables to be written to the config file.  The key to the dictionary is the section and the value is a list of lists with variable name and variable type (see sample in config.py).

Be sure all variables to be in the config file are defined in the *`cfg_values`* variable.

Valid types supported are 
- integer
- float
- boolean
- string
- list

##### Comments 

The variable *`cfg_comments`* contains any comment to be written to the config file to explain a variable or section.

Section comments are written after the section label and variable comments are written before the variable in the config file.

The *`cfg_comments`* variable is a dictionary and the key is the variable or section name and the value is a list with each item in the list being written as a seperate comment line.

#### configparms_ext.py

To override setting of path variables or to provide special processing logic, the *`configparm_ext.py`* module is provided.

##### Set path variables

Modify the method *`set_directories`* to support the structure of your project.

##### Special processing

Sometimes, special processing is needed to covert a section to dictionary in the config module, or special handling of a variable is needed.  This can be accomplished by modifying the `configparms_ext.py` module.  See the <a href="https://gitlab.com/tpgllc/app_config/-/blob/main/doc/customizing.md" target="_blank">customization documentation</a> to modify standard processing.

### Summary of set up ###
* Install the package
* Run app_config-init to extract the config.py and configparms_ext.py and place in your project src directory
* Modify these modules for your application (set the config file name and set the variables)
* import the module into your application
    



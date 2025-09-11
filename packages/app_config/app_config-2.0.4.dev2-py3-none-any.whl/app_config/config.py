#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  config.py
#     in each module, import config as cfg
#     access variables in this module as cfg.xxxxxx
#
#     the config file is created in the data directory and can be modified
#     for a specific run.
#
#  Copyright 2024 cswaim <cswaim@jcrl.net>
#  Licensed under the Apache License, Version 2.0
#  http://www.apache.org/licenses/LICENSE-2.0

# set path to application source directory
import os
import sys
import importlib

# import this module as the first application module:
#     import <relative-path>.config as cfg

# system variables change only the cfg_flnm
cfg_flnm = 'test_config.cfg'
wkdir_path = None
wkdir = None
srcdir = os.path.dirname(__file__)
datadir = None

# set the srcdir
#srcdir = os.path.dirname(__file__)

# section variables
# MAIN
var1 = True
var2 = 2
var3 = 3.4

# DATA
m1 ='textm1'
m2 = ['m2-1','m2-2','m2-3']

# SYSTEM
sys_cfg_version = '0.1'
sys_var = "sysvar test variable"

# values passed to ConfigParms
# dict key is the section, value is list of variable names and type
#   types are i-integer, f-float, b-boolean, s-string, l-list

cfg_values = {'MAIN': [('var1', 'b'), ('var2', 'i'), ('var3', 'f')],
              'DATA': [('m1', 's'), ('m2', 'l')],
              'SYSTEM': [('sys_cfg_version', 's'), ('sys_var', 's')],
              }

# comments
cfg_comments = {'sys_cfg_version': ['changing the version number will cause file to be rewritten'],
                'sys_var': ['sys var cmt1', 'remove me'],
                'var1': ['this is a comment for var1'],
                'm2': ['m2 comment 1', 'm2 comment 2'],
                'DATA': ['sec comment 1', 'sec comment 2']
                }

# config obj built by config parse
config = None

# variables passed to all modules
gen_var1 = []

"""
This module takes advantage of Python's behavior of importing the module
the first time and for every import after the first, only a reference is
passed.  The code is not re-executed.

There are several ways to instantiate the ConfigParm class which reads the
cfg file.  Pick an approach that you like.

Note that setting the autorun may effect tests as the defaults from the
config file are loaded and the test defaults must be reset.

to autorun on the first import:
    cp = ConfigParms(cfg_values, cfg_comments, autorun=True)

to control the run in your application, just instantiate the class in this module
    run_init()

and then in the application code, read the parm file:
    cfg.run()
"""

# the imports must be at end of the config module
#
# To override the behavior of ConfigParms
# such as change the path to data or src directories
# or to modify the default behavior for a section or variable
# make the modifications in the configparms_ext module
#
# the init will look for the configparms_ext module first and use it
# if it exists, otherwise it will use the package configparms module

def run_init():
    """run the init
        if the configparms_ext module exists, use it and is preferred
        otherwise the package configparms module is used
    """
    global cp, cu
    wkdir = os.getcwd()
    relative_path = os.path.relpath(srcdir, wkdir)
    try:
        configparms_mod = importlib.import_module('.configparms_ext',relative_path)
    except Exception as e:
        print(f"### {e}")
        print("###  loading ConfigParmsExt from app_config")
        from app_config.configparms import ConfigParms

    ConfigParms = configparms_mod.ConfigParmsExt
    from app_config.configutils import ConfigUtils
    cp = ConfigParms(cfg_values, cfg_comments, autorun=False)
    cu = ConfigUtils()

def run():
    """read the config file & set values in module"""
    cp.run()

# instantiate the configparms module
run_init()

'''

@author: wanzeyu

@contact: wan.zeyu@outlook.com

@file: __init__.py

@time: 2017/5/18 20:37

@desc: initialize sys path

'''
import inspect
import os
import sys

# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

# use this if you want to include modules from a subfolder
cmd_subfolder = os.path.realpath(
    os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "subfolder")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
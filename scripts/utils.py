#!/usr/bin/env python3
# auxiliary functions for tree generation

import os
from os.path import basename
import glob
import ast # abstract syntax tree module (used for string to dictionary parsing)


# Read in python sapling tree model
def read_tree_model(model):
    tree_model = {}

    with open(model) as m:
        model_content = m.readlines()
        tree_model = ast.literal_eval(model_content[0])

    if not tree_model:
        print('error: empty tree config found')
        return

    return tree_model


# Check valid file
def valid_file(path, prog=None, message='%s: no such file found: %s'):
    if not os.path.isfile(path):
        print(message % (prog, path))
        return False
    else:
        return True


# Check file not already exists
def file_exists(path, filename, prog=None):
    # glob lists all the files in the directory
    if [n for n in glob.glob(path + filename + '*')]:
        print('%s Warning: the output file already exists: %s' % (prog, path + filename + '*'))
        return True
    else:
        return False


def create_filepath(path, file):
    return os.path.join(path, file)


# Return file name without extension 
def get_filename(path):
    return os.path.splitext(basename(path))[0]


def get_path(path_to_file):
    return os.path.dirname(path_to_file)


def get_filename_with_extension(path):
    return os.path.splitext(basename(path))[0] + os.path.splitext(basename(path))[1]


def get_files(path, file_format):
    return [n for n in glob.glob(path + '*' + file_format)]


def remove_file(file_path):
    os.remove(file_path)

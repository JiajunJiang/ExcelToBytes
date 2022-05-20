from enum import Enum

import yaml


class language_type(Enum):
    cplus = 1
    csharp = 2
    java = 3
    go = 4
    python = 5
    php = 6
    js = 7
    kotlin = 8
    objc = 9


dict = {}


def load():
    file = open("config.yml")
    global dict
    dict = yaml.safe_load(file)


def client_language():
    global dict
    return dict['client_language']


def server_language():
    global dict
    return dict['server_language']


def package_name():
    global dict
    return dict['package_name']


# java only
def java_package():
    global dict
    return dict['java_package']


# java only
def java_outer_classname():
    global dict
    return dict['java_outer_classname']


# java only
def java_multiple_files():
    global dict
    return dict['java_multiple_files']


# "SPEED" / "CODE_SIZE" / "LITE_RUNTIME"
def optimize_for():
    global dict
    return dict['optimize_for']


def cc_enable_arenas():
    global dict
    return dict['cc_enable_arenas']


# Objective-C only
def objc_class_prefix():
    global dict
    return dict['objc_class_prefix']


def client_file_ext():
    global dict
    return dict['client_file_ext']


def server_file_ext():
    global dict
    return dict['server_file_ext']

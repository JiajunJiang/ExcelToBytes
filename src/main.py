# encoding:utf-8
import os

import xlrd
import importlib
import sys

import global_config
from archive import archive
from command import command
from interpreter import interpreter
from parse import parse

from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

importlib.reload(sys)


# argv 1 = Excel File Path
# argv 2 = Flag                 c - Client s - Server
def build(language, flag):
    for sheet in workbook.sheets():
        if "Sheet" in sheet.name or "#" in sheet.name:
            continue
        print("Start build Sheet: " + sheet.name)
        interpreter(excel_file, sheet.name, language, flag)
        parse(excel_file, sheet.name, language, flag)

        command.build_language_file(sheet.name + '.proto', language)

        archive(language, flag)

        print("Build {} Success".format(sheet.name))
    pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("please input excel_file")

    excel_file = sys.argv[1]

    try:
        workbook = xlrd.open_workbook(excel_file)
    except BaseException as e:
        print("open ExcelFile(%s) failed!" % excel_file)
        raise

    yaml_files = [file for file in os.listdir(os.getcwd()) if file.endswith(".yml")]
    data = []
    for file in yaml_files:
        global_config.load(file)
        print("Build Start")
        language_enum = global_config.language_type(global_config.language())
        flag = str(global_config.language_flag())
        print(flag)
        build(language_enum, flag)



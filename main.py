# encoding:utf-8

import xlrd
import importlib
import sys
import os

import global_config
from archive import archive
from command import command
from interpreter import interpreter
from parse import parse

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

        command.build_language_file(sheet.name.lower() + '.proto', language)

        archive(language, flag)

        print("Build {} Success".format(sheet.name))
    pass


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit("please input excel_file")

    excel_file = sys.argv[1]
    if len(sys.argv) == 3:
        flag = sys.argv[2]
    else:
        flag = 'cs'

    try:
        workbook = xlrd.open_workbook(excel_file)
    except BaseException as e:
        print("open ExcelFile(%s) failed!" % excel_file)
        raise

    language = ""
    if flag.__contains__('c'):
        print("Choose Client")
        build(global_config.client_language, 'c')
    if flag.__contains__('s'):
        print("Choose Server")
        build(global_config.server_language, 's')
    if not flag.__contains__('c') and not flag.__contains__('s'):
        sys.exit("params 2 flag is not c or s")

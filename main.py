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
if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit("please use path flag operation")

    excel_file = sys.argv[1]
    flag = sys.argv[2]

    try:
        workbook = xlrd.open_workbook(excel_file)
    except BaseException as e:
        print("open ExcelFile(%s) failed!" % excel_file)
        raise

    language = ""
    if flag == 'c':
        language = global_config.client_language
        print("Choose Client")
    elif flag == 's':
        language = global_config.server_language
        print("Choose Server")
    else:
        sys.exit("params 2 flag is not c or s")

    for sheet in workbook.sheets():
        if "Sheet" in sheet.name or "#" in sheet.name:
            continue
        print("Start build Sheet: " + sheet.name)
        interpreter(excel_file, sheet.name, language, flag)
        parse(excel_file, sheet.name, language, flag)

        command.build_language_file(sheet.name.lower() + '.proto', language)

        archive(language, flag)

        print("Build {} Success".format(sheet.name))

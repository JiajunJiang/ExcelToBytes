import xlrd
import importlib
import sys
import os

importlib.reload(sys)

# argv 1 = Excel File Path
# argv 2 = Client or Server     c - Client s - Server
# argv 3 = Operation            1 - FormatParse 2 - DataParse 0 - Both
if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("need three params")
        sys.exit(-1)

    excel_file = sys.argv[1]
    language_type = sys.argv[2]

    if not sys.argv[3].isdigit():
        print("params 3 is not ")
        sys.exit(-2)

    operation = int(sys.argv[3])

    try:
        workbook = xlrd.open_workbook(excel_file)
    except BaseException as e:
        print("open ExcelFile(%s) failed!" % excel_file)
        raise

    language = ""
    if language_type == "c":
        language = "Client"
        print("Choose Client")
    elif language_type == "s":
        language = "Server"
        print("Choose Server")
    else:
        print("params 2 is not c or s")
        sys.exit(-3)

    print(len(workbook.sheets()))
    for sheet in workbook.sheets():
        if "Sheet" in sheet.name or "#" in sheet.name :
            continue
        print("Start build Sheet: " + sheet.name)

    print("Hello world")

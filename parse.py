import sys

import xlrd

from command import command

FIELD_RULE_ROW = 0  # optional or repeated
FIELD_TYPE_ROW = 1  # protobuf type
FIELD_NAME_ROW = 2  # field name
FIELD_DESC_ROW = 3  # description
FIELD_FLAG_ROW = 4  # language flag
FIELD_VALUE_ROW = 5  # value


class parse:
    def __init__(self, file_path, sheet_name, language_type, flag):
        self.module = None
        self.pb_file = sheet_name + "_pb2"
        self.flag = flag
        self.language_type = language_type
        self.sheet_name = sheet_name
        self.file_path = file_path

        self.current_col = 0
        self.field_count = 1

        try:
            self.work_book = xlrd.open_workbook(self.file_path)
        except BaseException as e:
            print("can't open file %s" % self.file_path)
            raise

        try:
            self.sheet = self.work_book.sheet_by_name(self.sheet_name)
        except BaseException as e:
            print("can't open sheet %s " % self.sheet_name)
            raise

        self.row_length = len(self.sheet.col_values(0))
        self.col_length = len(self.sheet.row_values(0))

        self.current_row = 0
        self.current_col = 0

        self.load()

    def load(self):
        try:
            command.load_moudle(self.pb_file)
            self.module = sys.modules[self.pb_file]
        except BaseException as e:
            print("{} no exist or error".format(self.pb_file))
            raise
        self.start()

    def start(self):
        array_list = getattr(self.module, self.sheet_name + 'List')()

        for self.current_row in range(FIELD_VALUE_ROW, self.row_length):
            value = str(self.sheet.cell_value(self.current_row, 0)).strip()
            print(value)

            item = array_list.list.add()
            self.parse_item(item)

    def parse_item(self, item):
        self.current_col = 0
        while self.current_col < self.col_length:
            if self.check_flag():
                self.parse_field(item)
            self.current_col += 1

    def check_flag(self):
        key = str(self.sheet.cell_value(FIELD_FLAG_ROW, self.current_col)).strip().lower()
        return key.__contains__(self.flag)

    def parse_field(self, item):
        field_type = str(self.sheet.cell_value(FIELD_TYPE_ROW, self.current_col))
        rule = str(self.sheet.cell_value(FIELD_RULE_ROW, self.current_col))

        print(field_type)
        print(rule)

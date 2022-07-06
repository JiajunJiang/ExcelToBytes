# encoding:utf-8

import sys

import xlrd

import global_config
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
            if not self.check_annotation():
                item = array_list.list.add()
                self.parse_item(item)

        data = array_list.SerializeToString()
        self.save(data)

        if global_config.save_log():
            self.save_log(str(array_list))

    def parse_item(self, item):
        self.current_col = 0
        while self.current_col < self.col_length:
            if self.check_flag():
                self.parse_field(item)
            self.current_col += 1

    def check_annotation(self):
        if self.current_col == 0:
            field_value = self.sheet.cell_value(self.current_row, self.current_col)
            return str(field_value).__contains__("#")

    def check_flag(self):
        key = str(self.sheet.cell_value(FIELD_FLAG_ROW, self.current_col)).strip()
        return key.__contains__(self.flag)

    def parse_field(self, item):
        field_type = str(self.sheet.cell_value(FIELD_TYPE_ROW, self.current_col))
        rule = str(self.sheet.cell_value(FIELD_RULE_ROW, self.current_col))
        field_name = str(self.sheet.cell_value(FIELD_NAME_ROW, self.current_col))

        if rule == "optional":
            self.set_optional_value(field_type, field_name, item)
        elif rule == "repeated":
            self.set_repeated_value(field_type, field_name, item)
        elif rule == "map":
            self.set_map_value(field_type, field_name, item)

    def set_map_value(self, field_type, field_name, item):
        field_type_list = str(field_type).split(',')
        if len(field_type_list) != 2:
            print("value error {}".format(field_type_list))
            raise
        key_type = field_type_list[0]
        value_type = field_type_list[1]
        field_value = self.sheet.cell_value(self.current_row, self.current_col)
        if len(field_value) > 0:
            field_value_list = field_value.split(';')
            for value in field_value_list:
                value_list = value.split('-')
                if len(value_list) != 2:
                    print("value error {}".format(value_list))
                    raise
                value1 = self.get_value_by_field(key_type, value_list[0])
                value2 = self.get_value_by_field(value_type, value_list[1])
                item.__getattribute__(field_name).__setitem__(value1, value2)

    def set_repeated_value(self, field_type, field_name, item):
        field_value = self.sheet.cell_value(self.current_row, self.current_col)
        if len(str(field_value)) > 0:
            if str(field_value).find(";"):
                field_value_list = str(field_value).split(';')
            else:
                field_value_list = []
                field_value_list.append(field_value)

            for temp in field_value_list:
                if len(str(temp)) > 0:
                    value = self.get_value_by_field(field_type, temp)
                    item.__getattribute__(field_name).append(value)

    def set_optional_value(self, field_type, field_name, item):
        field_value = self.sheet.cell_value(self.current_row, self.current_col)
        item.__setattr__(field_name, self.get_value_by_field(field_type, field_value))

    def get_value_by_field(self, field_type, field_value):
        if field_type == "int32" \
                or field_type == "int64" \
                or field_type == "uint32" \
                or field_type == "uint64" \
                or field_type == "sint32" \
                or field_type == "sint64" \
                or field_type == "fixed32" \
                or field_type == "fixed64" \
                or field_type == "sfixed32" \
                or field_type == "sfixed64":
            if len(str(field_value)) == 0:
                return 0
            else:
                return int(float(field_value))
        elif field_type == "float" or field_type == "double":
            if len(str(field_value)) == 0:
                return 0.0
            else:
                return float(field_value)
        elif field_type == "bool":
            if len(str(field_value)) == 0:
                return False
            else:
                return True if int(float(field_value)) == 1 else False
        elif field_type == "string":
            return str(field_value).encode("utf8")
        else:
            print("error filed_type {}".format(field_type))
            return None

    def save(self, data):
        if self.flag == 'c':
            file_name = self.sheet_name + global_config.client_file_ext()
        elif self.flag == 's':
            file_name = self.sheet_name + global_config.server_file_ext()
        file = open(file_name, 'wb+')
        file.write(data)
        file.close()

    def save_log(self, data):
        if self.flag == 'c':
            file_name = self.sheet_name + '.log'
        elif self.flag == 's':
            file_name = self.sheet_name + '.log'
        file = open(file_name, 'wb+')
        file.write(data.encode())
        file.close()

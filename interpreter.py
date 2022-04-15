import sys

import xlrd

import global_config

FIELD_RULE_ROW = 0  # optional or repeated
FIELD_TYPE_ROW = 1  # protobuf type
FIELD_NAME_ROW = 2  # field name
FIELD_DESC_ROW = 3  # description
FIELD_FLAG_ROW = 4  # language flag


class interpreter:
    def __init__(self, file_path, sheet_name, language_type, flag):
        self.content = []
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
        print("prepare row = %s" % self.row_length)
        self.col_length = len(self.sheet.row_values(0))
        print("prepare col = %s" % self.col_length)

        self.start()

    def start(self):
        self.layout_file_header()
        self.layout_struct_name(self.sheet_name)
        self.layout_field()
        print(self.content)

    def layout_file_header(self):
        self.content.append("syntax = \"proto3\";\n")
        self.content.append("package = %s;\n" % global_config.package_name)
        if self.language_type == global_config.language_type.java:
            self.content.append("option java_package = %s;" % global_config.java_package)
            self.content.append("option java_outer_classname = %s;" % global_config.java_outer_classname)
            self.content.append(
                "option java_outer_classname = %s;" % ("true" if global_config.java_multiple_files else "false"))
            self.content.append("option optimize_for = %s;" % global_config.optimize_for)

        if self.language_type == global_config.language_type.cplus:
            self.content.append("option optimize_for = %s;" % global_config.optimize_for)
            self.content.append(
                "option cc_enable_arenas = %s;" % ("true" if global_config.cc_enable_arenas else "false"))

    def layout_struct_name(self, struct_name):
        self.content.append("message %s\n{" % struct_name)

    def layout_field(self):
        while self.current_col < self.col_length:
            if not self.check_flag():
                self.current_col += 1
                continue
            else:
                self.check_rule()
                self.current_col += 1

    def check_flag(self):
        key = str(self.sheet.cell_value(FIELD_FLAG_ROW, self.current_col)).strip().lower()
        return key.__contains__(self.flag)

    def check_rule(self):
        rule = str(self.sheet.cell_value(FIELD_RULE_ROW, self.current_col))
        name = str(self.sheet.cell_value(FIELD_NAME_ROW, self.current_col))
        desc = str(self.sheet.cell_value(FIELD_DESC_ROW, self.current_col))
        if rule == "optional":
            self.content.append("optional {} = {}; //{}\n".format(name, self.field_count, desc))
            self.field_count += 1
        elif rule == "repeated":
            self.content.append("repeated {} = {}; //{}\n".format(name, self.field_count, desc))
            self.field_count += 1
        else:
            sys.exit("Field Rule Error rule = {} name = {}".format(rule, name))

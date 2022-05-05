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


class interpreter:
    def __init__(self, file_path, sheet_name, language_type, flag):
        self.content = []
        self.flag = flag
        self.language_type = language_type
        self.sheet_name = sheet_name
        self.file_path = file_path
        self.pb_name = "{}.proto".format(self.sheet_name)

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
        self.layout_tail()
        self.layout_list()
        self.write_file()
        command.build_python_file(self.pb_name)
        print(self.content)

    def layout_file_header(self):
        self.content.append("syntax = \"proto3\";\n")
        self.content.append("package {};\n".format(global_config.package_name))
        if self.language_type == global_config.language_type.java:
            self.content.append("option java_package = \"{}\";\n".format(global_config.java_package))
            self.content.append("option java_outer_classname = \"{}\";\n".format(global_config.java_outer_classname))
            self.content.append(
                "option java_multiple_files = {};\n".format("true" if global_config.java_multiple_files else "false"))
            self.content.append("option optimize_for = {};\n".format(global_config.optimize_for))

        if self.language_type == global_config.language_type.cplus:
            self.content.append("option optimize_for = {};\n".format(global_config.optimize_for))
            self.content.append(
                "option cc_enable_arenas = {};\n".format("true" if global_config.cc_enable_arenas else "false"))

        if self.language_type == global_config.language_type.go:
            self.content.append("option go_package=\"./;{}\";".format(self.sheet_name))

    def layout_struct_name(self, struct_name):
        self.content.append("\nmessage %s\n{\n" % struct_name)

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
        field_type = str(self.sheet.cell_value(FIELD_TYPE_ROW, self.current_col))
        rule = str(self.sheet.cell_value(FIELD_RULE_ROW, self.current_col))
        name = str(self.sheet.cell_value(FIELD_NAME_ROW, self.current_col))
        desc = str(self.sheet.cell_value(FIELD_DESC_ROW, self.current_col))

        if not self.check_type(field_type):
            sys.exit("Error Field Type Col = {} name = {}".format(self.current_col, name))

        if rule == "optional":
            self.content.append("optional {} {} = {}; //{}\n".format(field_type, name, self.field_count, desc))
            self.field_count += 1
        elif rule == "repeated":
            self.content.append("repeated {} {} = {}; //{}\n".format(field_type, name, self.field_count, desc))
            self.field_count += 1
        else:
            sys.exit("Field Rule Error rule = {} name = {}".format(rule, name))

    def check_type(self, field_type):
        if field_type == "int32" \
                or field_type == "int64" \
                or field_type == "uint32" \
                or field_type == "uint64" \
                or field_type == "sint32" \
                or field_type == "sint64" \
                or field_type == "fixed32" \
                or field_type == "fixed64" \
                or field_type == "sfixed32" \
                or field_type == "sfixed64" \
                or field_type == "float" \
                or field_type == "double" \
                or field_type == "bool" \
                or field_type == "string":
            return True
        elif field_type.__contains__("map"):
            # todo map field
            return True
        else:
            return False

    def layout_tail(self):
        self.content.append("}\n")

    def layout_list(self):
        self.content.append("\n")
        self.content.append("message {}List\n".format(self.sheet_name))
        self.content.append("{\n")
        self.content.append("repeated {} list = 1;".format(self.sheet_name))
        self.content.append("\n}")

    def write_file(self):
        file = open(self.pb_name, "w+", encoding='utf-8')
        for line in self.content:
            temp = line.replace("optional", "            ").replace("repeated", "    repeated")
            file.write(temp)
        file.close()

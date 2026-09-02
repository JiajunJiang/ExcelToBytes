# encoding:utf-8

import sys

import global_config
from schema import Column, read_columns


class interpreter:
    def __init__(self, work_book, sheet_name, language_type, flag):
        self.content = []
        self.flag = flag
        self.language_type = language_type
        self.sheet_name = sheet_name
        self.pb_name = "{}.proto".format(self.sheet_name)

        self.current_col = 0
        self.field_count = 1
        self.nested = {}

        self.work_book = work_book
        self.sheet = self.work_book.sheet_by_name(self.sheet_name)

        self.columns = read_columns(self.sheet, self.flag)

        self.row_length = self.sheet.nrows
        self.col_length = self.sheet.ncols

        self.start()

    def start(self):
        self.layout_file_header()
        self.layout_struct_name(self.sheet_name)
        self.layout_field()
        self.layout_tail()
        self.layout_list()
        self.write_file()

    def layout_file_header(self):
        self.content.append("syntax = \"proto3\";\n")
        self.content.append("package {};\n".format(global_config.package_name()))
        if self.language_type == global_config.language_type.java:
            self.content.append("option java_package = \"{}\";\n".format(global_config.java_package()))
            self.content.append("option java_outer_classname = \"{}\";\n".format(global_config.java_outer_classname()))
            self.content.append(
                "option java_multiple_files = {};\n".format("true" if global_config.java_multiple_files() else "false"))
            self.content.append("option optimize_for = {};\n".format(global_config.optimize_for()))

        if self.language_type == global_config.language_type.cplus:
            self.content.append("option optimize_for = {};\n".format(global_config.optimize_for()))
            self.content.append(
                "option cc_enable_arenas = {};\n".format("true" if global_config.cc_enable_arenas() else "false"))

        if self.language_type == global_config.language_type.go:
            self.content.append("option go_package=\"./;{}\";".format(global_config.package_name()))

    def layout_struct_name(self, struct_name):
        self.content.append("\nmessage %s\n{\n" % struct_name)

    def layout_field(self):
        for column in self.columns:
            self.register_field(column)

        self.layout_nested()

    def register_field(self, column: Column):
        if len(column.path) > 1:
            self.register_nested(column)
            return

        self.content.append(self.field_line(column.rule, column.field_type, column.name,
                                             self.field_count, column.desc, "    "))
        self.field_count += 1

    def field_line(self, rule, field_type, field_name, field_number, desc, indent):
        if rule == "optional":
            return "{}{} {} = {}; //{}\n".format(indent, field_type, field_name, field_number, desc)
        elif rule == "repeated":
            return "{}repeated {} {} = {}; //{}\n".format(indent, field_type, field_name, field_number, desc)
        elif rule == "map":
            return "{}map<{}> {} = {}; //{}\n".format(indent, field_type, field_name, field_number, desc)
        else:
            sys.exit("Field Rule Error rule = {} name = {}".format(rule, field_name))

    def register_nested(self, column: Column):
        messages = self.nested
        for part in column.path[:-1]:
            node = messages.setdefault(part, {"leaves": [], "messages": {}})
            messages = node["messages"]
        node["leaves"].append((column.field_type, column.rule, column.desc, column.path[-1]))

    @staticmethod
    def nested_type_name(name):
        # 字段与其所属message内的嵌套类型共享命名空间 字段名必须与组名一致才能通过Monster.Base.Atk访问
        # 所以嵌套message类型名加Data后缀避免冲突
        return name + "Data"

    def layout_nested(self):
        for name, node in self.nested.items():
            self.content.append("    {} {} = {};\n".format(self.nested_type_name(name), name, self.field_count))
            self.field_count += 1
            self.layout_nested_message(name, node, 1)

    def layout_nested_message(self, name, node, depth):
        indent = "    " * depth
        field_indent = "    " * (depth + 1)
        self.content.append("\n{}message {}\n{}{{\n".format(indent, self.nested_type_name(name), indent))
        count = 1
        for field_type, rule, desc, field_name in node["leaves"]:
            self.content.append(self.field_line(rule, field_type, field_name, count, desc, field_indent))
            count += 1
        for sub_name in node["messages"]:
            self.content.append("{}{} {} = {};\n".format(field_indent, self.nested_type_name(sub_name), sub_name, count))
            count += 1
        for sub_name, sub_node in node["messages"].items():
            self.layout_nested_message(sub_name, sub_node, depth + 1)
        self.content.append("{}}}\n".format(indent))

    def layout_tail(self):
        self.content.append("}\n")

    def layout_list(self):
        self.content.append("\n")
        self.content.append("message {}List\n".format(self.sheet_name))
        self.content.append("{\n")
        self.content.append("    repeated {} list = 1;".format(self.sheet_name))
        self.content.append("\n}")

    def write_file(self):
        file = open(self.pb_name, "w+", encoding='utf-8')
        file.write("".join(self.content))
        file.close()

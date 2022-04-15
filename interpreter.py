import xlrd

import global_config


class interpreter:
    def __init__(self, file_path, sheet_name, language_type):
        self.content = []
        self.language_type = language_type
        self.sheet_name = sheet_name
        self.file_path = file_path

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

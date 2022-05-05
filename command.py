import os
import sys

import global_config


class command:

    @staticmethod
    def build_python_file(pb_file):
        command = "protoc.exe --python_out=./ " + pb_file
        print(command)
        os.system(command)

    @staticmethod
    def build_language_file(file_name, language_type):
        if language_type == global_config.language_type.java:
            command = "protoc.exe --java_out=./ " + file_name
        elif language_type == global_config.language_type.csharp:
            command = "protoc.exe --csharp_out=./ " + file_name
        elif language_type == global_config.language_type.cplus:
            command = "protoc.exe --cpp_out=./ " + file_name

        print(command)
        os.system(command)

    @staticmethod
    def load_moudle(pb_file):
        sys.path.append(os.getcwd())
        exec('from ' + pb_file + ' import *')

    @staticmethod
    def mkdir(folder_name):
        path = os.path.join(os.curdir + "/" + folder_name)
        if os.path.exists(path) is False:
            os.mkdir(path)
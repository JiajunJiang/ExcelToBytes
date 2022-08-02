import os
import sys
import platform
from importlib import reload

import global_config


class command:

    @staticmethod
    def build_python_file(pb_file):
        plat = platform.system().lower()
        if plat == 'windows':
            command = "protoc.exe --python_out=./ " + pb_file
        elif plat == 'linux':
            command = "linux/protoc --python_out=./ " + pb_file
        elif plat == 'darwin':
            command = "mac/protoc --python_out=./ " + pb_file

        print(command)
        os.system(command)

    @staticmethod
    def build_language_file(file_name, language_enum):
        plat = platform.system().lower()
        if plat == 'windows':
            file = "protoc.exe"
        elif plat == 'linux':
            file = "linux/protoc"
        elif plat == 'darwin':
            file = "mac/protoc"

        if language_enum == global_config.language_type.java:
            command = file + " --java_out=./ " + file_name
        elif language_enum == global_config.language_type.csharp:
            command = file + " --csharp_out=./ " + file_name
        elif language_enum == global_config.language_type.cplus:
            command = file + " --cpp_out=./ " + file_name
        elif language_enum == global_config.language_type.python:
            command = file + " --python_out=./ " + file_name
        elif language_enum == global_config.language_type.go:
            command = file + " --go_out=./ " + file_name
        elif language_enum == global_config.language_type.php:
            command = file + " --php_out=./ " + file_name
        elif language_enum == global_config.language_type.js:
            command = file + " --js_out=./ " + file_name
        elif language_enum == global_config.language_type.kotlin:
            command = file + " --kotlin_out=./ " + file_name
        elif language_enum == global_config.language_type.objc:
            command = file + " --objc_out=./ " + file_name
        else:
            print("Unknown Language Type OutPut Failed");
            raise

        print(command)
        os.system(command)

    @staticmethod
    def load_moudle(pb_file):
        sys.path.append(os.getcwd())
        exec('from ' + pb_file + ' import *')

        reload(sys.modules["google.protobuf.internal.builder"])
        reload(sys.modules["google.protobuf.descriptor"])
        reload(sys.modules["google.protobuf.descriptor_pool"])
        reload(sys.modules["google.protobuf.symbol_database"])

        reload(sys.modules[pb_file])

    @staticmethod
    def mkdir(folder_name):
        path = os.path.join(os.curdir + "/" + folder_name)
        if os.path.exists(path) is False:
            os.makedirs(path)

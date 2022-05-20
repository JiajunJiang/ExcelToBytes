import os
import sys
from importlib import reload

import global_config


class command:

    @staticmethod
    def build_python_file(pb_file):
        command = "protoc.exe --python_out=./ " + pb_file
        print(command)
        os.system(command)

    @staticmethod
    def build_language_file(file_name, language_enum):
        if language_enum == global_config.language_type.java:
            command = "protoc.exe --java_out=./ " + file_name
        elif language_enum == global_config.language_type.csharp:
            command = "protoc.exe --csharp_out=./ " + file_name
        elif language_enum == global_config.language_type.cplus:
            command = "protoc.exe --cpp_out=./ " + file_name
        elif language_enum == global_config.language_type.python:
            command = "protoc.exe --python_out=./ " + file_name
        elif language_enum == global_config.language_type.go:
            command = "protoc.exe --go_out=./ " + file_name
        elif language_enum == global_config.language_type.php:
            command = "protoc.exe --php_out=./ " + file_name
        elif language_enum == global_config.language_type.js:
            command = "protoc.exe --js_out=./ " + file_name
        elif language_enum == global_config.language_type.kotlin:
            command = "protoc.exe --kotlin_out=./ " + file_name
        elif language_enum == global_config.language_type.objc:
            command = "protoc.exe --objc_out=./ " + file_name
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

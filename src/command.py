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
        import importlib.util
        import sys

        # Clear protobuf internal state
        from google.protobuf import descriptor_pool, symbol_database
        descriptor_pool._DEFAULT = descriptor_pool.DescriptorPool()
        symbol_database._DEFAULT = symbol_database.SymbolDatabase()

        # Get the absolute path to the pb2 file
        pb_path = os.path.join(os.getcwd(), f"{pb_file}.py")

        # Use importlib to properly load the module
        spec = importlib.util.spec_from_file_location(pb_file, pb_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[pb_file] = module
        spec.loader.exec_module(module)

        return module

    @staticmethod
    def mkdir(folder_name):
        path = os.path.join(os.curdir + "/" + folder_name)
        if os.path.exists(path) is False:
            os.makedirs(path)

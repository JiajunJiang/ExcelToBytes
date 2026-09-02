import os
import platform
import subprocess

import global_config


class command:

    @staticmethod
    def build_python_file(pb_files):
        """pb_files: one proto file name or a list of them."""
        if isinstance(pb_files, str):
            pb_files = [pb_files]
        command.run_protoc(["--python_out=./"] + list(pb_files))

    @staticmethod
    def build_language_file(file_names, language_enum):
        if language_enum == global_config.language_type.java:
            out = "--java_out=./"
        elif language_enum == global_config.language_type.csharp:
            out = "--csharp_out=./"
        elif language_enum == global_config.language_type.cplus:
            out = "--cpp_out=./"
        elif language_enum == global_config.language_type.python:
            out = "--python_out=./"
        elif language_enum == global_config.language_type.go:
            out = "--go_out=./"
        elif language_enum == global_config.language_type.php:
            out = "--php_out=./"
        elif language_enum == global_config.language_type.js:
            out = "--js_out=./"
        elif language_enum == global_config.language_type.kotlin:
            out = "--kotlin_out=./"
        elif language_enum == global_config.language_type.objc:
            out = "--objc_out=./"
        else:
            print("Unknown Language Type OutPut Failed")
            raise ValueError("Unknown Language Type: {}".format(language_enum))

        if isinstance(file_names, str):
            file_names = [file_names]
        command.run_protoc([out] + list(file_names))

    @staticmethod
    def run_protoc(args):
        """Run the bundled protoc for this platform with an argv list and
        fail loudly on a non-zero exit (a failed compile used to be
        silently ignored and stale _pb2.py output was exported)."""
        plat = platform.system().lower()
        if plat == 'windows':
            file = "protoc.exe"
        elif plat == 'linux':
            file = os.path.join("linux", "protoc")
        elif plat == 'darwin':
            file = os.path.join("mac", "protoc")
        else:
            raise RuntimeError("Unsupported platform: {}".format(plat))

        cmd = [file] + args
        print(" ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("protoc failed ({}): {}".format(result.returncode, result.stderr))

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

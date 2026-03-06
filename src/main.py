# encoding:utf-8
import os
import sys
import xlrd
import importlib
from typing import List

import global_config
from archive import archive
from command import command
from interpreter import interpreter
from parse import ExcelToProtobufParser  # Updated import

# To resolve "TypeError: Couldn't build proto file into descriptor pool: duplicate file name xxx.proto",
# we have to set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION environment variable to "python".
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# Reload sys for Python 2 compatibility (though consider removing if using Python 3)
importlib.reload(sys)


def build_protobuf_from_excel(language: str, flag: str, excel_file: str) -> None:
    """
    Build protobuf files from Excel sheets.

    Args:
        language: Target language for protobuf generation
        flag: Language flag (c for client, s for server)
        excel_file: Path to Excel file
    """
    try:
        workbook = xlrd.open_workbook(excel_file)
    except Exception as e:
        raise RuntimeError(f"Failed to open Excel file {excel_file}: {str(e)}")

    for sheet in workbook.sheets():
        if "Sheet" in sheet.name or "#" in sheet.name:
            continue

        print(f"Processing sheet: {sheet.name}")

        try:
            # Process each sheet through the pipeline
            interpreter(excel_file, sheet.name, language, flag)
            ExcelToProtobufParser(excel_file, sheet.name, language, flag)  # Updated to use new class

            # Generate language-specific files
            command.build_language_file(f"{sheet.name}.proto", language)

            # Archive the results
            archive(language, flag)

            print(f"Successfully processed {sheet.name}")
        except Exception as e:
            print(f"Error processing sheet {sheet.name}: {str(e)}")
            raise


def load_config_files() -> List[str]:
    """Find and load all YAML config files in current directory."""
    return [f for f in os.listdir(os.getcwd()) if f.endswith(".yml")]


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python script.py <excel_file>")

    excel_file = sys.argv[1]

    try:
        # Process each config file
        for config_file in load_config_files():
            global_config.load(config_file)
            print("Starting build process")

            language = global_config.language_type(global_config.language())
            flag = str(global_config.language_flag())

            print(f"Building with flag: {flag}")
            build_protobuf_from_excel(language, flag, excel_file)

    except Exception as e:
        print(f"Build failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
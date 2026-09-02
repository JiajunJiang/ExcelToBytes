# encoding:utf-8
import os
import sys
import xlrd
from typing import List

import global_config
from archive import archive
from command import command
from interpreter import interpreter
from parse import ExcelToProtobufParser


def build_protobuf_from_excel(workbook, language: str, flag: str) -> None:
    """
    Build protobuf files from Excel sheets.

    Args:
        workbook: The already-opened xlrd workbook (opened once for all
            sheets instead of once per sheet per stage).
        language: Target language for protobuf generation
        flag: Language flag (c for client, s for server)
    """
    sheets = [sheet for sheet in workbook.sheets()
              if "Sheet" not in sheet.name and "#" not in sheet.name]
    if not sheets:
        return

    # Stage 1: write a .proto file for every sheet (pure in-process work)
    proto_files = []
    for sheet in sheets:
        print(f"Processing sheet: {sheet.name}")
        interpreter(workbook, sheet.name, language, flag)
        proto_files.append(f"{sheet.name}.proto")

    # Stage 2: one protoc run compiles the python bindings for all sheets
    command.build_python_file(proto_files)

    # Stage 3: serialize each sheet's data through its _pb2 module
    for sheet in sheets:
        ExcelToProtobufParser(workbook, sheet.name, language, flag)
        print(f"Successfully processed {sheet.name}")

    # Stage 4: one protoc run generates the target-language output for all
    # sheets (protoc accepts multiple input files; one process per sheet
    # was slow)
    command.build_language_file(proto_files, language)

    # Archive the results once, after every sheet is done
    archive(language, flag)


def load_config_files() -> List[str]:
    """Find and load all YAML config files in current directory."""
    return [f for f in os.listdir(os.getcwd()) if f.endswith(".yml")]


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python script.py <excel_file>")

    excel_file = sys.argv[1]

    try:
        # Open the workbook once and share it across all sheets and stages
        workbook = xlrd.open_workbook(excel_file)

        # Process each config file
        for config_file in load_config_files():
            global_config.load(config_file)
            print("Starting build process")

            language = global_config.language_type(global_config.language())
            flag = str(global_config.language_flag())

            print(f"Building with flag: {flag}")
            build_protobuf_from_excel(workbook, language, flag)

    except Exception as e:
        print(f"Build failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

# encoding:utf-8
import os
import sys
import xlrd
from glob import glob
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


def is_flag(arg: str) -> bool:
    return len(arg) > 0 and set(arg.lower()) <= set('cs')


def collect_excel_file(paths: List[str]) -> List[str]:
    """Expand file args and folder args into a deduplicated xlsx list.

    Folders are scanned non-recursively; Excel lock files (~$foo.xlsx) are
    skipped and a warning is printed for inputs that contain no xlsx.
    """
    excel_files = []
    for path in paths:
        if os.path.isdir(path):
            folder_files = glob(os.path.join(path, '*.xlsx')) + glob(os.path.join(path, '*.XLSX'))
            folder_files = sorted(set(folder_files))
            if len(folder_files) == 0:
                print("Warning: no xlsx file in folder %s" % path)
            for file in folder_files:
                if os.path.basename(file).startswith('~$'):
                    continue
                excel_files.append(file)
        elif path.lower().endswith('.xlsx'):
            excel_files.append(path)
        else:
            print("Warning: skip not xlsx file %s" % path)
    return excel_files


def build_all(excel_files: List[str], flag: str) -> List[str]:
    """Build every collected xlsx through every config file, isolating
    per-file failures so one bad sheet doesn't abort the whole batch.

    The command-line flag (default 'cs') selects which config files run:
    a config runs when its language_flag overlaps the requested flag, so
    'py main.py A.xlsx c' only runs the client-oriented yml configs.
    """
    failed_files = []
    for excel_file in excel_files:
        try:
            # Open the workbook once and share it across all sheets and stages
            workbook = xlrd.open_workbook(excel_file)

            # Process each config file
            for config_file in load_config_files():
                global_config.load(config_file)
                config_flag = str(global_config.language_flag())

                if not (set(config_flag) & set(flag)):
                    print(f"Skip config {config_file} (flag {config_flag}, requested {flag})")
                    continue

                print("Starting build process")

                language = global_config.language_type(global_config.language())

                print(f"Building with flag: {config_flag}")
                build_protobuf_from_excel(workbook, language, config_flag)
        except Exception as e:
            print(f"Build File({excel_file}) Failed: {e}")
            failed_files.append(excel_file)
    return failed_files


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python main.py <excel_file_or_folder> [more files/folders] [c|s|cs]")

    # argv 1..N = Excel file paths or folder paths, optionally mixed with a
    # c/s/cs flag anywhere in the list (filters which config files run)
    flag = 'cs'
    paths = []
    for arg in sys.argv[1:]:
        if os.path.exists(arg):
            paths.append(arg)
        elif is_flag(arg):
            flag = arg.lower()
        else:
            sys.exit("path not exist or unknown flag %s" % arg)

    excel_files = collect_excel_file(paths)
    if len(excel_files) == 0:
        sys.exit("no excel file found")

    print("Build Excel Count = %d" % len(excel_files))

    failed_files = build_all(excel_files, flag)

    if len(failed_files) > 0:
        for excel_file in failed_files:
            print(f"Build Failed: {excel_file}")
        sys.exit(f"Build Finish {len(failed_files)} Failed")
    print("Build Finish All Success")


if __name__ == '__main__':
    main()

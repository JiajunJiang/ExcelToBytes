# encoding:utf-8

import sys
import xlrd
import global_config
from command import command
from typing import Any, Dict, List, Union, Optional

# Constants for row indices
FIELD_RULE_ROW = 0  # optional or repeated
FIELD_TYPE_ROW = 1  # protobuf type
FIELD_NAME_ROW = 2  # field name
FIELD_DESC_ROW = 3  # description
FIELD_FLAG_ROW = 4  # language flag
FIELD_VALUE_ROW = 5  # value

# Type aliases
FieldValue = Union[int, float, bool, str, bytes]
NumericTypes = {'int32', 'int64', 'uint32', 'uint64', 'sint32', 'sint64',
                'fixed32', 'fixed64', 'sfixed32', 'sfixed64'}
FloatTypes = {'float', 'double'}


class ExcelToProtobufParser:
    def __init__(self, file_path: str, sheet_name: str, language_type: str, flag: str):
        self.module = None
        self.pb_file = f"{sheet_name}_pb2"
        self.flag = flag
        self.language_type = language_type
        self.sheet_name = sheet_name
        self.file_path = file_path

        try:
            self.work_book = xlrd.open_workbook(self.file_path)
            self.sheet = self.work_book.sheet_by_name(self.sheet_name)
        except Exception as e:
            raise RuntimeError(f"Failed to open file {self.file_path} or sheet {self.sheet_name}: {str(e)}")

        self.row_count = len(self.sheet.col_values(0))
        self.col_count = len(self.sheet.row_values(0))

        self._load_module()
        self._process_sheet()

    def _load_module(self) -> None:
        """Dynamically load the protobuf module."""
        try:
            command.load_moudle(self.pb_file)
            self.module = sys.modules[self.pb_file]
        except Exception as e:
            raise RuntimeError(f"Failed to load module {self.pb_file}: {str(e)}")

    def _process_sheet(self) -> None:
        """Process the entire Excel sheet and generate protobuf output."""
        array_list = getattr(self.module, f"{self.sheet_name}List")()

        for row_idx in range(FIELD_VALUE_ROW, self.row_count):
            if not self._is_comment_row(row_idx):
                item = array_list.list.add()
                self._parse_row_to_item(row_idx, item)

        self._save_output(array_list.SerializeToString())

        if global_config.save_log():
            self._save_log(str(array_list))

    def _parse_row_to_item(self, row_idx: int, item: Any) -> None:
        """Parse a single row into a protobuf item."""
        for col_idx in range(self.col_count):
            if self._is_column_enabled(col_idx):
                self._parse_field(row_idx, col_idx, item)

    def _is_comment_row(self, row_idx: int) -> bool:
        """Check if a row is commented out (starts with #)."""
        return str(self.sheet.cell_value(row_idx, 0)).startswith("#")

    def _is_column_enabled(self, col_idx: int) -> bool:
        """Check if a column is enabled for the current language flag."""
        flag_value = str(self.sheet.cell_value(FIELD_FLAG_ROW, col_idx)).strip()
        return self.flag in flag_value

    def _parse_field(self, row_idx: int, col_idx: int, item: Any) -> None:
        """Parse a single field based on its rule type."""
        field_type = str(self.sheet.cell_value(FIELD_TYPE_ROW, col_idx))
        rule = str(self.sheet.cell_value(FIELD_RULE_ROW, col_idx)).lower()
        field_name = str(self.sheet.cell_value(FIELD_NAME_ROW, col_idx))
        field_value = self.sheet.cell_value(row_idx, col_idx)

        if rule == "optional":
            self._set_optional_field(field_type, field_name, field_value, item)
        elif rule == "repeated":
            self._set_repeated_field(field_type, field_name, field_value, item)
        elif rule == "map":
            self._set_map_field(field_type, field_name, field_value, item)
        else:
            raise ValueError(f"Unknown field rule: {rule}")

    def _set_optional_field(self, field_type: str, field_name: str, field_value: Any, item: Any) -> None:
        """Set an optional field value."""
        parsed_value = self._parse_field_value(field_type, field_value)
        if parsed_value is not None:
            item.__setattr__(field_name, parsed_value)

    def _set_repeated_field(self, field_type: str, field_name: str, field_value: Any, item: Any) -> None:
        """Set a repeated field value."""
        if not str(field_value):
            return

        values = str(field_value).split(';') if ";" in str(field_value) else [field_value]

        for value in values:
            if str(value):
                parsed_value = self._parse_field_value(field_type, value)
                if parsed_value is not None:
                    item.__getattribute__(field_name).append(parsed_value)

    def _set_map_field(self, field_type: str, field_name: str, field_value: Any, item: Any) -> None:
        """Set a map field value."""
        if not str(field_value):
            return

        key_type, value_type = self._parse_map_types(field_type)
        pairs = str(field_value).split(';')

        for pair in pairs:
            if pair:
                key, value = self._parse_map_pair(pair, key_type, value_type)
                item.__getattribute__(field_name).__setitem__(key, value)

    def _parse_map_types(self, field_type: str) -> tuple[str, str]:
        """Parse key and value types from a map field type."""
        types = field_type.split(',')
        if len(types) != 2:
            raise ValueError(f"Invalid map field type format: {field_type}")
        return types[0].strip(), types[1].strip()

    def _parse_map_pair(self, pair: str, key_type: str, value_type: str) -> tuple[Any, Any]:
        """Parse a key-value pair for a map field."""
        parts = pair.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid map pair format: {pair}")
        return (
            self._parse_field_value(key_type, parts[0]),
            self._parse_field_value(value_type, parts[1])
        )

    def _parse_field_value(self, field_type: str, value: Any) -> Optional[FieldValue]:
        """Parse a field value according to its type."""
        str_value = str(value).strip()

        if field_type in NumericTypes:
            return int(float(str_value)) if str_value else 0
        elif field_type in FloatTypes:
            return float(str_value) if str_value else 0.0
        elif field_type == "bool":
            return bool(int(float(str_value))) if str_value else False
        elif field_type == "string":
            return str_value.encode("utf8")
        else:
            raise ValueError(f"Unsupported field type: {field_type}")

    def _save_output(self, data: bytes) -> None:
        """Save the serialized protobuf data to file."""
        output_file = f"{self.sheet_name}{global_config.file_ext()}"
        try:
            with open(output_file, 'wb') as f:
                f.write(data)
        except IOError as e:
            raise RuntimeError(f"Failed to write output file {output_file}: {str(e)}")

    def _save_log(self, data: str) -> None:
        """Save a log file with human-readable output."""
        log_file = f"{self.sheet_name}.log"
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(data)
        except IOError as e:
            raise RuntimeError(f"Failed to write log file {log_file}: {str(e)}")
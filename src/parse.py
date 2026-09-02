# encoding:utf-8

import re
import sys
from typing import Any, List, Optional, Union

import global_config
from command import command
from schema import (Column, FIELD_VALUE_ROW, FloatTypes, NumericTypes,
                    read_columns)

FieldValue = Union[int, float, bool, str, bytes]

# map 键值对 "key-value" 的分隔符是第一个不属于 key 的 '-'。
# key 为数值类型时,先匹配可选符号开头的数字,其后的 '-' 才是分隔符,
# 这样 "10--20"(负值)、"-5-10"(负键)、"-5--20"(双负)都能正确切分。
NUMERIC_KEY_PAIR_RE = re.compile(r"^([+-]?(?:\d+\.?\d*|\.\d+))\s*-\s*(.*)$")

# 每对数据在切分前先整体 strip,兼容 " 12 - 24 " 这类带空格的写法
PAIR_SPLIT_RE = re.compile(r"\s*;\s*")


class ExcelToProtobufParser:
    def __init__(self, work_book, sheet_name: str, language_type: str, flag: str):
        self.pb_file = f"{sheet_name}_pb2"
        self.flag = flag
        self.language_type = language_type
        self.sheet_name = sheet_name

        self.sheet = work_book.sheet_by_name(sheet_name)
        self.columns: List[Column] = read_columns(self.sheet, self.flag)

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

        add = array_list.list.add
        rows = self.sheet._cell_values
        row_count = self.sheet.nrows
        columns = self.columns

        for row_idx in range(FIELD_VALUE_ROW, row_count):
            row = rows[row_idx]
            if str(row[0]).startswith("#"):
                continue
            item = add()
            for column in columns:
                value = row[column.index]
                rule = column.rule
                field_name = column.path[-1]
                if len(column.path) > 1:
                    target = self._resolve_target(item, column.path)
                else:
                    target = item

                if rule == "optional":
                    self._set_optional_field(column.field_type, field_name, value, target)
                elif rule == "repeated":
                    self._set_repeated_field(column.field_type, field_name, value, target)
                else:
                    self._set_map_field(column.field_type, field_name, value, target)

        self._save_output(array_list.SerializeToString())

        if global_config.save_log():
            self._save_log(str(array_list))

    def _resolve_target(self, item: Any, path: tuple) -> Any:
        """Walk the nested-message path (Base.HP -> item.Base)."""
        for part in path[:-1]:
            item = getattr(item, part)
        return item

    def _set_optional_field(self, field_type: str, field_name: str, field_value: Any, item: Any) -> None:
        """Set an optional field value."""
        parsed_value = self._parse_field_value(field_type, field_value)
        if parsed_value is not None:
            setattr(item, field_name, parsed_value)

    def _set_repeated_field(self, field_type: str, field_name: str, field_value: Any, item: Any) -> None:
        """Set a repeated field value."""
        if not str(field_value):
            return

        values = str(field_value).split(';') if ";" in str(field_value) else [field_value]

        for value in values:
            if str(value):
                parsed_value = self._parse_field_value(field_type, value)
                if parsed_value is not None:
                    getattr(item, field_name).append(parsed_value)

    def _set_map_field(self, field_type: str, field_name: str, field_value: Any, item: Any) -> None:
        """Set a map field value."""
        if not str(field_value):
            return

        key_type, value_type = self._parse_map_types(field_type)
        pairs = str(field_value).split(';')

        for pair in pairs:
            if pair:
                key, value = self._parse_map_pair(pair, key_type, value_type)
                getattr(item, field_name)[key] = value

    def _parse_map_types(self, field_type: str) -> tuple[str, str]:
        """Parse key and value types from a map field type."""
        types = field_type.split(',')
        if len(types) != 2:
            raise ValueError(f"Invalid map field type format: {field_type}")
        return types[0].strip(), types[1].strip()

    def _parse_map_pair(self, pair: str, key_type: str, value_type: str) -> tuple[Any, Any]:
        """Parse a key-value pair for a map field.

        Pairs are separated by ';', a key from its value by the FIRST '-'.
        Splitting on the first '-' only is what makes negative numbers
        unambiguous: "10--20" -> key 10, value -20; "-5-10" -> key -5,
        value 10. The old str.split('-') could not express either form.
        """
        pair = pair.strip()
        if key_type in NumericTypes or key_type in FloatTypes or key_type == "bool":
            # Numeric key: the separator is the '-' right after the leading
            # number, so negative keys and values both parse correctly.
            match = NUMERIC_KEY_PAIR_RE.match(pair)
            if not match:
                raise ValueError(f"Invalid map pair format: {pair}")
            key_str, value_str = match.group(1), match.group(2)
        else:
            parts = pair.split('-', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid map pair format: {pair}")
            key_str, value_str = parts
        return (
            self._parse_field_value(key_type, key_str),
            self._parse_field_value(value_type, value_str)
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

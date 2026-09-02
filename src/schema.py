# encoding:utf-8

"""Shared sheet-schema extraction.

The five header rows are read exactly once per sheet; both the .proto
generator (interpreter) and the data exporter (parse) consume the resulting
Column list instead of re-reading the header cells for every data cell.
"""

from typing import List, NamedTuple, Tuple

# Row indices of the header area
FIELD_RULE_ROW = 0   # optional / repeated / map
FIELD_TYPE_ROW = 1   # protobuf type, "key,value" for map fields
FIELD_NAME_ROW = 2   # field name; dots mark nested groups
FIELD_DESC_ROW = 3   # free-form description
FIELD_FLAG_ROW = 4   # c / s / cs export flag
FIELD_VALUE_ROW = 5  # first data row

# Scalar protobuf types accepted in the type row
SUPPORTED_TYPES = frozenset((
    "int32", "int64", "uint32", "uint64", "sint32", "sint64",
    "fixed32", "fixed64", "sfixed32", "sfixed64",
    "float", "double", "bool", "string",
))

NumericTypes = frozenset((
    "int32", "int64", "uint32", "uint64", "sint32", "sint64",
    "fixed32", "fixed64", "sfixed32", "sfixed64",
))
FloatTypes = frozenset(("float", "double"))

RULES = frozenset(("optional", "repeated", "map"))


class Column(NamedTuple):
    index: int              # sheet column index
    rule: str               # optional / repeated / map
    field_type: str         # protobuf type; "key,value" for map
    name: str               # original name cell, for error messages
    desc: str               # description cell
    path: Tuple[str, ...]   # name split on "."; length 1 for a plain field


def validate_field_type(field_type: str) -> bool:
    """True if the type cell is a valid scalar type or a "key,value" pair."""
    if "," in field_type:
        types = [t.strip() for t in field_type.split(",")]
        return len(types) == 2 and all(t in SUPPORTED_TYPES for t in types)
    return field_type in SUPPORTED_TYPES


def read_columns(sheet, flag: str) -> List[Column]:
    """Scan the header rows once and return one Column per flag-enabled
    column, in sheet order. Raises ValueError for malformed headers."""
    columns = []
    for col in range(sheet.ncols):
        flag_value = str(sheet.cell_value(FIELD_FLAG_ROW, col)).strip()
        if flag not in flag_value:
            continue

        rule = str(sheet.cell_value(FIELD_RULE_ROW, col)).strip().lower()
        field_type = str(sheet.cell_value(FIELD_TYPE_ROW, col)).strip()
        name = str(sheet.cell_value(FIELD_NAME_ROW, col)).strip()
        desc = str(sheet.cell_value(FIELD_DESC_ROW, col))
        path = tuple(part.strip() for part in name.split("."))

        if not validate_field_type(field_type):
            raise ValueError("Error Field Type Col = {} name = {}".format(col, name))
        if rule not in RULES:
            raise ValueError("Field Rule Error rule = {} name = {}".format(rule, name))
        if not all(path):
            raise ValueError("Nested Field Name Error name = {}".format(name))

        columns.append(Column(col, rule, field_type, name, desc, path))
    return columns

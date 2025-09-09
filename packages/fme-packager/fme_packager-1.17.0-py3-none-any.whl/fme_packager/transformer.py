"""
Tools for extracting key information out of FME's transformer definition files.
"""

import json
import os.path
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, List
import csv
from io import StringIO


def parse_data_processing_type(data_processing_type: dict):
    """
    Parse data processing type from conditional logic dictionary.

    :param data_processing_type: The data processing type dict with conditional logic
    :return: List of data processing types
    """
    types = set()

    # Extract all "then" values from conditional statements
    if_conditions = data_processing_type.get("if", [])
    for condition in if_conditions:
        then_value = condition.get("then")
        if then_value:
            types.add(then_value)

    # Add default value if present
    default_value = data_processing_type.get("default")
    if default_value:
        types.add(default_value)

    return sorted(list(types))


def csv_split(line: str) -> List[str]:
    """
    Split a CSV line into a list of values, handling quoted strings.

    :param line: The CSV line to split.
    :return: List of values from the CSV line.
    """
    try:
        return next(csv.reader(StringIO(line.strip())))
    except StopIteration:
        return []


class Transformer(ABC):
    """Represents one version of a transformer."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> int:
        pass

    @property
    @abstractmethod
    def python_compatibility(self) -> str:
        pass

    @property
    @abstractmethod
    def categories(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def aliases(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def visible(self) -> bool:
        pass

    @property
    @abstractmethod
    def data_processing_types(self) -> List[str]:
        pass


@dataclass
class CustomTransformerHeader:
    name: str
    version: int
    category: List[str]
    guid: str
    insert_mode: str
    blocked_looping: str
    process_count: str
    process_group_by: str
    process_groups_ordered: str
    build_num: int
    preserves_attrs: str
    deprecated: bool
    pyver: str
    preserve_group_attr: str = ""
    replaced_by: str = ""
    data_processing_type: List[str] = field(default_factory=list)

    # noinspection PyUnreachableCode
    def __post_init__(self):
        if not isinstance(self.version, int):
            self.version = int(self.version)
        if not isinstance(self.build_num, int):
            self.build_num = int(self.build_num)
        if isinstance(self.category, str):
            self.category = csv_split(self.category)
        if isinstance(self.deprecated, str):
            self.deprecated = self.deprecated.lower() == "yes"
        if isinstance(self.data_processing_type, str):
            self.data_processing_type = self.data_processing_type.split()


def parse_custom_transformer_header(line: str) -> CustomTransformerHeader:
    """
    Parses custom transformer header.

    :param line: Custom transformer header line from FMX.
    :return: Parsed header
    """
    fields = csv_split(line.replace("# TRANSFORMER_BEGIN", ""))
    return CustomTransformerHeader(*fields)


class CustomTransformer(Transformer):
    def __init__(self, lines: List[bytes]):
        super().__init__()
        self.header: CustomTransformerHeader
        self.lines = lines
        for line in lines:
            if line.startswith(b"# TRANSFORMER_BEGIN"):
                self.header = parse_custom_transformer_header(line.decode("utf8"))
                break
        else:
            raise ValueError("TRANSFORMER_BEGIN line not found")

    @property
    def name(self):
        return self.header.name

    @property
    def version(self):
        return self.header.version

    @property
    def python_compatibility(self):
        return self.header.pyver

    @property
    def categories(self):
        return self.header.category

    @property
    def aliases(self):
        return []

    @property
    def visible(self):
        return not self.header.deprecated

    @property
    def data_processing_types(self):
        return self.header.data_processing_type

    @property
    def is_encrypted(self):
        return self.lines[0].strip() == b"FMW0001"


class FmxTransformer(Transformer):
    def __init__(self, lines):
        super().__init__()
        self.lines = lines
        self.props = {}
        for line in self.lines:
            match = re.match(r"^(.+?):\s+(.+?)$", line)
            if match:
                name = match.group(1).strip()
                if name.startswith("PARAMETER_"):
                    continue
                self.props[name] = match.group(2).strip()
        if self.name is None or self.version is None:
            raise ValueError("TRANSFORMER_NAME or VERSION not found")

    @property
    def name(self):
        return self.props.get("TRANSFORMER_NAME")

    @property
    def version(self):
        return int(self.props.get("VERSION"))

    @property
    def python_compatibility(self):
        return self.props.get("PYTHON_COMPATIBILITY")

    def _split_prop(self, property_name, sep=","):
        return (
            [p.strip() for p in self.props.get(property_name).split(sep)]
            if self.props.get(property_name)
            else []
        )

    @property
    def categories(self):
        return self._split_prop("CATEGORY", ",")

    @property
    def aliases(self):
        return self._split_prop("ALIASES", " ")

    @property
    def visible(self):
        return self.props.get("VISIBLE", "yes").lower() == "yes"

    @property
    def data_processing_types(self):
        data_processing_type = self.props.get("DATA_PROCESSING_TYPE")
        if not data_processing_type:
            return []

        data_processing_type = data_processing_type.strip()

        # Try to parse as JSON first
        try:
            parsed_data = json.loads(data_processing_type)
            return parse_data_processing_type(parsed_data)
        except json.JSONDecodeError:
            pass

        # If JSON parsing fails, treat as simple string
        return [data_processing_type]


class FmxjTransformer(Transformer):
    def __init__(self, info, version_def):
        self.info = info
        self.json_def = version_def

    @property
    def name(self):
        return self.info["name"]

    @property
    def version(self):
        return self.json_def["version"]

    @property
    def python_compatibility(self):
        # FIXME: key typo from tstportConfiguration/testdata/PortConfiguration.fmxj
        return self.json_def.get("pythonCompatability")

    @property
    def categories(self):
        return self.info.get("categories", [])

    @property
    def aliases(self):
        return self.info.get("aliases", [])

    @property
    def visible(self):
        return not self.info.get("deprecated", False)

    @property
    def data_processing_types(self):
        data_processing_type = self.json_def.get("dataProcessingType")
        if not data_processing_type:
            return []

        # Handle simple string case
        if isinstance(data_processing_type, str):
            return [data_processing_type]

        # Handle conditional logic case
        if isinstance(data_processing_type, dict):
            return parse_data_processing_type(data_processing_type)

        return []


class TransformerFile(ABC):
    """Represents a transformer file containing one or more transformer versions."""

    def __init__(self, file_path):
        self.file_path = file_path

    @abstractmethod
    def versions(self) -> Iterable[Transformer]:
        pass


def get_matching_indexes(lines, matcher):
    """
    Returns indexes of lines where line is (or can be decoded as) UTF-8 and matcher function is true.
    """
    indexes = []
    for i, line in enumerate(lines):
        if not isinstance(line, str):
            try:
                line = line.decode("utf8")
            except (UnicodeDecodeError, AttributeError):
                continue
        if matcher(line):
            indexes.append(i)
    return indexes


class FmxFile(TransformerFile):
    def __init__(self, file_path):
        super().__init__(file_path)

    def versions(self):
        with open(self.file_path, "r") as f:
            lines = f.readlines()
        transformer_begin_indexes = get_matching_indexes(
            lines, lambda l: l.startswith("TRANSFORMER_NAME")
        )
        for def_num, i in enumerate(transformer_begin_indexes):
            if i == transformer_begin_indexes[-1]:
                end_idx = len(lines) - 1
            else:
                end_idx = transformer_begin_indexes[def_num + 1] - 1
            yield FmxTransformer(lines[i:end_idx])


class CustomTransformerFmxFile(TransformerFile):
    def __init__(self, file_path):
        super().__init__(file_path)

    def versions(self):
        with open(self.file_path, "rb") as f:
            lines = f.readlines()
        transformer_begin_indexes = get_matching_indexes(
            lines, lambda l: l.startswith("# TRANSFORMER_BEGIN")
        )
        for def_num, i in enumerate(transformer_begin_indexes):
            if i == transformer_begin_indexes[-1]:
                end_idx = len(lines) - 1
            else:
                end_idx = transformer_begin_indexes[def_num + 1] - 2
            yield CustomTransformer(lines[i - 1 : end_idx])


class FmxjFile(TransformerFile):
    def __init__(self, file_path):
        super().__init__(file_path)
        with open(file_path) as f:
            self.body = json.load(f)

    def versions(self):
        for item in self.body["versions"]:
            yield FmxjTransformer(self.body["info"], item)


def load_transformer(transformer_path) -> TransformerFile:
    filename, ext = os.path.splitext(transformer_path)
    ext = ext.lower()
    if ext == ".fmx":
        # Check first line for Custom Transformer text
        with open(transformer_path, "rb") as f:
            line = f.readline()
        if line.startswith(b"#!") or line.startswith(b"FMW0001"):
            return CustomTransformerFmxFile(transformer_path)
        return FmxFile(transformer_path)
    if ext == ".fmxj":
        return FmxjFile(transformer_path)
    raise ValueError(f"Unrecognized transformer: {transformer_path}")

from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LineWeldedJointConfiguration(_message.Message):
    __slots__ = ("assigned_to_line_welded_joints", "comment", "name", "no", "user_defined_name_enabled", "special_settings", "id_for_export_import", "metadata_for_export_import")
    class SpecialSettingsTreeTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[LineWeldedJointConfiguration.SpecialSettingsTreeTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[LineWeldedJointConfiguration.SpecialSettingsTreeTableRow, _Mapping]]] = ...) -> None: ...
    class SpecialSettingsTreeTableRow(_message.Message):
        __slots__ = ("key", "caption", "symbol", "value", "unit", "children")
        KEY_FIELD_NUMBER: _ClassVar[int]
        CAPTION_FIELD_NUMBER: _ClassVar[int]
        SYMBOL_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        UNIT_FIELD_NUMBER: _ClassVar[int]
        CHILDREN_FIELD_NUMBER: _ClassVar[int]
        key: str
        caption: str
        symbol: str
        value: _common_pb2.Value
        unit: str
        children: _containers.RepeatedCompositeFieldContainer[LineWeldedJointConfiguration.SpecialSettingsTreeTableRow]
        def __init__(self, key: _Optional[str] = ..., caption: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., unit: _Optional[str] = ..., children: _Optional[_Iterable[_Union[LineWeldedJointConfiguration.SpecialSettingsTreeTableRow, _Mapping]]] = ...) -> None: ...
    ASSIGNED_TO_LINE_WELDED_JOINTS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SPECIAL_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_to_line_welded_joints: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    name: str
    no: int
    user_defined_name_enabled: bool
    special_settings: LineWeldedJointConfiguration.SpecialSettingsTreeTable
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_to_line_welded_joints: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., special_settings: _Optional[_Union[LineWeldedJointConfiguration.SpecialSettingsTreeTable, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConcreteDesignConfiguration(_message.Message):
    __slots__ = ("assigned_to_single_foundations", "comment", "name", "no", "user_defined_name_enabled", "settings_ec7", "id_for_export_import", "metadata_for_export_import")
    class SettingsEc7TreeTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[ConcreteDesignConfiguration.SettingsEc7TreeTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[ConcreteDesignConfiguration.SettingsEc7TreeTableRow, _Mapping]]] = ...) -> None: ...
    class SettingsEc7TreeTableRow(_message.Message):
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
        children: _containers.RepeatedCompositeFieldContainer[ConcreteDesignConfiguration.SettingsEc7TreeTableRow]
        def __init__(self, key: _Optional[str] = ..., caption: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., unit: _Optional[str] = ..., children: _Optional[_Iterable[_Union[ConcreteDesignConfiguration.SettingsEc7TreeTableRow, _Mapping]]] = ...) -> None: ...
    ASSIGNED_TO_SINGLE_FOUNDATIONS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_EC7_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_to_single_foundations: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    name: str
    no: int
    user_defined_name_enabled: bool
    settings_ec7: ConcreteDesignConfiguration.SettingsEc7TreeTable
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_to_single_foundations: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., settings_ec7: _Optional[_Union[ConcreteDesignConfiguration.SettingsEc7TreeTable, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

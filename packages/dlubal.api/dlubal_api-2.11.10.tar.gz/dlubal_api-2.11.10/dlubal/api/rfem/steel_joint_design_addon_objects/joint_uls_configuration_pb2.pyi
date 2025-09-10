from dlubal.api.common import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JointUlsConfiguration(_message.Message):
    __slots__ = ("assigned_to_joints", "comment", "name", "no", "user_defined_name_enabled", "settings_aisc", "settings_csa", "settings_ec3", "id_for_export_import", "metadata_for_export_import")
    class SettingsAiscTreeTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[JointUlsConfiguration.SettingsAiscTreeTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[JointUlsConfiguration.SettingsAiscTreeTableRow, _Mapping]]] = ...) -> None: ...
    class SettingsAiscTreeTableRow(_message.Message):
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
        children: _containers.RepeatedCompositeFieldContainer[JointUlsConfiguration.SettingsAiscTreeTableRow]
        def __init__(self, key: _Optional[str] = ..., caption: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., unit: _Optional[str] = ..., children: _Optional[_Iterable[_Union[JointUlsConfiguration.SettingsAiscTreeTableRow, _Mapping]]] = ...) -> None: ...
    class SettingsCsaTreeTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[JointUlsConfiguration.SettingsCsaTreeTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[JointUlsConfiguration.SettingsCsaTreeTableRow, _Mapping]]] = ...) -> None: ...
    class SettingsCsaTreeTableRow(_message.Message):
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
        children: _containers.RepeatedCompositeFieldContainer[JointUlsConfiguration.SettingsCsaTreeTableRow]
        def __init__(self, key: _Optional[str] = ..., caption: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., unit: _Optional[str] = ..., children: _Optional[_Iterable[_Union[JointUlsConfiguration.SettingsCsaTreeTableRow, _Mapping]]] = ...) -> None: ...
    class SettingsEc3TreeTable(_message.Message):
        __slots__ = ("rows",)
        ROWS_FIELD_NUMBER: _ClassVar[int]
        rows: _containers.RepeatedCompositeFieldContainer[JointUlsConfiguration.SettingsEc3TreeTableRow]
        def __init__(self, rows: _Optional[_Iterable[_Union[JointUlsConfiguration.SettingsEc3TreeTableRow, _Mapping]]] = ...) -> None: ...
    class SettingsEc3TreeTableRow(_message.Message):
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
        children: _containers.RepeatedCompositeFieldContainer[JointUlsConfiguration.SettingsEc3TreeTableRow]
        def __init__(self, key: _Optional[str] = ..., caption: _Optional[str] = ..., symbol: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Value, _Mapping]] = ..., unit: _Optional[str] = ..., children: _Optional[_Iterable[_Union[JointUlsConfiguration.SettingsEc3TreeTableRow, _Mapping]]] = ...) -> None: ...
    ASSIGNED_TO_JOINTS_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NO_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_NAME_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_AISC_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_CSA_FIELD_NUMBER: _ClassVar[int]
    SETTINGS_EC3_FIELD_NUMBER: _ClassVar[int]
    ID_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FOR_EXPORT_IMPORT_FIELD_NUMBER: _ClassVar[int]
    assigned_to_joints: _containers.RepeatedScalarFieldContainer[int]
    comment: str
    name: str
    no: int
    user_defined_name_enabled: bool
    settings_aisc: JointUlsConfiguration.SettingsAiscTreeTable
    settings_csa: JointUlsConfiguration.SettingsCsaTreeTable
    settings_ec3: JointUlsConfiguration.SettingsEc3TreeTable
    id_for_export_import: str
    metadata_for_export_import: str
    def __init__(self, assigned_to_joints: _Optional[_Iterable[int]] = ..., comment: _Optional[str] = ..., name: _Optional[str] = ..., no: _Optional[int] = ..., user_defined_name_enabled: bool = ..., settings_aisc: _Optional[_Union[JointUlsConfiguration.SettingsAiscTreeTable, _Mapping]] = ..., settings_csa: _Optional[_Union[JointUlsConfiguration.SettingsCsaTreeTable, _Mapping]] = ..., settings_ec3: _Optional[_Union[JointUlsConfiguration.SettingsEc3TreeTable, _Mapping]] = ..., id_for_export_import: _Optional[str] = ..., metadata_for_export_import: _Optional[str] = ...) -> None: ...

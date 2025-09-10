import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ColumnDef(_message.Message):
    __slots__ = ("id", "name", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    type: _common_pb2.EpochFolioType
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[_common_pb2.EpochFolioType, str]] = ...) -> None: ...

class TableRow(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[_common_pb2.Scalar]
    def __init__(self, values: _Optional[_Iterable[_Union[_common_pb2.Scalar, _Mapping]]] = ...) -> None: ...

class TableData(_message.Message):
    __slots__ = ("rows",)
    ROWS_FIELD_NUMBER: _ClassVar[int]
    rows: _containers.RepeatedCompositeFieldContainer[TableRow]
    def __init__(self, rows: _Optional[_Iterable[_Union[TableRow, _Mapping]]] = ...) -> None: ...

class Table(_message.Message):
    __slots__ = ("type", "category", "title", "columns", "data")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    COLUMNS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    type: _common_pb2.EpochFolioDashboardWidget
    category: str
    title: str
    columns: _containers.RepeatedCompositeFieldContainer[ColumnDef]
    data: TableData
    def __init__(self, type: _Optional[_Union[_common_pb2.EpochFolioDashboardWidget, str]] = ..., category: _Optional[str] = ..., title: _Optional[str] = ..., columns: _Optional[_Iterable[_Union[ColumnDef, _Mapping]]] = ..., data: _Optional[_Union[TableData, _Mapping]] = ...) -> None: ...

class CardData(_message.Message):
    __slots__ = ("title", "value", "type", "group")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    title: str
    value: _common_pb2.Scalar
    type: _common_pb2.EpochFolioType
    group: int
    def __init__(self, title: _Optional[str] = ..., value: _Optional[_Union[_common_pb2.Scalar, _Mapping]] = ..., type: _Optional[_Union[_common_pb2.EpochFolioType, str]] = ..., group: _Optional[int] = ...) -> None: ...

class CardDef(_message.Message):
    __slots__ = ("type", "category", "data", "group_size")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    GROUP_SIZE_FIELD_NUMBER: _ClassVar[int]
    type: _common_pb2.EpochFolioDashboardWidget
    category: str
    data: _containers.RepeatedCompositeFieldContainer[CardData]
    group_size: int
    def __init__(self, type: _Optional[_Union[_common_pb2.EpochFolioDashboardWidget, str]] = ..., category: _Optional[str] = ..., data: _Optional[_Iterable[_Union[CardData, _Mapping]]] = ..., group_size: _Optional[int] = ...) -> None: ...

import common_pb2 as _common_pb2
import table_def_pb2 as _table_def_pb2
import chart_def_pb2 as _chart_def_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CardDefList(_message.Message):
    __slots__ = ("cards",)
    CARDS_FIELD_NUMBER: _ClassVar[int]
    cards: _containers.RepeatedCompositeFieldContainer[_table_def_pb2.CardDef]
    def __init__(self, cards: _Optional[_Iterable[_Union[_table_def_pb2.CardDef, _Mapping]]] = ...) -> None: ...

class ChartList(_message.Message):
    __slots__ = ("charts",)
    CHARTS_FIELD_NUMBER: _ClassVar[int]
    charts: _containers.RepeatedCompositeFieldContainer[_chart_def_pb2.Chart]
    def __init__(self, charts: _Optional[_Iterable[_Union[_chart_def_pb2.Chart, _Mapping]]] = ...) -> None: ...

class TableList(_message.Message):
    __slots__ = ("tables",)
    TABLES_FIELD_NUMBER: _ClassVar[int]
    tables: _containers.RepeatedCompositeFieldContainer[_table_def_pb2.Table]
    def __init__(self, tables: _Optional[_Iterable[_Union[_table_def_pb2.Table, _Mapping]]] = ...) -> None: ...

class TearSheet(_message.Message):
    __slots__ = ("cards", "charts", "tables")
    CARDS_FIELD_NUMBER: _ClassVar[int]
    CHARTS_FIELD_NUMBER: _ClassVar[int]
    TABLES_FIELD_NUMBER: _ClassVar[int]
    cards: CardDefList
    charts: ChartList
    tables: TableList
    def __init__(self, cards: _Optional[_Union[CardDefList, _Mapping]] = ..., charts: _Optional[_Union[ChartList, _Mapping]] = ..., tables: _Optional[_Union[TableList, _Mapping]] = ...) -> None: ...

class FullTearSheet(_message.Message):
    __slots__ = ("categories",)
    class CategoriesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: TearSheet
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[TearSheet, _Mapping]] = ...) -> None: ...
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    categories: _containers.MessageMap[str, TearSheet]
    def __init__(self, categories: _Optional[_Mapping[str, TearSheet]] = ...) -> None: ...

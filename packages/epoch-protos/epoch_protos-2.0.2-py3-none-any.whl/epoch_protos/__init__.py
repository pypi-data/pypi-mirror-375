"""
EpochProtos - Protocol Buffer definitions for EpochFolio models
"""

# Version will be replaced by setup process
__version__ = "2.0.2"

# Import all protobuf modules
from . import common_pb2
from . import chart_def_pb2
from . import table_def_pb2
from . import tearsheet_pb2

__all__ = [
    'common_pb2',
    'chart_def_pb2', 
    'table_def_pb2',
    'tearsheet_pb2'
]
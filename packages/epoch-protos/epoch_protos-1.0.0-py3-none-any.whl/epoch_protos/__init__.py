"""
EpochProtos Python Package

Generated protobuf definitions for EpochFolio models.
Provides Python/Pydantic-compatible data models for:
- Chart definitions (LinesDef, BarDef, HeatMapDef, etc.)
- Table definitions (Table, CardDef, etc.)
- Common enums and types (EpochFolioCategory, EpochFolioDashboardWidget, etc.)
"""

__version__ = "1.0.0"
__author__ = "EpochLab"

# Import generated protobuf modules
try:
    from . import common_pb2
    from . import chart_def_pb2
    from . import table_def_pb2
except ImportError:
    # Protobuf files not generated yet
    pass

__all__ = [
    "common_pb2",
    "chart_def_pb2", 
    "table_def_pb2"
]

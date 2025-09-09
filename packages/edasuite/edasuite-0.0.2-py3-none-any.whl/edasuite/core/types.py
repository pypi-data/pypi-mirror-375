"""Type definitions and enums for EDASuite."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


class FeatureType(Enum):
    """Enumeration of feature types."""
    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class FeatureMetadata:
    """Optional metadata for features from external JSON."""
    name: str
    provider: Optional[str] = None
    description: Optional[str] = None
    variable_type: Optional[str] = None
    default: Optional[str] = None
    no_hit_value: Optional[str] = None


@dataclass
class DatasetInfo:
    """Basic dataset information."""
    rows: int
    columns: int
    memory_mb: float
    missing_cells: int
    missing_percentage: float
    duplicate_rows: int = 0


@dataclass
class MissingInfo:
    """Missing data information."""
    count: int
    percent: float


@dataclass
class ContinuousStats:
    """Statistics for continuous features."""
    count: int
    mean: float
    std: float
    min: float
    max: float
    q1: float
    median: float
    q3: float
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    

@dataclass
class CategoricalStats:
    """Statistics for categorical features."""
    count: int
    unique: int
    mode: Any
    mode_count: int
    value_counts: Dict[str, int]
    value_percentages: Dict[str, float]
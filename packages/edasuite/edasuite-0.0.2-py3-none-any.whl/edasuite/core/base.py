"""Base analyzer interface and common functionality."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import time

import pandas as pd

from edasuite.core.types import FeatureType


@dataclass
class AnalysisResult:
    """Container for analysis results with metadata."""
    analyzer_name: str
    column_name: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "analyzer": self.analyzer_name,
            "column": self.column_name,
            "data": self.data,
            "metadata": self.metadata,
            "execution_time": self.execution_time
        }


class BaseAnalyzer(ABC):
    """Abstract base class for all data analyzers."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def analyzer_name(self) -> str:
        """Return the name of this analyzer."""
        pass
    
    @abstractmethod
    def can_analyze(self, series: pd.Series) -> bool:
        """Check if this analyzer can process the given series."""
        pass
    
    @abstractmethod
    def _analyze_impl(self, series: pd.Series) -> Dict[str, Any]:
        """Core analysis implementation."""
        pass
    
    def analyze(self, series: pd.Series) -> AnalysisResult:
        """Main analysis method implementing the template pattern."""
        start_time = time.perf_counter()
        
        if not self.can_analyze(series):
            raise ValueError(f"{self.analyzer_name} cannot analyze series '{series.name}'")
        
        processed_series = self._preprocess(series)
        results = self._analyze_impl(processed_series)
        results = self._postprocess(results, processed_series)
        
        execution_time = time.perf_counter() - start_time
        
        return AnalysisResult(
            analyzer_name=self.analyzer_name,
            column_name=series.name,
            data=results,
            metadata={
                "dtype": str(series.dtype),
                "size": len(series),
                "null_count": series.isnull().sum(),
            },
            execution_time=execution_time,
        )
    
    def _preprocess(self, series: pd.Series) -> pd.Series:
        """Pre-process series before analysis."""
        return series
    
    def _postprocess(self, results: Dict[str, Any], series: pd.Series) -> Dict[str, Any]:
        """Post-process analysis results."""
        return results
    
    @staticmethod
    def infer_feature_type(series: pd.Series) -> FeatureType:
        """Infer the feature type from pandas series."""
        if pd.api.types.is_numeric_dtype(series):
            unique_ratio = series.nunique() / len(series)
            if unique_ratio < 0.05 and series.nunique() < 20:
                return FeatureType.CATEGORICAL
            return FeatureType.CONTINUOUS
        elif pd.api.types.is_datetime64_any_dtype(series):
            return FeatureType.DATETIME
        elif pd.api.types.is_object_dtype(series):
            try:
                pd.to_datetime(series.dropna().iloc[:100], format='mixed', errors='coerce')
                return FeatureType.DATETIME
            except:
                pass
            
            if series.nunique() / len(series) < 0.5:
                return FeatureType.CATEGORICAL
            return FeatureType.TEXT
        else:
            return FeatureType.CATEGORICAL
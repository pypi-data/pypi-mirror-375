"""Analyzer for categorical features."""

from typing import Dict, Any
import pandas as pd
import numpy as np
from scipy import stats

from edasuite.core.base import BaseAnalyzer
from edasuite.core.types import CategoricalStats, MissingInfo


class CategoricalAnalyzer(BaseAnalyzer):
    """Analyzer for categorical features."""
    
    def __init__(self, max_categories: int = 50):
        """
        Initialize categorical analyzer.
        
        Args:
            max_categories: Maximum number of categories to include in value counts
        """
        super().__init__()
        self.max_categories = max_categories
    
    @property
    def analyzer_name(self) -> str:
        return "categorical"
    
    def can_analyze(self, series: pd.Series) -> bool:
        """Check if series is categorical or object type."""
        return (
            pd.api.types.is_object_dtype(series) or
            pd.api.types.is_categorical_dtype(series) or
            (pd.api.types.is_numeric_dtype(series) and series.nunique() < 20)
        )
    
    def _analyze_impl(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze categorical feature."""
        # Remove NaN values for calculations
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return self._empty_stats()
        
        # Value counts
        value_counts = clean_series.value_counts()
        total_count = len(clean_series)
        
        # Limit categories if too many
        if len(value_counts) > self.max_categories:
            top_categories = value_counts.head(self.max_categories)
            other_count = value_counts[self.max_categories:].sum()
            if other_count > 0:
                top_categories['_other_'] = other_count
            value_counts = top_categories
        
        # Calculate percentages
        value_percentages = {
            str(k): round(v / total_count * 100, 2) 
            for k, v in value_counts.items()
        }
        
        # Convert value counts to regular dict with string keys
        value_counts_dict = {
            str(k): int(v) for k, v in value_counts.items()
        }
        
        # Basic statistics
        mode_value = clean_series.mode()[0] if len(clean_series.mode()) > 0 else None
        
        categorical_stats = CategoricalStats(
            count=len(clean_series),
            unique=int(clean_series.nunique()),
            mode=str(mode_value) if mode_value is not None else None,
            mode_count=int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            value_counts=value_counts_dict,
            value_percentages=value_percentages
        )
        
        # Missing values
        missing_count = series.isnull().sum()
        missing_info = MissingInfo(
            count=int(missing_count),
            percent=round(missing_count / len(series) * 100, 2) if len(series) > 0 else 0
        )
        
        # Calculate entropy
        probabilities = value_counts / total_count
        entropy = stats.entropy(probabilities)
        
        # Cardinality analysis
        cardinality = clean_series.nunique()
        cardinality_ratio = cardinality / len(clean_series) if len(clean_series) > 0 else 0
        
        return {
            "type": "categorical",
            "missing": {
                "count": missing_info.count,
                "percent": missing_info.percent
            },
            "stats": {
                "count": categorical_stats.count,
                "unique": categorical_stats.unique,
                "mode": categorical_stats.mode,
                "mode_count": categorical_stats.mode_count,
                "mode_frequency": round(categorical_stats.mode_count / categorical_stats.count * 100, 2)
            },
            "distribution": {
                "value_counts": categorical_stats.value_counts,
                "value_percentages": categorical_stats.value_percentages,
                "top_n": min(10, len(value_counts_dict))
            },
            "cardinality": {
                "unique_values": cardinality,
                "cardinality_ratio": round(cardinality_ratio, 4),
                "is_high_cardinality": cardinality_ratio > 0.5,
                "entropy": round(float(entropy), 4)
            }
        }
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics for series with no valid values."""
        return {
            "type": "categorical",
            "missing": {"count": 0, "percent": 0.0},
            "stats": {
                "count": 0,
                "unique": 0,
                "mode": None,
                "mode_count": 0,
                "mode_frequency": 0.0
            },
            "distribution": {
                "value_counts": {},
                "value_percentages": {},
                "top_n": 0
            },
            "cardinality": {
                "unique_values": 0,
                "cardinality_ratio": 0.0,
                "is_high_cardinality": False,
                "entropy": 0.0
            }
        }
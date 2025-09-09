"""Basic statistics analyzer for dataset overview."""

from typing import Dict, Any

import pandas as pd
import numpy as np

from edasuite.core.base import BaseAnalyzer
from edasuite.core.types import DatasetInfo, FeatureType


class BasicStatsAnalyzer(BaseAnalyzer):
    """Analyzer for basic dataset statistics and overview."""
    
    @property
    def analyzer_name(self) -> str:
        return "basic_stats"
    
    def can_analyze(self, series: pd.Series) -> bool:
        """BasicStatsAnalyzer works on entire DataFrame, not series."""
        return False
    
    def _analyze_impl(self, series: pd.Series) -> Dict[str, Any]:
        """Not used for BasicStatsAnalyzer."""
        pass
    
    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze entire DataFrame for basic statistics.
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with dataset overview
        """
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        
        dataset_info = DatasetInfo(
            rows=len(df),
            columns=len(df.columns),
            memory_mb=df.memory_usage(deep=True).sum() / 1024 / 1024,
            missing_cells=missing_cells,
            missing_percentage=(missing_cells / total_cells * 100) if total_cells > 0 else 0,
            duplicate_rows=df.duplicated().sum()
        )
        
        # Analyze feature types
        feature_types = {}
        for col in df.columns:
            feature_types[col] = self.infer_feature_type(df[col]).value
        
        # Count by type
        type_counts = {
            "continuous": sum(1 for t in feature_types.values() if t == "continuous"),
            "categorical": sum(1 for t in feature_types.values() if t == "categorical"),
            "datetime": sum(1 for t in feature_types.values() if t == "datetime"),
            "text": sum(1 for t in feature_types.values() if t == "text"),
        }
        
        # Missing values by column
        missing_by_column = {}
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_by_column[col] = {
                    "count": int(missing_count),
                    "percent": round(missing_count / len(df) * 100, 2)
                }
        
        return {
            "dataset_info": {
                "rows": int(dataset_info.rows),
                "columns": int(dataset_info.columns),
                "memory_mb": round(dataset_info.memory_mb, 2),
                "missing_cells": int(dataset_info.missing_cells),
                "missing_percentage": round(dataset_info.missing_percentage, 2),
                "duplicate_rows": int(dataset_info.duplicate_rows)
            },
            "feature_types": type_counts,
            "feature_type_details": feature_types,
            "missing_values": {
                "total_missing": int(missing_cells),
                "columns_with_missing": len(missing_by_column),
                "details": missing_by_column
            },
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
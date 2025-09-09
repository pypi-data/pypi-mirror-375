"""Analyzer for continuous/numerical features."""

from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats

from edasuite.core.base import BaseAnalyzer
from edasuite.core.types import ContinuousStats, MissingInfo


class ContinuousAnalyzer(BaseAnalyzer):
    """Analyzer for continuous/numerical features."""
    
    @property
    def analyzer_name(self) -> str:
        return "continuous"
    
    def can_analyze(self, series: pd.Series) -> bool:
        """Check if series is numeric."""
        return pd.api.types.is_numeric_dtype(series)
    
    def _analyze_impl(self, series: pd.Series) -> Dict[str, Any]:
        """Analyze continuous feature."""
        # Remove NaN values for calculations
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return self._empty_stats()
        
        # Basic statistics
        basic_stats = ContinuousStats(
            count=len(clean_series),
            mean=float(clean_series.mean()),
            std=float(clean_series.std()),
            min=float(clean_series.min()),
            max=float(clean_series.max()),
            q1=float(clean_series.quantile(0.25)),
            median=float(clean_series.median()),
            q3=float(clean_series.quantile(0.75))
        )
        
        # Additional statistics
        try:
            # Check if data has sufficient variance for skewness/kurtosis calculation
            if basic_stats.std > 1e-10:  # Avoid near-zero variance
                with np.errstate(all='ignore'):  # Suppress numpy warnings
                    skew_val = stats.skew(clean_series, nan_policy='omit')
                    kurt_val = stats.kurtosis(clean_series, nan_policy='omit')
                    
                    # Check for valid results
                    basic_stats.skewness = float(skew_val) if np.isfinite(skew_val) else None
                    basic_stats.kurtosis = float(kurt_val) if np.isfinite(kurt_val) else None
            else:
                # Insufficient variance for meaningful skewness/kurtosis
                basic_stats.skewness = None
                basic_stats.kurtosis = None
        except (RuntimeWarning, ValueError, FloatingPointError):
            basic_stats.skewness = None
            basic_stats.kurtosis = None
        
        # Missing values
        missing_count = series.isnull().sum()
        missing_info = MissingInfo(
            count=int(missing_count),
            percent=round(missing_count / len(series) * 100, 2) if len(series) > 0 else 0
        )
        
        # Outlier detection using IQR method
        outliers = self._detect_outliers(clean_series, basic_stats.q1, basic_stats.q3)
        
        # Distribution analysis
        distribution = self._analyze_distribution(clean_series)
        
        return {
            "type": "continuous",
            "missing": {
                "count": missing_info.count,
                "percent": missing_info.percent
            },
            "stats": {
                "count": basic_stats.count,
                "mean": round(basic_stats.mean, 4),
                "std": round(basic_stats.std, 4),
                "min": round(basic_stats.min, 4),
                "max": round(basic_stats.max, 4),
                "q1": round(basic_stats.q1, 4),
                "median": round(basic_stats.median, 4),
                "q3": round(basic_stats.q3, 4),
                "skewness": round(basic_stats.skewness, 4) if basic_stats.skewness else None,
                "kurtosis": round(basic_stats.kurtosis, 4) if basic_stats.kurtosis else None,
                "iqr": round(basic_stats.q3 - basic_stats.q1, 4)
            },
            "outliers": outliers,
            "distribution": distribution,
            "unique_values": int(clean_series.nunique()),
            "unique_ratio": round(clean_series.nunique() / len(clean_series), 4)
        }
    
    def _detect_outliers(self, series: pd.Series, q1: float, q3: float) -> Dict[str, Any]:
        """Detect outliers using IQR method."""
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            "count": int(len(outliers)),
            "percent": round(len(outliers) / len(series) * 100, 2),
            "lower_bound": round(lower_bound, 4),
            "upper_bound": round(upper_bound, 4),
            "method": "iqr"
        }
    
    def _analyze_distribution(self, series: pd.Series, bins: int = 10) -> Dict[str, Any]:
        """Analyze distribution of values."""
        hist, bin_edges = np.histogram(series, bins=bins)
        
        return {
            "bins": bins,
            "counts": hist.tolist(),
            "bin_edges": [round(edge, 4) for edge in bin_edges.tolist()],
            "entropy": round(stats.entropy(hist + 1), 4)  # Add 1 to avoid log(0)
        }
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty statistics for series with no valid values."""
        return {
            "type": "continuous",
            "missing": {"count": 0, "percent": 0.0},
            "stats": {
                "count": 0,
                "mean": None,
                "std": None,
                "min": None,
                "max": None,
                "q1": None,
                "median": None,
                "q3": None,
                "skewness": None,
                "kurtosis": None,
                "iqr": None
            },
            "outliers": {"count": 0, "percent": 0.0},
            "distribution": None,
            "unique_values": 0,
            "unique_ratio": 0.0
        }
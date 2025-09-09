"""Data loading and validation utilities."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from edasuite.core.types import FeatureMetadata


class DataLoader:
    """Handles loading and validation of datasets."""
    
    @staticmethod
    def load_csv(
        filepath: Union[str, Path],
        sample_size: Optional[int] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load CSV file with optional sampling.
        
        Args:
            filepath: Path to CSV file
            sample_size: Optional number of rows to sample
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            Loaded DataFrame
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        
        if sample_size:
            df = pd.read_csv(filepath, nrows=sample_size, **kwargs)
        else:
            df = pd.read_csv(filepath, **kwargs)
        
        return df
    
    @staticmethod
    def load_feature_metadata(
        filepath: Union[str, Path]
    ) -> Dict[str, FeatureMetadata]:
        """
        Load feature metadata from JSON file.
        
        Args:
            filepath: Path to JSON file with feature metadata
            
        Returns:
            Dictionary mapping feature names to metadata
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        metadata = {}
        features = data.get('features', [])
        
        for feature in features:
            feature_obj = FeatureMetadata(
                name=feature.get('name'),
                provider=feature.get('provider'),
                description=feature.get('description'),
                variable_type=feature.get('variable_type'),
                default=feature.get('default'),
                no_hit_value=feature.get('no_hit_value')
            )
            if feature_obj.name:
                metadata[feature_obj.name] = feature_obj
        
        return metadata
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate DataFrame and return basic information.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        if df.empty:
            raise ValueError("DataFrame is empty")
        
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "memory_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            "column_types": df.dtypes.to_dict(),
            "has_duplicates": df.duplicated().any(),
            "duplicate_count": df.duplicated().sum()
        }
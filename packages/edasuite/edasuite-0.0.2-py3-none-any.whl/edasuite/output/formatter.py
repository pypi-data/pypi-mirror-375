"""JSON output formatter for EDA results."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union


class JSONFormatter:
    """Formats EDA results for JSON output."""
    
    @staticmethod
    def format_results(
        dataset_info: Dict[str, Any],
        features: Dict[str, Any],
        correlations: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        execution_time: float = 0.0
    ) -> Dict[str, Any]:
        """
        Format EDA results into structured JSON.
        
        Args:
            dataset_info: Basic dataset information
            features: Feature analysis results
            correlations: Correlation analysis results
            metadata: Additional metadata
            execution_time: Total execution time
            
        Returns:
            Formatted dictionary ready for JSON serialization
        """
        output = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "execution_time_seconds": round(execution_time, 2),
                "version": "0.1.0"
            },
            "dataset_info": dataset_info,
            "features": features
        }
        
        if correlations:
            output["correlations"] = correlations
        
        if metadata:
            output["metadata"].update(metadata)
        
        return output
    
    @staticmethod
    def save_json(
        data: Dict[str, Any],
        filepath: Union[str, Path],
        indent: int = 2,
        compact: bool = False
    ) -> None:
        """
        Save formatted data to JSON file.
        
        Args:
            data: Data to save
            filepath: Output file path
            indent: JSON indentation (None for compact)
            compact: If True, minimize JSON size
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            if compact:
                json.dump(data, f, separators=(',', ':'))
            else:
                json.dump(data, f, indent=indent)
    
    @staticmethod
    def to_json_string(
        data: Dict[str, Any],
        indent: Optional[int] = 2,
        compact: bool = False
    ) -> str:
        """
        Convert data to JSON string.
        
        Args:
            data: Data to convert
            indent: JSON indentation
            compact: If True, minimize JSON size
            
        Returns:
            JSON string
        """
        if compact:
            return json.dumps(data, separators=(',', ':'))
        else:
            return json.dumps(data, indent=indent)
    
    @staticmethod
    def compress_features(features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compress feature data for efficient storage.
        
        Removes redundant information and optimizes structure.
        
        Args:
            features: Feature analysis results
            
        Returns:
            Compressed feature data
        """
        compressed = {}
        
        for name, data in features.items():
            if data.get('type') == 'continuous':
                compressed[name] = {
                    't': 'c',  # type: continuous
                    'm': data.get('missing', {}),  # missing
                    's': {  # stats (abbreviated keys)
                        'mean': data['stats'].get('mean'),
                        'std': data['stats'].get('std'),
                        'min': data['stats'].get('min'),
                        'max': data['stats'].get('max'),
                        'med': data['stats'].get('median')
                    },
                    'o': data.get('outliers', {}).get('count', 0)  # outlier count
                }
            elif data.get('type') == 'categorical':
                compressed[name] = {
                    't': 'cat',  # type: categorical
                    'm': data.get('missing', {}),  # missing
                    'u': data['stats'].get('unique'),  # unique values
                    'mode': data['stats'].get('mode'),
                    'top5': dict(list(data['distribution']['value_counts'].items())[:5])
                }
        
        return compressed
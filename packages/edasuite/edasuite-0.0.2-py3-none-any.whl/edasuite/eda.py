"""Main EDA orchestrator."""

import time
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import pandas as pd

from edasuite.core.loader import DataLoader
from edasuite.core.base import BaseAnalyzer
from edasuite.core.types import FeatureMetadata, FeatureType
from edasuite.analyzers.basic import BasicStatsAnalyzer
from edasuite.analyzers.continuous import ContinuousAnalyzer
from edasuite.analyzers.categorical import CategoricalAnalyzer
from edasuite.output.formatter import JSONFormatter


class EDARunner:
    """Main orchestrator for EDA pipeline."""

    def __init__(
        self,
        max_categories: int = 50,
        sample_size: Optional[int] = None,
        top_correlations: int = 3,
        max_correlation_features: Optional[int] = None
    ):
        """
        Initialize EDA Runner.

        Args:
            max_categories: Maximum categories for categorical analysis
            sample_size: Optional sample size for large datasets
            top_correlations: Number of top correlations to show per feature
            max_correlation_features: Maximum features for correlation matrix. None = no limit
        """
        self.max_categories = max_categories
        self.sample_size = sample_size
        self.top_correlations = top_correlations
        self.max_correlation_features = max_correlation_features

        # Initialize analyzers
        self.basic_analyzer = BasicStatsAnalyzer()
        self.continuous_analyzer = ContinuousAnalyzer()
        self.categorical_analyzer = CategoricalAnalyzer(max_categories)

        # JSON formatter
        self.formatter = JSONFormatter()

    def run(
        self,
        csv_path: Union[str, Path],
        feature_metadata_path: Optional[Union[str, Path]] = None,
        output_path: Optional[Union[str, Path]] = None,
        compact_json: bool = False,
        columns: Optional[List[str]] = None,
        target_variable: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run complete EDA pipeline.

        Args:
            csv_path: Path to CSV dataset
            feature_metadata_path: Optional path to feature metadata JSON
            output_path: Optional path to save JSON output
            compact_json: If True, minimize JSON size
            columns: Optional list of columns to analyze (overrides feature_metadata)
            target_variable: Name of target variable column

        Returns:
            Complete EDA results as dictionary
        """
        start_time = time.perf_counter()

        # Load data
        print(f"Loading dataset from {csv_path}...")
        df = DataLoader.load_csv(csv_path, sample_size=self.sample_size)

        # Load feature metadata and determine columns to analyze
        feature_metadata = {}
        if feature_metadata_path:
            print(f"Loading feature metadata from {feature_metadata_path}...")
            feature_metadata = DataLoader.load_feature_metadata(feature_metadata_path)

            if not columns:  # If columns not explicitly provided, use feature metadata
                columns = list(feature_metadata.keys())
                print(f"Found {len(columns)} features in metadata")
            else:
                print(f"Using explicitly provided columns list with {len(columns)} features")

        # Filter columns if specified (either from metadata or explicit list)
        if columns:
            missing_cols = set(columns) - set(df.columns)
            if missing_cols:
                print(f"Warning: {len(missing_cols)} features not found in dataset")
                print(f"Missing features: {list(missing_cols)[:10]}...")  # Show first 10

            available_cols = [col for col in columns if col in df.columns]
            print(f"Analyzing {len(available_cols)} available features")

            # Include target variable if specified and not already included
            if target_variable and target_variable in df.columns and target_variable not in available_cols:
                available_cols.append(target_variable)
                print(f"Added target variable: {target_variable}")

            df = df[available_cols]

        # Run basic analysis
        print("Running basic dataset analysis...")
        dataset_info = self.basic_analyzer.analyze_dataframe(df)

        # Calculate correlations for numeric features
        print("Computing feature correlations...")
        correlation_matrix = self._compute_correlation_matrix(df, target_variable)

        # Analyze each feature
        print(f"Analyzing {len(df.columns)} features...")
        features = self._analyze_features(df, feature_metadata, target_variable, correlation_matrix)

        # Format results
        execution_time = time.perf_counter() - start_time
        results = self.formatter.format_results(
            dataset_info=dataset_info['dataset_info'],
            features=features,
            correlations={},  # Empty correlations - now embedded in features
            metadata={
                "dataset_name": Path(csv_path).name,
                "total_features_analyzed": len(features),
                "feature_types": dataset_info['feature_types'],
                "target_variable": target_variable,
                "has_feature_metadata": bool(feature_metadata),
                "correlation_config": {
                    "top_correlations": self.top_correlations,
                    "correlation_threshold": 0.1
                }
            },
            execution_time=execution_time
        )

        # Add missing values summary
        results['missing_values'] = dataset_info['missing_values']

        # Save if output path provided
        if output_path:
            print(f"Saving results to {output_path}...")
            self.formatter.save_json(results, output_path, compact=compact_json)

        print(f"EDA completed in {execution_time:.2f} seconds")
        return results

    def _analyze_features(
        self,
        df: pd.DataFrame,
        feature_metadata: Dict[str, FeatureMetadata],
        target_variable: Optional[str] = None,
        correlation_matrix: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Analyze all features in the dataset."""
        features = {}

        for col in df.columns:
            # Determine feature type - use metadata if available, otherwise infer
            if col in feature_metadata and feature_metadata[col].variable_type:
                metadata_type = feature_metadata[col].variable_type.lower()
                if metadata_type == "continuous":
                    feature_type = FeatureType.CONTINUOUS
                elif metadata_type == "categorical":
                    feature_type = FeatureType.CATEGORICAL
                else:
                    # Fallback to inference for unknown metadata types
                    feature_type = BaseAnalyzer.infer_feature_type(df[col])
            else:
                # No metadata available, infer from data
                feature_type = BaseAnalyzer.infer_feature_type(df[col])

            # Choose appropriate analyzer
            if feature_type.value == "continuous":
                analyzer = self.continuous_analyzer
                if analyzer.can_analyze(df[col]):
                    result = analyzer.analyze(df[col])
                    features[col] = result.data
            else:
                analyzer = self.categorical_analyzer
                if analyzer.can_analyze(df[col]):
                    result = analyzer.analyze(df[col])
                    features[col] = result.data

            # Mark if this is the target variable
            if col == target_variable:
                features[col]['is_target'] = True

            # Add metadata if available
            if col in feature_metadata:
                metadata = feature_metadata[col]
                features[col]['provider'] = metadata.provider
                features[col]['description'] = metadata.description

            # Add correlations for numeric features
            if col in features:
                correlations_data = self._get_feature_correlations(
                    col, correlation_matrix, target_variable, df
                )
                features[col]['correlations'] = correlations_data

        return features

    def _compute_correlation_matrix(self, df: pd.DataFrame, target_variable: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Compute correlation matrix for numeric features."""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) < 2:
            return None
            
        # Calculate correlation matrix (limit only if max_correlation_features is set)
        if self.max_correlation_features and len(numeric_cols) > self.max_correlation_features:
            print(f"Warning: Too many numeric features ({len(numeric_cols)}), using smart selection for top {self.max_correlation_features}")
            
            selected_cols = self._select_correlated_features(
                df[numeric_cols], target_variable, self.max_correlation_features
            )
            numeric_cols = selected_cols
            print(f"Selected {len(numeric_cols)} features using correlation-based selection")
        elif len(numeric_cols) > 100:
            print(f"Computing full correlation matrix for {len(numeric_cols)} features...")
            
        return df[numeric_cols].corr()
    
    def _select_correlated_features(
        self, 
        df: pd.DataFrame, 
        target_variable: Optional[str], 
        max_features: int
    ) -> List[str]:
        """Select features with highest correlations for matrix computation."""
        all_cols = df.columns.tolist()
        selected = set()
        
        # Always include target variable if available
        if target_variable and target_variable in all_cols:
            selected.add(target_variable)
        
        # If we have a target, find features most correlated with it
        if target_variable and target_variable in all_cols and len(selected) < max_features:
            # Compute pairwise correlations with target only (efficient)
            target_series = df[target_variable]
            target_corrs = {}
            
            for col in all_cols:
                if col != target_variable:
                    # Compute correlation between this feature and target directly
                    corr_val = target_series.corr(df[col])
                    if pd.notna(corr_val):
                        target_corrs[col] = abs(corr_val)
            
            # Sort by correlation strength and add top features
            sorted_target_corrs = sorted(target_corrs.items(), key=lambda x: x[1], reverse=True)
            for col, corr_val in sorted_target_corrs:
                if len(selected) < max_features:
                    selected.add(col)
        
        # Fill remaining slots with features that have highest pairwise correlations
        if len(selected) < max_features:
            remaining_cols = [col for col in all_cols if col not in selected]
            
            # Add remaining features in order (no sampling)
            for col in remaining_cols:
                if len(selected) < max_features:
                    selected.add(col)
        
        return list(selected)
    
    def _get_feature_correlations(
        self, 
        feature: str, 
        correlation_matrix: Optional[pd.DataFrame],
        target_variable: Optional[str] = None,
        df: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Get correlation data for a specific feature."""
        
        # Default structure for non-numeric features
        correlations_data = {
            "target_correlation": None,
            "top_correlated_features": []
        }
        
        # Skip if no correlation matrix
        if correlation_matrix is None:
            correlations_data["note"] = "Correlation not calculated for categorical features"
            return correlations_data
            
        # If feature is in correlation matrix, use precomputed correlations
        if feature in correlation_matrix.columns:
            return self._get_precomputed_correlations(feature, correlation_matrix, target_variable)
            
        # If feature not in matrix but we have df, compute correlations on-demand
        if df is not None and feature in df.columns and pd.api.types.is_numeric_dtype(df[feature]):
            return self._compute_feature_correlations(feature, df, correlation_matrix, target_variable)
            
        return correlations_data
    
    def _get_precomputed_correlations(
        self, 
        feature: str, 
        correlation_matrix: pd.DataFrame, 
        target_variable: Optional[str]
    ) -> Dict[str, Any]:
        """Get correlations for features already in the correlation matrix."""
        correlations_data = {
            "target_correlation": None,
            "top_correlated_features": []
        }
        
        # Get target correlation if target is numeric
        if target_variable and target_variable in correlation_matrix.columns and feature != target_variable:
            correlations_data["target_correlation"] = round(
                correlation_matrix.loc[feature, target_variable], 4
            )
        
        # Get top correlated features (excluding self and target)
        feature_corrs = correlation_matrix[feature].drop(feature)
        if target_variable and target_variable in feature_corrs.index:
            feature_corrs = feature_corrs.drop(target_variable)
            
        # Sort by absolute correlation and get top N
        top_corrs = feature_corrs.abs().sort_values(ascending=False).head(self.top_correlations)
        
        correlations_data["top_correlated_features"] = [
            {
                "feature": corr_feature,
                "correlation": round(correlation_matrix.loc[feature, corr_feature], 4)
            }
            for corr_feature in top_corrs.index
            if abs(correlation_matrix.loc[feature, corr_feature]) > 0.1  # threshold
        ]
        
        return correlations_data
    
    def _compute_feature_correlations(
        self, 
        feature: str, 
        df: pd.DataFrame, 
        correlation_matrix: pd.DataFrame, 
        target_variable: Optional[str]
    ) -> Dict[str, Any]:
        """Compute correlations on-demand for features not in the correlation matrix."""
        correlations_data = {
            "target_correlation": None,
            "top_correlated_features": []
        }
        
        feature_series = df[feature]
        
        # Get target correlation
        if target_variable and target_variable in correlation_matrix.columns:
            if target_variable in df.columns:
                target_corr = feature_series.corr(df[target_variable])
                if pd.notna(target_corr):
                    correlations_data["target_correlation"] = round(target_corr, 4)
        
        # Compute correlations with features in the correlation matrix
        feature_correlations = []
        for matrix_feature in correlation_matrix.columns:
            if matrix_feature != feature and matrix_feature in df.columns:
                corr_val = feature_series.corr(df[matrix_feature])
                if pd.notna(corr_val) and abs(corr_val) > 0.1:
                    feature_correlations.append({
                        "feature": matrix_feature,
                        "correlation": round(corr_val, 4)
                    })
        
        # Sort by absolute correlation and get top N
        feature_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
        correlations_data["top_correlated_features"] = feature_correlations[:self.top_correlations]
        
        return correlations_data

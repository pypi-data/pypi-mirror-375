"""Test continuous feature analyzer."""

import json
from edasuite.core.loader import DataLoader
from edasuite.analyzers.continuous import ContinuousAnalyzer

# Load dataset (with sampling for faster testing)
print("Loading dataset...")
df = DataLoader.load_csv("tmp/dataset.csv", sample_size=1000)

# Create analyzer
analyzer = ContinuousAnalyzer()

# Test on numeric columns that exist in this dataset
numeric_cols = ['Insuf_fund_amount_360', 'Insuf_fund_count_360', 'Windows_amount_360_ratio']

for col in numeric_cols:
    if col in df.columns:
        print(f"\n=== Analyzing: {col} ===")
        result = analyzer.analyze(df[col])
        
        # Display results
        print(f"Column: {result.column_name}")
        print(f"Analyzer: {result.analyzer_name}")
        print(f"Execution time: {result.execution_time:.4f}s")
        
        # Show analysis data
        data = result.data
        print(f"\nStatistics:")
        print(json.dumps(data['stats'], indent=2))
        
        print(f"\nOutliers:")
        print(json.dumps(data['outliers'], indent=2))
        
        print(f"\nUnique values: {data['unique_values']}")
        print(f"Unique ratio: {data['unique_ratio']}")
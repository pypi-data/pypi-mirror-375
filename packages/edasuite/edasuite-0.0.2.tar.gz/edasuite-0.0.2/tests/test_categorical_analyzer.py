"""Test categorical feature analyzer."""

import json
from edasuite.core.loader import DataLoader
from edasuite.analyzers.categorical import CategoricalAnalyzer

# Load dataset (with sampling for faster testing)
print("Loading dataset...")
df = DataLoader.load_csv("tmp/dataset.csv", sample_size=1000)

# Create analyzer
analyzer = CategoricalAnalyzer(max_categories=10)

# Test on categorical columns that exist in this dataset
categorical_cols = ['dataTag', 'sha_email', 'full_name']

for col in categorical_cols:
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
        
        print(f"\nCardinality:")
        print(json.dumps(data['cardinality'], indent=2))
        
        print(f"\nTop values:")
        for value, count in list(data['distribution']['value_counts'].items())[:5]:
            pct = data['distribution']['value_percentages'][value]
            print(f"  {value}: {count} ({pct}%)")
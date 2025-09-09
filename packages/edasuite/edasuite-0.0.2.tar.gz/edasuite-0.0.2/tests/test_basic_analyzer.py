"""Test basic statistics analyzer."""

import json
from edasuite.core.loader import DataLoader
from edasuite.analyzers.basic import BasicStatsAnalyzer

# Load dataset (with sampling for faster testing)
print("Loading dataset...")
df = DataLoader.load_csv("tmp/dataset.csv", sample_size=1000)

# Create and run analyzer
print("\nRunning BasicStatsAnalyzer...")
analyzer = BasicStatsAnalyzer()
results = analyzer.analyze_dataframe(df)

# Display results
print("\n=== Dataset Overview ===")
print(json.dumps(results["dataset_info"], indent=2))

print("\n=== Feature Types ===")
print(json.dumps(results["feature_types"], indent=2))

print("\n=== Missing Values Summary ===")
missing = results["missing_values"]
print(f"Total missing cells: {missing['total_missing']}")
print(f"Columns with missing: {missing['columns_with_missing']}")

# Show top 5 columns with most missing values
if missing['details']:
    sorted_missing = sorted(missing['details'].items(), 
                          key=lambda x: x[1]['count'], 
                          reverse=True)[:5]
    print("\nTop 5 columns with missing values:")
    for col, info in sorted_missing:
        print(f"  - {col}: {info['count']} ({info['percent']}%)")
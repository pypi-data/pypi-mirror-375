"""End-to-end test of EDASuite with dataset.csv"""

import json
from pathlib import Path
from edasuite import EDARunner

# Initialize EDA runner
print("Initializing EDASuite...")
runner = EDARunner(max_categories=20)

# Run EDA on test dataset
csv_path = "tmp/dataset.csv"
output_path = "tmp/eda_results.json"

# Test with a subset of columns for faster execution
test_columns = [
    'Class', 'Amount', 'Time', 
    'V1', 'V2', 'V3', 'V4', 'V5',
    'dataTag', 'V1_binned_optimal'
]

print(f"\nRunning EDA on {csv_path}")
print(f"Analyzing columns: {test_columns}")

results = runner.run(
    csv_path=csv_path,
    output_path=output_path,
    columns=test_columns,
    compact_json=False
)

# Display summary
print("\n" + "="*50)
print("EDA RESULTS SUMMARY")
print("="*50)

# Dataset info
dataset_info = results['dataset_info']
print(f"\nDataset Overview:")
print(f"  Rows: {dataset_info['rows']:,}")
print(f"  Columns: {dataset_info['columns']}")
print(f"  Memory: {dataset_info['memory_mb']:.2f} MB")
print(f"  Missing cells: {dataset_info['missing_cells']}")
print(f"  Duplicate rows: {dataset_info['duplicate_rows']}")

# Feature types
metadata = results['metadata']
print(f"\nFeature Types:")
for ftype, count in metadata['feature_types'].items():
    if count > 0:
        print(f"  {ftype}: {count}")

# Missing values
missing = results['missing_values']
if missing['columns_with_missing'] > 0:
    print(f"\nMissing Values:")
    print(f"  Total: {missing['total_missing']}")
    print(f"  Columns affected: {missing['columns_with_missing']}")

# Correlations
if 'correlations' in results and results['correlations']:
    corr = results['correlations']
    print(f"\nCorrelations:")
    print(f"  Features analyzed: {corr['correlation_summary']['features_analyzed']}")
    print(f"  High correlation pairs: {corr['correlation_summary']['high_correlation_pairs']}")
    
    if corr['high_correlations']:
        print(f"\n  Top 3 correlations:")
        for pair in corr['high_correlations'][:3]:
            print(f"    {pair['feature1']} <-> {pair['feature2']}: {pair['correlation']}")

# Sample feature analysis
print(f"\nSample Feature Analysis:")
for i, (name, data) in enumerate(results['features'].items()):
    if i >= 3:  # Show first 3 features
        break
    print(f"\n  {name} ({data['type']}):")
    if data['type'] == 'continuous':
        stats = data['stats']
        print(f"    Mean: {stats['mean']:.2f}, Std: {stats['std']:.2f}")
        print(f"    Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
        print(f"    Outliers: {data['outliers']['count']}")
    else:
        stats = data['stats']
        print(f"    Unique values: {stats['unique']}")
        print(f"    Mode: {stats['mode']} ({stats['mode_frequency']}%)")

print(f"\n✅ Results saved to: {output_path}")
print(f"   File size: {Path(output_path).stat().st_size / 1024:.2f} KB")
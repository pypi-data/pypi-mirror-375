"""Test EDASuite with real data and feature metadata."""

import json
from pathlib import Path
from edasuite import EDARunner

# Initialize EDA runner
print("Testing EDASuite with real data...")
runner = EDARunner(max_categories=20)

# Test with real data and feature config
csv_path = "tmp/dataset.csv"
feature_config_path = "tmp/feature_config.json"
output_path = "tmp/real_eda_results.json"
target_var = "target_variable"

print(f"\nRunning EDA on real dataset:")
print(f"  CSV: {csv_path}")
print(f"  Feature config: {feature_config_path}")
print(f"  Target variable: {target_var}")

# Run EDA using feature metadata to determine columns
results = runner.run(
    csv_path=csv_path,
    feature_metadata_path=feature_config_path,
    target_variable=target_var,
    output_path=output_path,
    compact_json=False
)

# Display summary
print("\n" + "="*60)
print("REAL DATA EDA RESULTS SUMMARY")
print("="*60)

# Dataset info
dataset_info = results['dataset_info']
print(f"\nDataset Overview:")
print(f"  Rows: {dataset_info['rows']:,}")
print(f"  Columns analyzed: {dataset_info['columns']}")
print(f"  Memory: {dataset_info['memory_mb']:.2f} MB")
print(f"  Missing cells: {dataset_info['missing_cells']:,}")
print(f"  Duplicate rows: {dataset_info['duplicate_rows']:,}")

# Metadata info
metadata = results['metadata']
print(f"\nAnalysis Configuration:")
print(f"  Target variable: {metadata['target_variable']}")
print(f"  Has feature metadata: {metadata['has_feature_metadata']}")
print(f"  Total features analyzed: {metadata['total_features_analyzed']}")

# Feature types
print(f"\nFeature Types:")
for ftype, count in metadata['feature_types'].items():
    if count > 0:
        print(f"  {ftype}: {count}")

# Target variable analysis
target_features = {name: data for name, data in results['features'].items() 
                  if data.get('is_target', False)}
if target_features:
    print(f"\nTarget Variable Analysis:")
    for name, data in target_features.items():
        print(f"  Variable: {name}")
        print(f"  Type: {data['type']}")
        if data['type'] == 'categorical':
            print(f"  Unique values: {data['stats']['unique']}")
            print(f"  Mode: {data['stats']['mode']} ({data['stats']['mode_frequency']}%)")
        else:
            print(f"  Mean: {data['stats']['mean']:.4f}")
            print(f"  Range: [{data['stats']['min']:.4f}, {data['stats']['max']:.4f}]")

# Target correlations
if 'correlations' in results and 'target_correlations' in results['correlations']:
    target_corr = results['correlations']['target_correlations']
    print(f"\nTop 5 Features Correlated with Target:")
    for i, (feature, corr) in enumerate(list(target_corr.items())[:5]):
        print(f"  {i+1}. {feature}: {corr}")

# Missing values
missing = results['missing_values']
if missing['columns_with_missing'] > 0:
    print(f"\nMissing Values:")
    print(f"  Total: {missing['total_missing']:,}")
    print(f"  Columns affected: {missing['columns_with_missing']}")

# Sample features with metadata
features_with_metadata = {name: data for name, data in results['features'].items() 
                         if 'provider' in data}
if features_with_metadata:
    print(f"\nSample Features with Metadata (first 3):")
    for i, (name, data) in enumerate(list(features_with_metadata.items())[:3]):
        print(f"  {name}:")
        print(f"    Provider: {data.get('provider', 'N/A')}")
        print(f"    Type: {data['type']}")
        print(f"    Description: {data.get('description', 'N/A')[:60]}...")

print(f"\n✅ Results saved to: {output_path}")
print(f"   File size: {Path(output_path).stat().st_size / 1024:.2f} KB")
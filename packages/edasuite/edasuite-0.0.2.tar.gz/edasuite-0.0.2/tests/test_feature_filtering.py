"""Test that EDA only analyzes features present in feature_metadata."""

from edasuite import EDARunner

print("Testing feature filtering with metadata...")

# Initialize EDA runner
runner = EDARunner(max_categories=20)

# Test with feature metadata - should only analyze features in metadata
print("\n" + "="*60)
print("TEST: EDA with feature metadata filtering")
print("="*60)

results = runner.run(
    csv_path="tmp/dataset.csv",
    feature_metadata_path="tmp/feature_config.json",
    output_path="tmp/test_filtered_eda.json",
    compact_json=True
)

print(f"\n✅ Analysis completed!")
print(f"   Total features analyzed: {results['metadata']['total_features_analyzed']}")
print(f"   Has feature metadata: {results['metadata']['has_feature_metadata']}")
print(f"   Dataset columns: {results['dataset_info']['columns']}")

# Count features in metadata file to verify
import json
with open("tmp/feature_config.json", 'r') as f:
    metadata = json.load(f)
    metadata_features = len(metadata.get('features', []))

print(f"   Features in metadata file: {metadata_features}")

if results['metadata']['total_features_analyzed'] == metadata_features:
    print("   ✅ SUCCESS: Only analyzed features from metadata!")
else:
    print(f"   ❌ ERROR: Analyzed {results['metadata']['total_features_analyzed']} but metadata has {metadata_features}")

print(f"\n📁 Results saved to: tmp/test_filtered_eda.json")
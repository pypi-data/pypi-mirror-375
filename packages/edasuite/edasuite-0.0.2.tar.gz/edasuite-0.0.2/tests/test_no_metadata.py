"""Test EDA without feature metadata (should analyze all columns)."""

from edasuite import EDARunner

print("Testing EDA without feature metadata...")

# Initialize EDA runner
runner = EDARunner(max_categories=20)

print("\n" + "="*60)
print("TEST: EDA without feature metadata (analyze all columns)")
print("="*60)

results = runner.run(
    csv_path="tmp/dataset.csv",
    output_path="tmp/test_no_metadata_eda.json",
    compact_json=True
)

print(f"\n✅ Analysis completed!")
print(f"   Total features analyzed: {results['metadata']['total_features_analyzed']}")
print(f"   Has feature metadata: {results['metadata']['has_feature_metadata']}")
print(f"   Dataset columns: {results['dataset_info']['columns']}")

# Should analyze all columns in the dataset
if results['metadata']['total_features_analyzed'] == results['dataset_info']['columns']:
    print("   ✅ SUCCESS: Analyzed all columns when no metadata provided!")
else:
    print(f"   ❌ ERROR: Mismatch in column counts")

print(f"\n📁 Results saved to: tmp/test_no_metadata_eda.json")
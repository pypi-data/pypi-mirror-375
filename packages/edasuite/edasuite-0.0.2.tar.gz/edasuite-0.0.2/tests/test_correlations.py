"""Test the new feature-level correlation functionality."""

from edasuite import EDARunner

print("Testing new correlation functionality...")

# Test with different top_correlations values
for top_n in [3, 5]:
    print(f"\n" + "="*60)
    print(f"TEST: EDA with top_correlations={top_n}")
    print("="*60)
    
    runner = EDARunner(max_categories=20, top_correlations=top_n)
    
    results = runner.run(
        csv_path="tmp/dataset.csv",
        feature_metadata_path="tmp/feature_config.json",
        target_variable="target_variable",
        output_path=f"tmp/test_correlations_{top_n}.json",
        compact_json=True
    )
    
    print(f"✅ Analysis completed with top_correlations={top_n}")
    print(f"   Total features: {results['metadata']['total_features_analyzed']}")
    print(f"   Correlation config: {results['metadata']['correlation_config']}")
    
    # Check a few features for correlation data
    sample_features = list(results['features'].keys())[:3]
    for feature in sample_features:
        corr_data = results['features'][feature].get('correlations', {})
        print(f"   Feature '{feature}':")
        print(f"     Target correlation: {corr_data.get('target_correlation')}")
        print(f"     Top correlations: {len(corr_data.get('top_correlated_features', []))}")
        
        # Show first correlation if any
        if corr_data.get('top_correlated_features'):
            first_corr = corr_data['top_correlated_features'][0]
            print(f"     Highest: {first_corr['feature']} ({first_corr['correlation']})")

print(f"\n📁 Results saved to: tmp/test_correlations_3.json and tmp/test_correlations_5.json")
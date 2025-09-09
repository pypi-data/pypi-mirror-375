"""Test data loader with dataset.csv"""

from edasuite.core.loader import DataLoader

# Test loading CSV (with sampling for faster testing)
print("Testing DataLoader...")
df = DataLoader.load_csv("tmp/dataset.csv", sample_size=1000)
print(f"Loaded dataset with shape: {df.shape}")

# Validate DataFrame
validation = DataLoader.validate_dataframe(df)
print(f"Dataset info:")
print(f"  - Rows: {validation['rows']}")
print(f"  - Columns: {validation['columns']}")
print(f"  - Memory: {validation['memory_mb']:.2f} MB")
print(f"  - Has duplicates: {validation['has_duplicates']}")

# Show first few columns
print(f"\nFirst 5 columns: {list(df.columns[:5])}")
print(f"Data types sample: {dict(list(df.dtypes.items())[:5])}")
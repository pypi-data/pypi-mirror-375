from synthbiodata import create_config, generate_sample_data

print("\n=== Molecular Descriptors Examples ===")

# Simple usage
df1 = generate_sample_data(data_type="molecular-descriptors")
print("\nSimple usage results:")
print(f"Generated {len(df1)} samples with {len(df1.columns)} features")

# Imbalanced data with default ratio
df2 = generate_sample_data(data_type="molecular-descriptors", imbalanced=True)
print("\nImbalanced data results:")
print(f"Generated {len(df2)} samples with {len(df2.columns)} features")

# Advanced usage with full configuration
config = create_config(
    "molecular-descriptors",
    imbalanced=True,
    n_samples=10000,
    positive_ratio=0.03,
    mw_mean=400.0,  # Customize molecular weight parameters
    mw_std=80.0,
    # Customize target families and their probabilities
    target_families=['GPCR', 'Kinase'],
    target_family_probs=[0.6, 0.4]  # Must sum to 1.0
)
df3 = generate_sample_data(config=config)
print("\nAdvanced configuration results:")
print(f"Generated {len(df3)} samples with {len(df3.columns)} features")
print(f"Target families distribution:")
print(df3.group_by('target_family').len())


print("\n=== ADME Examples ===")

# Simple ADME usage
df4 = generate_sample_data(data_type="adme")
print("\nSimple ADME results:")
print(f"Generated {len(df4)} samples with {len(df4.columns)} features")

# Imbalanced ADME data
df5 = generate_sample_data(
    data_type="adme",
    imbalanced=True,
    n_samples=10000,
    positive_ratio=0.03
)
print("\nImbalanced ADME results:")
print(f"Generated {len(df5)} samples with {len(df5.columns)} features")

# Advanced ADME configuration
adme_config = create_config(
    "adme",
    imbalanced=True,
    n_samples=10000,
    positive_ratio=0.03,
    absorption_mean=75.0,
    absorption_std=15.0,
    clearance_mean=4.0,
    half_life_mean=15.0
)
df6 = generate_sample_data(config=adme_config)
print("\nAdvanced ADME configuration results:")
print(f"Generated {len(df6)} samples with {len(df6.columns)} features")
print("ADME feature statistics:")
print(df6.describe())
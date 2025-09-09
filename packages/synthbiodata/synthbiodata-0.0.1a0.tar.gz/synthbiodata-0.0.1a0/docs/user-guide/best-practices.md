# Examples



## Best Practices

### Test Configurations

Test configurations with small datasets first:

```python
# Test with minimal configuration
test_config = create_config(
    data_type="molecular-descriptors",
    n_samples=10,  # Very small for testing; only 10 data points
    random_state=42
)

# Generate and inspect data
df = generate_sample_data(config=test_config)
print(f"Generated {len(df)} samples successfully")
```

### Reproducibility

Always set `random_state` for reproducible results:

```python
config = create_config(
    data_type="molecular-descriptors",
    random_state=123  # Ensures reproducible data
)
```


### Validate Before Use

Check configuration validity before expensive operations:

```python
try:
    config = create_config(
        data_type="adme",
        absorption_mean=75.0,
        clearance_mean=5.0
    )
    print("Configuration is valid")
except (RangeError, DistributionError, ValidationError) as e:
    print(f"Configuration error: {e}")
```

### Use Realistic Ranges

Choose parameters that reflect realistic biological ranges:

- **Molecular Weight**: 150-600 Da for drug-like molecules
- **LogP**: -2 to 6 for good drug-like properties
- **TPSA**: 0-200 Å² for membrane permeability
- **Absorption**: 20-100% for oral bioavailability
- **Protein Binding**: 50-99% for plasma distribution

### Performance Considerations

- Larger `n_samples` values require more memory and computation time
- Complex target family distributions may slow down generation
- Consider using `imbalanced=True` for more realistic class distributions


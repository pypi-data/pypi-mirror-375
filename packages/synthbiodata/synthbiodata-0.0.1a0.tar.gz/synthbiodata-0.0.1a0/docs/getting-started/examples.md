# Code Examples

All the code examples from the SynthBioData documentation in a single place!

## Basic Usage

### Quick Start

Generate data with default settings:

```python
from synthbiodata import generate_sample_data

# Generate molecular descriptor data
df = generate_sample_data(data_type="molecular-descriptors")
print(f"Generated {len(df)} samples with {len(df.columns)} features")

# Generate ADME data
df_adme = generate_sample_data(data_type="adme")
print(f"Generated {len(df_adme)} samples with {len(df_adme.columns)} features")
```

### Custom Configuration

Create custom configurations for different use cases:

```python
from synthbiodata import create_config, generate_sample_data

# Create a custom configuration
custom_config = create_config(
    data_type="molecular-descriptors",
    n_samples=1000,
    positive_ratio=0.1,
    imbalanced=True,
)

# Generate data with your custom configuration
df = generate_sample_data(config=custom_config)
print(f"Total samples: {len(df)}")
print(f"Features: {len(df.columns) - 1}")  # Exclude target column
print(f"Positive ratio: {df['binds_target'].mean():.1%}")
```

### Reproducible Data Generation

Ensure reproducible results with random seeds:

```python
# Generate reproducible data
df1 = generate_sample_data(
    data_type="molecular-descriptors",
    random_state=321
)

# Same seed = identical results
df2 = generate_sample_data(
    data_type="molecular-descriptors", 
    random_state=321
)

assert (df1 == df2).all().all()  # True
```

## Configuration Examples

### Basic Parameters

Using the same parameters for both data types:

```python
from synthbiodata import create_config, generate_sample_data

# Same parameters work for both data types
# Molecular descriptors configuration
config_molecular = create_config(
    data_type="molecular-descriptors",
    n_samples=1000,           # Dataset with 1000 samples
    positive_ratio=0.5,       # 50% positive samples (balanced)
    test_size=0.2,            # 20% for testing
    val_size=0.2,             # 20% for validation
    random_state=123          # Set seed for reproducibility
)

# ADME configuration with identical basic parameters
config_adme = create_config(
    data_type="adme",
    n_samples=1000,           # Same sample size
    positive_ratio=0.5,       # Same positive ratio
    test_size=0.2,            # Same test split
    val_size=0.2,             # Same validation split
    random_state=123          # Same random seed
)

# Generate data with each configuration
df_molecular = generate_sample_data(config=config_molecular)
df_adme = generate_sample_data(config=config_adme)

# Check the dataset - same parameters produce consistent splits
print(f"Molecular dataset: {len(df_molecular)} samples, {df_molecular['binds_target'].mean():.1%} positive")
print(f"ADME dataset: {len(df_adme)} samples, {df_adme['bioavailable'].mean():.1%} positive")
```

### Molecular Descriptors Configuration

Custom molecular descriptor configuration:

```python
from synthbiodata import create_config, generate_sample_data

# Create a custom molecular descriptors configuration
config = create_config(
    data_type="molecular-descriptors",
    n_samples=2000,                    # Generate 2000 samples
    positive_ratio=0.15,               # 15% positive samples
    mw_mean=400.0,                     # Mean molecular weight
    mw_std=80.0,                       # Standard deviation
    mw_min=200.0,                      # Minimum weight
    mw_max=500.0,                      # Maximum weight
    logp_mean=3.0,                     # Mean LogP
    logp_std=1.2,                      # LogP standard deviation
    logp_min=0.0,                      # Minimum LogP
    logp_max=5.0,                      # Maximum LogP
    tpsa_mean=90.0,                    # Mean TPSA
    tpsa_std=35.0,                     # TPSA standard deviation
    target_families=['GPCR', 'Kinase'], # Target families
    target_family_probs=[0.6, 0.4],    # Family probabilities
    random_state=123                    # Reproducible results
)

# Generate the data
df = generate_sample_data(config=config)

# Inspect the results
print(f"Generated {len(df)} samples")
print(f"Positive ratio: {df['binds_target'].mean():.1%}")
print(f"Target families: {df['target_family'].value_counts().to_dict()}")
print(f"Molecular weight range: {df['molecular_weight'].min():.1f} - {df['molecular_weight'].max():.1f} Da")
```

### ADME Configuration

Custom ADME configuration:

```python
from synthbiodata.config.schema.v1.adme import ADMEConfig

# Create a configuration for high-absorption compounds
config = ADMEConfig(
    n_samples=3000,
    positive_ratio=0.05,
    absorption_mean=90.0,
    absorption_std=10.0,
    plasma_protein_binding_mean=95.0,
    plasma_protein_binding_std=5.0,
    clearance_mean=3.0,
    clearance_std=1.0,
    half_life_mean=18.0,
    half_life_std=8.0,
    renal_clearance_ratio=0.2,
    random_state=456
)
```

### Factory Function Usage

Using the factory function for easy configuration:

```python
from synthbiodata import create_config

# Create molecular configuration with custom parameters
config = create_config(
    data_type="molecular-descriptors",
    n_samples=2000,
    positive_ratio=0.15,
    mw_mean=300.0,
    random_state=789
)

# Create ADME configuration
config = create_config(
    data_type="adme",
    n_samples=1500,
    absorption_mean=80.0,
    random_state=789
)
```

### Direct Class Instantiation

For full control, instantiate configuration classes directly:

```python
from synthbiodata.config.schema.v1.molecular import MolecularConfig
from synthbiodata.config.schema.v1.adme import ADMEConfig

# Molecular configuration
mol_config = MolecularConfig(
    n_samples=1000,
    mw_mean=400.0,
    target_families=['GPCR', 'Kinase', 'Protease'],
    target_family_probs=[0.5, 0.3, 0.2]
)

# ADME configuration
adme_config = ADMEConfig(
    n_samples=1000,
    absorption_mean=75.0,
    half_life_mean=15.0
)
```

## Validation Examples

### Dataset Split Validation

Valid and invalid split configurations:

```python
# Valid: 60% training, 20% validation, 20% test
config = create_config(
    data_type="molecular-descriptors",
    test_size=0.2,
    val_size=0.2
)

# Invalid: Would raise RangeError
config = create_config(
    data_type="molecular-descriptors", 
    test_size=0.6,
    val_size=0.5  # Total = 1.1 > 1.0
)
```

### Positive Ratio Validation

Valid and invalid positive ratios:

```python
# Valid ratios
config = create_config(positive_ratio=0.1)   # 10% positive
config = create_config(positive_ratio=0.5)   # 50% positive
config = create_config(positive_ratio=0.9)   # 90% positive

# Invalid ratios
config = create_config(positive_ratio=0.0)   # No positive samples
config = create_config(positive_ratio=1.0)   # All positive samples
config = create_config(positive_ratio=1.5)   # > 100%
```

### Molecular Weight Validation

Valid and invalid molecular weight parameters:

```python
from synthbiodata.config.schema.v1.molecular import MolecularConfig

# Valid molecular weight parameters
config = MolecularConfig(
    mw_min=150.0,    # Minimum weight
    mw_max=600.0,    # Maximum weight (must be > min)
    mw_std=100.0     # Standard deviation (must be > 0)
)

# Invalid: min >= max
config = MolecularConfig(mw_min=500.0, mw_max=400.0)  # RangeError

# Invalid: std <= 0
config = MolecularConfig(mw_std=0.0)  # RangeError
```

### LogP Validation

Valid LogP parameters:

```python
# Valid LogP parameters
config = MolecularConfig(
    logp_min=-2.0,   # Hydrophilic
    logp_max=6.0,    # Lipophilic
    logp_std=1.5     # Distribution width
)
```

### TPSA Validation

Valid TPSA parameters:

```python
# Valid TPSA parameters
config = MolecularConfig(
    tpsa_min=0.0,    # Non-polar
    tpsa_max=200.0,  # Highly polar
    tpsa_std=40.0    # Distribution width
)
```

### Target Family Validation

Valid and invalid target family distributions:

```python
# Valid target family distribution
config = MolecularConfig(
    target_families=['GPCR', 'Kinase', 'Protease'],
    target_family_probs=[0.5, 0.3, 0.2]  # Sums to 1.0
)

# Invalid: length mismatch
config = MolecularConfig(
    target_families=['GPCR', 'Kinase'],
    target_family_probs=[0.5, 0.3, 0.2]  # 2 families, 3 probabilities
)

# Invalid: probabilities don't sum to 1.0
config = MolecularConfig(
    target_families=['GPCR', 'Kinase'],
    target_family_probs=[0.5, 0.3]  # Sums to 0.8, not 1.0
)
```

### ADME Percentage Validation

Valid and invalid percentage parameters:

```python
from synthbiodata.config.schema.v1.adme import ADMEConfig

# Valid percentage parameters
config = ADMEConfig(
    absorption_mean=75.0,              # 75% absorption
    plasma_protein_binding_mean=90.0   # 90% protein binding
)

# Invalid: negative percentage
config = ADMEConfig(absorption_mean=-10.0)  # RangeError

# Invalid: > 100%
config = ADMEConfig(plasma_protein_binding_mean=150.0)  # RangeError
```

### ADME Positive Value Validation

Valid and invalid positive parameters:

```python
# Valid positive parameters
config = ADMEConfig(
    clearance_mean=5.0,    # 5 L/h clearance
    half_life_mean=12.0    # 12 hours half-life
)

# Invalid: zero or negative
config = ADMEConfig(clearance_mean=0.0)    # RangeError
config = ADMEConfig(half_life_mean=-2.0)   # RangeError
```

### ADME Ratio Validation

Valid and invalid ratio parameters:

```python
# Valid ratio parameter
config = ADMEConfig(renal_clearance_ratio=0.3)  # 30% renal clearance

# Invalid: outside 0-1 range
config = ADMEConfig(renal_clearance_ratio=1.5)  # RangeError
```

### Standard Deviation Validation

Valid and invalid standard deviations:

```python
# Valid standard deviations
config = ADMEConfig(
    absorption_std=20.0,
    clearance_std=2.0,
    half_life_std=6.0
)

# Invalid: zero or negative standard deviation
config = ADMEConfig(absorption_std=0.0)  # RangeError
```

## Error Handling Examples

### RangeError Handling

Handling range validation errors:

```python
from synthbiodata.exceptions import RangeError

try:
    config = MolecularConfig(mw_min=500.0, mw_max=400.0)
except RangeError as e:
    print(f"Invalid range: {e}")
    # Output: Invalid range: mw_min (500.0) must be less than max_val (400.0)
```

### DistributionError Handling

Handling distribution validation errors:

```python
from synthbiodata.exceptions import DistributionError

try:
    config = MolecularConfig(
        target_families=['GPCR', 'Kinase'],
        target_family_probs=[0.5, 0.3]  # Sums to 0.8
    )
except DistributionError as e:
    print(f"Invalid distribution: {e}")
    # Output: Invalid distribution: Target family probabilities must sum to 1.0, got 0.8
```

## Best Practices Examples

### Test Configurations

Testing with small datasets:

```python
# Test with minimal configuration
test_config = create_config(
    data_type="molecular-descriptors",
    n_samples=10,  # Very small for testing; only 10 data points
    random_state=123
)

# Generate and inspect data
df = generate_sample_data(config=test_config)
print(f"Generated {len(df)} samples successfully")
```

### Reproducibility

Ensuring reproducible results:

```python
config = create_config(
    data_type="molecular-descriptors",
    random_state=123  # Ensures reproducible data
)
```

### Validation Before Use

Checking configuration validity:

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



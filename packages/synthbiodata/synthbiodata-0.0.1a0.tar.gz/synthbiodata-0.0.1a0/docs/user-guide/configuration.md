# Configuration Guide

SynthBioData provides a flexible configuration system that allows you to customize data generation parameters for different types of synthetic biological data. This doc page covers the available configuration options and how to use them effectively.

## Overview

The configuration system is built on Pydantic models with full type validation and automatic parameter checking. All configurations inherit from `BaseConfig` and extend it with data-type-specific parameters.

## General Configuration

All data types share common configuration parameters defined in `BaseConfig`:

### Basic Parameters


| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `n_samples` | int | 10000 | Number of samples to generate |
| `positive_ratio` | float | 0.03 | Ratio of positive samples in the dataset (between 0 and 1) |
| `test_size` | float | 0.2 | Fraction of data to use for testing (between 0 and 1) |
| `val_size` | float | 0.2 | Fraction of data to use for validation (between 0 and 1) |
| `random_state` | int | 42 | Random seed for reproducible data generation |
| `imbalanced` | bool | False | Whether to generate an imbalanced dataset |

#### Example



<details>
<summary>Click to expand example code: Base configuration</summary>

How to use the basic parameters to create different types of datasets:

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

</details>

### Validation

The configuration system automatically validates all parameters to ensure they are within realistic biological ranges and mathematically valid. For detailed validation rules and error handling, see the [Validation Rules](validation-rules.md) page.

## Molecular Descriptors Configuration

The `MolecularConfig` class extends `BaseConfig` with parameters specific to molecular descriptor generation.

### Molecular Weight Parameters

| Parameter   | Type   | Default | Description                              |
|-------------|--------|---------|------------------------------------------|
| `mw_mean`   | float  | 350.0   | Mean molecular weight in Daltons         |
| `mw_std`    | float  | 100.0   | Standard deviation of molecular weight   |
| `mw_min`    | float  | 150.0   | Minimum molecular weight                 |
| `mw_max`    | float  | 600.0   | Maximum molecular weight                 |


### LogP Parameters

| Parameter   | Type   | Default | Description                                   |
|-------------|--------|---------|-----------------------------------------------|
| `logp_mean` | float  | 2.5     | Mean LogP (octanol-water partition coefficient)|
| `logp_std`  | float  | 1.5     | Standard deviation of LogP                    |
| `logp_min`  | float  | -2.0    | Minimum LogP value                            |
| `logp_max`  | float  | 6.0     | Maximum LogP value                            |

### TPSA Parameters

| Parameter    | Type   | Default | Description                          |
|--------------|--------|---------|--------------------------------------|
| `tpsa_mean`  | float  | 80.0    | Mean topological polar surface area  |
| `tpsa_std`   | float  | 40.0    | Standard deviation of TPSA           |
| `tpsa_min`   | float  | 0.0     | Minimum TPSA value                   |
| `tpsa_max`   | float  | 200.0   | Maximum TPSA value                   |

### Target Family Parameters

| Parameter             | Type         | Default Value                                              | Description                                                                 |
|-----------------------|--------------|------------------------------------------------------------|-----------------------------------------------------------------------------|
| `target_families`     | list[str]    | ['GPCR', 'Kinase', 'Protease', 'Nuclear Receptor', 'Ion Channel'] | List of target protein families to sample from                              |
| `target_family_probs` | list[float]  | [0.3, 0.25, 0.2, 0.15, 0.1]                               | Probability distribution for selecting each target family (must sum to 1.0)  |

#### Example

<details>
<summary>Click to expand example code: Molecular descriptors configuration</summary>

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

</details>

## ADME Data Configuration

The `ADMEConfig` class extends `BaseConfig` with parameters for generating ADME (Absorption, Distribution, Metabolism, Excretion) data.

### Absorption Parameters

| Parameter                        | Type   | Default | Description                                   |
|-----------------------------------|--------|---------|-----------------------------------------------|
| `absorption_mean`                 | float  | 70.0    | Mean absorption percentage (0-100)            |
| `absorption_std`                  | float  | 20.0    | Standard deviation of absorption              |
| `plasma_protein_binding_mean`     | float  | 85.0    | Mean plasma protein binding percentage (0-100)|
| `plasma_protein_binding_std`      | float  | 15.0    | Standard deviation of plasma protein binding  |

### Metabolism Parameters

| Parameter           | Type   | Default | Description                        |
|---------------------|--------|---------|------------------------------------|
| `clearance_mean`    | float  | 5.0     | Mean clearance rate in L/h         |
| `clearance_std`     | float  | 2.0     | Standard deviation of clearance    |
| `half_life_mean`    | float  | 12.0    | Mean half-life in hours            |
| `half_life_std`     | float  | 6.0     | Standard deviation of half-life    |

### Excretion Parameters

| Parameter                | Type   | Default | Description                                 |
|--------------------------|--------|---------|---------------------------------------------|
| `renal_clearance_ratio`  | float  | 0.3     | Ratio of renal to total clearance (0-1)     |

### Example: Custom ADME Configuration

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

## Using Configurations

### Factory Function

The easiest way to create configurations is using the factory function:

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







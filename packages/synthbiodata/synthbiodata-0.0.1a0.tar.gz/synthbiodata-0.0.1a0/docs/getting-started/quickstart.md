# Getting Started with SynthBioData

Welcome to **SynthBioData**! This guide will help you get up and running with synthetic biological data generation for drug discovery and machine learning applications.

!!! warning "Important Notice"
    This package generates *synthetic* data for testing and educational purposes only.  
    
    The data produced does **not** represent real biological or chemical measurements and should **not** be used for clinical, regulatory, or production applications.

## What is SynthBioData?

SynthBioData is a Python package that generates realistic synthetic drug discovery data, including:

- **Molecular Descriptors**: Molecular weight, LogP, TPSA, hydrogen bond donors/acceptors, and more
- **ADME Data**: Absorption, Distribution, Metabolism, and Excretion properties
- **Target Families**: Support for GPCR, Kinase, Protease, and other protein families
- **Chemical Fingerprints**: Binary chemical fingerprints as features

## Quick Installation

Install SynthBioData using your preferred package manager:

=== "uv (Recommended)"
    ```bash
    uv pip install synthbiodata
    ```

=== "pip"
    ```bash
    pip install synthbiodata
    ```

=== "conda"
    ```bash
    conda install -c conda-forge synthbiodata
    ```

## How to use `synthbiodata`

### 1. Basic Usage

Start with the simplest approach by generating data with the default settings:

```python
from synthbiodata import generate_sample_data

# Generate molecular descriptor data
df = generate_sample_data(data_type="molecular-descriptors")
print(f"Generated {len(df)} samples with {len(df.columns)} features")

# Generate ADME data
df_adme = generate_sample_data(data_type="adme")
print(f"Generated {len(df_adme)} samples with {len(df_adme.columns)} features")
```

### 2. Custom Configuration

For more control over data generation, provide a  custom configuration. In the example below,  `custom_config` has parameters like `n_samples`, `postive_ratio` and `imbalanced` to generate an imabalance dataset with 1000 samples:

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

### 3. Reproducible datasets

Ensure reproducible data generation by setting the paramater `random_state`:

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

## Data Types Overview

### Molecular Descriptors

Generate synthetic molecular data with features like:

- **Physical Properties**: Molecular weight, LogP, TPSA
- **Structural Features**: Hydrogen bond donors/acceptors, rotatable bonds
- **Chemical Properties**: Aromatic rings, chemical fingerprints
- **Target Information**: Protein families (GPCR, Kinase, Protease, etc.)

### ADME Data

Generate ADME (Absorption, Distribution, Metabolism, Excretion) data with:

- **Absorption**: Bioavailability percentages and absorption rates
- **Distribution**: Plasma protein binding and volume of distribution
- **Metabolism**: Clearance rates and half-life predictions
- **Excretion**: Renal clearance and elimination parameters

## Next Steps

Now that you have the basics, explore these detailed guides:

<div class="grid cards" markdown>

-   :material-rocket-launch: **[Quick Start Tutorial](quickstart.md)**
    
    Step-by-step tutorial with practical examples

-   :material-cog: **[Configuration Guide](../user-guide/configuration.md)**
    
    Learn about all configuration options and customization

-   :material-book-open: **[User Guide](../user-guide/architecture.md)**
    
    Comprehensive usage examples and advanced features

-   :material-api: **[API Reference](../api/data-generators.md)**
    
    Complete API documentation and class references

</div>

## Key Features

<div class="grid cards" markdown>

-   :material-molecule: **Realistic Data**
    
    Generate data that mimics real-world molecular properties and distributions

-   :material-target: **Multiple Target Types**
    
    Support for various protein families and target types

-   :material-chart-line: **Configurable Parameters**
    
    Customize data generation to match your specific needs

-   :material-speedometer: **High Performance**
    
    Built on Polars for fast data manipulation and processing

-   :material-shield-check: **Type Safe**
    
    Full type hints and Pydantic validation for robust configuration

-   :material-reproducible: **Reproducible**
    
    Deterministic data generation with random seed support

</div>

## Common Use Cases

- **Machine Learning Research**: Generate training data for drug discovery ML models
- **Algorithm Testing**: Test and validate ML algorithms with controlled synthetic data
- **Educational Purposes**: Learn about molecular properties and drug discovery concepts
- **Benchmarking**: Create standardized datasets for comparing different approaches
- **Prototype Development**: Quickly generate data for proof-of-concept applications

## Need Help?

- 📖 Check out the [User Guide](../user-guide/architecture.md) for detailed examples
- 🔧 Visit the [API Reference](../api/data-generators.md) for complete documentation
- 🐛 Report issues on [GitHub](https://github.com/ojeda-e/synthbiodata/issues)
- 💬 Join discussions in the [GitHub Discussions](https://github.com/ojeda-e/synthbiodata/discussions)

---

Ready to dive deeper? Start with the [Quick Start Tutorial](quickstart.md) for a hands-on walkthrough!

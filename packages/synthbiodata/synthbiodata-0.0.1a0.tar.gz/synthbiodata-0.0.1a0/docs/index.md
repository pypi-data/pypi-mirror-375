# SynthBioData (Synthetic Biological Data)

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Polars](https://img.shields.io/badge/powered%20by-Polars-CB4C78.svg)](https://pola.rs/)

A Python package for generating synthetic drug discovery data that mimics real-world scenarios using realistic molecular descriptors and target properties.

!!! warning "Important Notice"
    This package generates *synthetic* data for testing and educational purposes only.  
    
    The data produced does **not** represent real biological or chemical measurements and should **not** be used for clinical, regulatory, or production applications.

## Quick Start

Get started with `synthbiodata` in just a few lines of code:

```python
from synthbiodata import generate_sample_data

# Generate molecular descriptor data
df = generate_sample_data(data_type="molecular-descriptors")
print(f"Generated {len(df)} samples with {len(df.columns)} features")

# Generate ADME data
df_adme = generate_sample_data(data_type="adme")
print(f"Generated {len(df_adme)} samples with {len(df_adme.columns)} features")
```

## Key Features

<div class="grid cards" markdown>

-   :material-molecule: **Molecular Descriptors**
    
    Generate realistic molecular properties like MW, LogP, TPSA, HBD, HBA, and more

-   :material-test-tube: **ADME Data**
    
    Simulate Absorption, Distribution, Metabolism, and Excretion properties

-   :material-target: **Target Families**
    
    Support for GPCR, Kinase, Protease, and other protein families

-   :material-chart-line: **Chemical Fingerprints**
    
    Generate binary chemical fingerprints as features

-   :material-cog: **Configurable**
    
    Customize data generation parameters and distributions

-   :material-speedometer: **Efficient**
    
    Built on Polars for fast data manipulation and processing

</div>

## Data Types

### Molecular Descriptors
Generate synthetic molecular data with features like:

- Molecular weight, LogP, TPSA
- Hydrogen bond donors/acceptors
- Rotatable bonds, aromatic rings
- Chemical fingerprints
- Target protein families (GPCR, Kinase, Protease, etc.)

### ADME Data
Generate ADME (Absorption, Distribution, Metabolism, Excretion) data with:

- Absorption percentages
- Plasma protein binding
- Clearance rates and half-life
- Bioavailability predictions

## ⬇ Installation

Install synthbiodata using your preferred package manager:

=== "uv"
    ```bash
    uv pip install synthbiodata
    ```

=== "pip"
    ```bash
    pip install synthbiodata
    ```

<!-- === "conda"
    ```bash
    conda install -c conda-forge synthbiodata
    ``` -->

## 📖 Documentation

Explore the docs:

- **[Quick Start](getting-started/quickstart.md)** - Get up and running quickly.
- **[User Guide](user-guide/architecture.md)** - The backstage of Synthbiodata explained.
- **[API Reference](api/data-generators.md)** - Complete API documentation.
- **[Examples](getting-started/examples.md) - Detailed usage examples.

## 🔗 Links

- [GitHub Repository](https://github.com/ojeda-e/synthbiodata)
- [Issue Tracker](https://github.com/ojeda-e/synthbiodata/issues)
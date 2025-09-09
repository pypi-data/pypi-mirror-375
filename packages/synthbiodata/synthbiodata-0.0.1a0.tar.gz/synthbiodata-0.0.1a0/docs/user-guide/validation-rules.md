# Validation Rules

SynthBioData uses comprehensive validation to ensure that all configuration parameters are within realistic biological ranges and mathematically valid. This page documents all validation rules for each data type.

## What is a Validation Rule?

!!! note "Definition"
    A **validation rule** in SynthBioData is a constraint that ensures configuration parameters are valid, realistic, and safe.

In a more detailed definition, validations rules are:

1. **Mathematically Valid**: Parameters must satisfy basic mathematical requirements.
    
    - Ex: Minimum values must be less than maximum values, probabilities must sum to 1.0.

2. **Biologically Realistic**: Parameters must fall within ranges that make sense for real-world biological data.

    - Ex: Molecular weights between 150-600 Da for drug-like molecules.

3. **Computationally Sound**: Parameters must not cause errors during data generation.

    - Ex: Standard deviations must be positive to avoid invalid distributions.

4. **Type Safe**: Parameters must match their expected data types.

    - Ex: Integers for sample counts, floats for ratios.

When you create a configuration, SynthBioData automatically checks all these rules and raises specific exceptions if any parameter violates them. This prevents you from generating unrealistic data or encountering runtime errors during data generation. 

## General Validation Rules

All data types share these common validation rules:

### Dataset Split Validation

**Rule**: `test_size + val_size` must be less than 1.0

**Purpose**: Ensures there's always data remaining for training after validation and test splits.

**Example**:
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

**Rule**: `positive_ratio` must be between 0 and 1 (exclusive)

**Purpose**: Ensures valid probability for positive sample generation.

**Example**:
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

## Validation Rules for Data Types
### Molecular Data Validation Rules

Molecular descriptor configurations have additional validation rules for realistic biological ranges.

#### Molecular Weight Validation

**Rule**: `mw_min < mw_max` and `mw_std > 0`

**Purpose**: Ensures valid molecular weight ranges and distributions.

**Example**:
```python
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

#### LogP Validation

**Rule**: `logp_min < logp_max` and `logp_std > 0`

**Purpose**: Ensures valid LogP (lipophilicity) ranges for drug-like molecules.

**Example**:
```python
# Valid LogP parameters
config = MolecularConfig(
    logp_min=-2.0,   # Hydrophilic
    logp_max=6.0,    # Lipophilic
    logp_std=1.5     # Distribution width
)
```

#### TPSA Validation

**Rule**: `tpsa_min < tpsa_max` and `tpsa_std > 0`

**Purpose**: Ensures valid topological polar surface area ranges.

**Example**:
```python
# Valid TPSA parameters
config = MolecularConfig(
    tpsa_min=0.0,    # Non-polar
    tpsa_max=200.0,  # Highly polar
    tpsa_std=40.0    # Distribution width
)
```

#### Target Family Validation

**Rule**: `len(target_families) == len(target_family_probs)` and `sum(target_family_probs) == 1.0`

**Purpose**: Ensures valid probability distribution for target family selection.

**Example**:
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

### ADME Data Validation Rules

ADME configurations have validation rules specific to pharmacokinetic parameters.

#### Percentage Parameter Validation

**Rule**: Parameters representing percentages must be between 0 and 100

**Applies to**: `absorption_mean`, `plasma_protein_binding_mean`

**Example**:
```python
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

#### Positive Value Validation

**Rule**: Parameters representing rates or times must be positive

**Applies to**: `clearance_mean`, `half_life_mean`

**Example**:
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

#### Ratio Validation

**Rule**: Parameters representing ratios must be between 0 and 1

**Applies to**: `renal_clearance_ratio`

**Example**:
```python
# Valid ratio parameter
config = ADMEConfig(renal_clearance_ratio=0.3)  # 30% renal clearance

# Invalid: outside 0-1 range
config = ADMEConfig(renal_clearance_ratio=1.5)  # RangeError
```

#### Standard Deviation Validation

**Rule**: All standard deviations must be positive

**Applies to**: All `*_std` parameters

**Example**:
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

## Error Handling

When validation fails, SynthBioData raises specific exceptions with detailed error messages:

### RangeError

Raised when parameters are outside valid ranges:

```python
from synthbiodata.exceptions import RangeError

try:
    config = MolecularConfig(mw_min=500.0, mw_max=400.0)
except RangeError as e:
    print(f"Invalid range: {e}")
    # Output: Invalid range: mw_min (500.0) must be less than max_val (400.0)
```

### DistributionError

Raised when probability distributions are invalid:

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



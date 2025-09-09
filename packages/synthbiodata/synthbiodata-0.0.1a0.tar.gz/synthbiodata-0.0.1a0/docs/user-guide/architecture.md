# System Architecture

SynthBioData is built on a modular, extensible architecture that separates concerns and provides a clean interface for generating different types of synthetic biological data. This design makes the system maintainable, testable, and easy to extend with new data types.

## Core Design Principles

The architecture follows several key design principles:

**Separation of Concerns**: Configuration, data generation, and business logic are separated into distinct modules.

**Type Safety**: Full type hints and Pydantic validation ensure robust parameter handling and clear interfaces.

**Extensibility**: New data types can be added by implementing the base generator interface without modifying existing code.

**Reproducibility**: All generators use seeded random number generation to ensure consistent results.

**Performance**: Built on Polars for efficient data manipulation and NumPy for fast numerical operations.

## Component Overview

### Configuration Layer

The configuration system provides type-safe parameter management:

- **`BaseConfig`**: Common parameters shared by all data types (sample size, random state, validation splits).
- **`MolecularConfig`**: Molecular-specific parameters (MW, LogP, TPSA ranges, target families).
- **`ADMEConfig`**: ADME-specific parameters (absorption, clearance, half-life distributions).

All configurations use Pydantic for automatic validation and provide clear error messages for invalid parameters.

### Generator Layer

The generator layer implements the actual data generation logic:

- **`BaseGenerator`**: Abstract base class providing common functionality.
- **`MolecularGenerator`**: Generates molecular descriptor data with target binding probabilities.
- **`ADMEGenerator`**: Generates ADME data with bioavailability classifications.

Each generator is self-contained and responsible for its specific data type.

### Factory Layer

The factory layer provides convenient interfaces for creating configurations and generators:

- **`create_config()`**: Type-safe configuration creation with automatic parameter validation.
- **`create_generator()`**: Generator instantiation based on configuration type.
- **`generate_sample_data()`**: High-level function for quick data generation.

## Inheritance Hierarchy

The data generation system follows a clean inheritance hierarchy:

```
BaseGenerator (Abstract)
├── MolecularGenerator
└── ADMEGenerator
```

**BaseGenerator** is responsible for storing and validating configuration settings, ensuring reproducible results through seeded random number generation (using NumPy) and deterministic fake data creation (using Faker). It also defines the abstract interface that all data generators must implement.

**MolecularGenerator** extends BaseGenerator by providing molecular descriptor generation (including MW, LogP, TPSA, and related properties), chemical fingerprint generation, target protein family simulation, and binding probability calculation.

**ADMEGenerator** extends BaseGenerator by providing ADME property generation (including absorption, distribution, metabolism, and excretion) as well as bioavailability classification and pharmacokinetic parameter simulation.

## Data Flow

The typical data generation flow follows these steps:

```mermaid
graph LR
    A[**Configuration**] --> B[Validation]
    B --> C[Generator]
    C --> D[Data Generation]
    D --> E[DataFrame]
    E --> F[**Result**]
    
    style A fill:#5f9099,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#5f9970,stroke:#333,stroke-width:2px,color:#fff
```

### Process Steps

1. **Configuration Creation**: User creates or loads a configuration object.
2. **Validation**: Pydantic validates all parameters and raises errors for invalid values.
3. **Generator Instantiation**: Factory creates appropriate generator based on configuration type.
4. **Data Generation**: Generator creates synthetic data using statistical distributions.
5. **Post-processing**: Data is formatted into Polars DataFrames with proper column names and types.
6. **Return**: Complete dataset is returned to the use.


## Extensibility

The architecture is designed to make it straightforward to introduce new data types. 

Adding one involves extending the BaseConfig with any required parameters, then implementing a new generator class that inherits from BaseGenerator. Once the generator is defined, it only needs to be registered with the factory functions and given sensible defaults in the constants module.

This modular design ensures that new functionality can be integrated seamlessly, without disrupting existing features or requiring changes to the core architecture.

## Error Handling

The system is designed with comprehensive error handling built in at multiple levels.

Before any data generation begins, configuration validation powered by Pydantic ensures that invalid parameters are caught early. In addition, custom validators enforce that inputs fall within realistic biological ranges, preventing nonsensical configurations from slipping through. Strong type hints add another layer of safety by reducing common programming errors during development. 

Finally, when issues do occur, the system provides clear and detailed error messages, making it easier for users to understand what went wrong and how to fix it.

For more information on error handling, check the [validation rules](./validation-rules.md) documentation page.

## Performance Considerations

The architecture is designed for performance, combining efficient data structures and computational strategies:

SynthBioData is powered by Polars to provide a foundation for fast and flexible data manipulation, while NumPy enables highly efficient vectorized numerical operations. To reduce memory overhead, the system uses generators to create data in chunks whenever possible. For large datasets, Polars’ lazy evaluation further optimizes execution by deferring computations until results are actually needed.

This design ensures that SynthBioData can handle both small experimental datasets and large-scale data generation tasks efficiently.


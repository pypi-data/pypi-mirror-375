"""
Factory functions for creating configurations and generators.
"""

from typing import Optional, overload, Literal, cast
import polars as pl

from synthbiodata.config.base import BaseConfig, DataType
from synthbiodata.config.schema.v1.molecular import MolecularConfig
from synthbiodata.config.schema.v1.adme import ADMEConfig
from synthbiodata.core.base import BaseGenerator
from synthbiodata.core.molecular import MolecularGenerator
from synthbiodata.core.adme import ADMEGenerator
from synthbiodata.exceptions import DataTypeError
from synthbiodata.logging import logger

# Overloads for the create_config function - type hints
@overload
def create_config(data_type: Literal["molecular-descriptors"], imbalanced: bool = False, **kwargs) -> MolecularConfig:
    ...

@overload
def create_config(data_type: Literal["adme"], imbalanced: bool = False, **kwargs) -> ADMEConfig:
    ...

@overload
def create_config(data_type: str, imbalanced: bool = False, **kwargs) -> BaseConfig:
    ...

def create_config(data_type: str, imbalanced: bool = False, **kwargs) -> BaseConfig:
    """
    Create a configuration for the specified data type.

    Parameters
    ----------
    data_type : str
        The type of data to generate ("molecular-descriptors" or "adme").
    imbalanced : bool, optional
        Whether to generate imbalanced data, by default False.
    **kwargs
        Additional configuration parameters.

    Returns
    -------
    MolecularConfig
        If `data_type` is "molecular-descriptors".
    ADMEConfig
        If `data_type` is "adme".
    BaseConfig
        For other types (though this will raise an error).

    Raises
    ------
    DataTypeError
        If `data_type` is not a valid DataType.
    """
    config_classes = {
        DataType.MOLECULAR: MolecularConfig,
        DataType.ADME: ADMEConfig,
    }
    
    try:
        data_type_enum = DataType(data_type)
    except ValueError:
        logger.error(f"Invalid data type: {data_type}")
        raise DataTypeError(f"'{data_type}' is not a valid DataType")
        
    config_class = config_classes.get(data_type_enum, BaseConfig)
    
    # Set imbalanced flag and update kwargs
    kwargs['imbalanced'] = imbalanced
    if imbalanced and 'positive_ratio' not in kwargs:
        kwargs['positive_ratio'] = 0.03  # Default imbalanced ratio
        
    config = config_class(**kwargs)
    if data_type == "molecular-descriptors":
        return cast(MolecularConfig, config)
    elif data_type == "adme":
        return cast(ADMEConfig, config)
    return config

def create_generator(config: BaseConfig) -> BaseGenerator:
    """Create a generator for the given configuration."""
    if isinstance(config, MolecularConfig):
        return MolecularGenerator(config)
    elif isinstance(config, ADMEConfig):
        return ADMEGenerator(config)
    raise ValueError(f"Unsupported config type: {type(config)}")

def generate_sample_data(
    data_type: str = "molecular-descriptors",
    imbalanced: bool = False,
    config: Optional[BaseConfig] = None,
    **kwargs
) -> pl.DataFrame:
    """Generate synthetic biological data."""
    if config is None:
        # Set default values only if not provided in kwargs
        if 'n_samples' not in kwargs:
            kwargs['n_samples'] = 5000
        if 'positive_ratio' not in kwargs:
            kwargs['positive_ratio'] = 0.03 if imbalanced else 0.5
        if 'random_state' not in kwargs:
            kwargs['random_state'] = 42
            
        config = create_config(data_type, imbalanced=imbalanced, **kwargs)
    
    generator = create_generator(config)
    return generator.generate_data()

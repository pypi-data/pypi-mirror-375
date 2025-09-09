"""
Generator for ADME (Absorption, Distribution, Metabolism, Excretion) data.
"""

import numpy as np
import polars as pl
from synthbiodata.logging import logger
from synthbiodata.config.schema.v1.adme import ADMEConfig
from synthbiodata.core.base import BaseGenerator

class ADMEGenerator(BaseGenerator):
    """
    Generator for synthetic ADME (Absorption, Distribution, Metabolism, Excretion) data. Creates
    binary bioavailability labels based on realistic pharmaceutical criteria.

    The ADMEGenerator class creates synthetic datasets simulating pharmacokinetic properties
    relevant to drug discovery and pharmaceutical research. It generates realistic distributions
    for features such as absorption percentage, plasma protein binding, clearance rate, and half-life.
    The generator can also simulate imbalanced datasets for classification tasks by controlling the
    proportion of positive (bioavailable) samples.

    This generator is useful for benchmarking machine learning models, simulating clinical trial data,
    and educational purposes where realistic ADME data is required without using sensitive patient information.

    Attributes:
        config (ADMEConfig): Configuration object specifying statistical parameters and options for ADME data generation.

    Methods:
        __init__(config): Initialize the ADME generator with the provided configuration.
        generate_data(): Generate a complete synthetic ADME dataset as a polars DataFrame, including binary bioavailability labels.
    
    Code Example:
        ```python
        from synthbiodata.config.schema.v1.adme import ADMEConfig
        from synthbiodata.core.adme import ADMEGenerator
        
        config = ADMEConfig(n_samples=100, random_state=123)
        gen = ADMEGenerator(config)
        df = gen.generate_data()
        print(df.head())
        ```
    """
    
    def __init__(self, config: ADMEConfig):
        """Initialize the ADME generator."""
        super().__init__(config)
        self.config: ADMEConfig = config
    
    def generate_data(self) -> pl.DataFrame:
        """Generate synthetic ADME data."""
        logger.info(f"Generating {self.config.n_samples} ADME samples...")
        if self.config.imbalanced:
            logger.info(f"Using imbalanced dataset with positive ratio: {self.config.positive_ratio:.1%}")
        
        # Generate base features
        data = {
            'absorption': np.clip(
                self.rng.normal(
                    self.config.absorption_mean,
                    self.config.absorption_std,
                    self.config.n_samples
                ),
                0, 100
            ),
            'plasma_protein_binding': np.clip(
                self.rng.normal(
                    self.config.plasma_protein_binding_mean,
                    self.config.plasma_protein_binding_std,
                    self.config.n_samples
                ),
                0, 100
            ),
            'clearance': np.clip(
                self.rng.normal(
                    self.config.clearance_mean,
                    self.config.clearance_std,
                    self.config.n_samples
                ),
                0, None
            ),
            'half_life': np.clip(
                self.rng.normal(
                    self.config.half_life_mean,
                    self.config.half_life_std,
                    self.config.n_samples
                ),
                0, None
            ),
        }
        
        # Calculate drug bioavailability (binary target)
        bioavailability = np.logical_and.reduce([
            data['absorption'] > 50,
            data['plasma_protein_binding'] < 95,
            data['clearance'] < 8,
            data['half_life'] > 6
        ]).astype(int)
        
        # If imbalanced, adjust the labels
        if self.config.imbalanced:
            n_positive = int(self.config.n_samples * self.config.positive_ratio)
            current_positives = bioavailability.sum()
            if current_positives > n_positive:
                # Randomly set some positives to negative
                positive_indices = np.where(bioavailability == 1)[0]
                to_flip = self.rng.choice(
                    positive_indices,
                    size=int(current_positives - n_positive),
                    replace=False
                )
                bioavailability[to_flip] = 0
            elif current_positives < n_positive:
                # Randomly set some negatives to positive
                negative_indices = np.where(bioavailability == 0)[0]
                to_flip = self.rng.choice(
                    negative_indices,
                    size=int(n_positive - current_positives),
                    replace=False
                )
                bioavailability[to_flip] = 1
        
        df = pl.DataFrame(data)
        df = df.with_columns(pl.Series("good_bioavailability", bioavailability))
        
        positive_count = bioavailability.sum()
        positive_ratio = positive_count / len(bioavailability)
        logger.info(f"Generated {len(df)} samples")
        logger.info(f"Features: {len(df.columns) - 1}")  # Exclude target column
        logger.info(f"Positive samples: {positive_count} ({positive_ratio:.1%})")
        
        return df

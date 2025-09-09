"""
Base generator class for synthetic data generation.


The abstract base class that all data generators inherit from. Provides common functionality including random number generation, Faker integration, and the abstract interface that all generators must implement.
"""

from abc import ABC, abstractmethod
import numpy as np
import polars as pl
from faker import Faker

from synthbiodata.config.base import BaseConfig

class BaseGenerator(ABC):
    """
    Abstract base class for all synthetic data generators.

    This class provides common functionality for all data generators, including:

    - Storing the configuration object.
    - Initializing a NumPy random number generator with a fixed random state for reproducibility.
    - Providing a seeded Faker instance for generating fake data.
    - Defining the abstract interface for data generation.

    Attributes:
        config (BaseConfig): Configuration object containing generator parameters and random state.
        rng (numpy.random.Generator): NumPy random number generator initialized with the provided random state.
        fake (faker.Faker): Faker instance seeded for reproducible fake data generation.

    Methods:
        generate_data: Abstract method to generate synthetic data. Must be implemented by subclasses.
    """
    
    def __init__(self, config: BaseConfig):
        """Initialize the generator."""
        self.config = config
        self.rng = np.random.default_rng(config.random_state)
        self.fake = Faker()
        self.fake.seed_instance(config.random_state)
    
    @abstractmethod
    def generate_data(self) -> pl.DataFrame:
        """Generate synthetic data."""
        pass

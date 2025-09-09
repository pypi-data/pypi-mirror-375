"""
Base configuration classes and validation for synthetic data generation.
"""

from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, model_validator

from synthbiodata.constants import DATASET_DEFAULTS
from synthbiodata.exceptions import RangeError
from synthbiodata.logging import logger

class DataType(str, Enum):
    """Supported data types for generation."""
    MOLECULAR = "molecular-descriptors"
    ADME = "adme"
    # TODO: Add other data types as needed (cancer, dose-response, etc.)

class BaseConfig(BaseModel):
    """Base configuration for all data types."""
    schema_version: Literal["1.0"] = "1.0"
    
    n_samples: int = Field(DATASET_DEFAULTS["DEFAULT_SAMPLES"], 
                        description="Number of samples to generate")
    positive_ratio: float = Field(DATASET_DEFAULTS["IMBALANCED_RATIO"], 
                              description="Ratio of positive samples")
    test_size: float = Field(DATASET_DEFAULTS["TEST_SIZE"], 
                         description="Test set size ratio")
    val_size: float = Field(DATASET_DEFAULTS["VAL_SIZE"], 
                        description="Validation set size ratio")
    random_state: int = Field(DATASET_DEFAULTS["RANDOM_SEED"], 
                          description="Random seed for reproducibility")
    imbalanced: bool = Field(False, description="Whether to generate imbalanced dataset")

    @model_validator(mode='after')
    def validate_splits(self) -> 'BaseConfig':
        """Validate dataset split ratios."""
        total_split = self.test_size + self.val_size
        if total_split >= 1:
            logger.error(f"Invalid split ratios: test_size={self.test_size}, val_size={self.val_size}, total={total_split}")
            raise RangeError("total split ratio", total_split, max_val=1.0)
            
        if self.positive_ratio <= 0 or self.positive_ratio >= 1:
            logger.error(f"Invalid positive ratio: {self.positive_ratio}")
            raise RangeError("positive_ratio", self.positive_ratio, min_val=0.0, max_val=1.0)
            
        logger.debug("Validated dataset split ratios successfully")
        return self

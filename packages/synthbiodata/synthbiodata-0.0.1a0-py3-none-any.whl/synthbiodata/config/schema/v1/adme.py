"""
Configuration schema for ADME data (version 1.0).
"""

from pydantic import Field, model_validator

from synthbiodata.constants import ADME_DEFAULTS
from synthbiodata.exceptions import RangeError
from synthbiodata.logging import logger
from synthbiodata.config.base import BaseConfig

class ADMEConfig(BaseConfig):
    """Configuration for ADME data generation."""
    # Absorption
    absorption_mean: float = Field(ADME_DEFAULTS["ABSORPTION_MEAN"], 
                               description="Mean absorption percentage")
    absorption_std: float = Field(ADME_DEFAULTS["ABSORPTION_STD"], 
                              description="Standard deviation of absorption")
    
    # Distribution
    plasma_protein_binding_mean: float = Field(ADME_DEFAULTS["PROTEIN_BINDING_MEAN"], 
                                           description="Mean plasma protein binding percentage")
    plasma_protein_binding_std: float = Field(ADME_DEFAULTS["PROTEIN_BINDING_STD"], 
                                          description="Standard deviation of plasma protein binding")
    
    # Metabolism
    clearance_mean: float = Field(ADME_DEFAULTS["CLEARANCE_MEAN"], 
                              description="Mean clearance rate (L/h)")
    clearance_std: float = Field(ADME_DEFAULTS["CLEARANCE_STD"], 
                             description="Standard deviation of clearance")
    half_life_mean: float = Field(ADME_DEFAULTS["HALF_LIFE_MEAN"], 
                              description="Mean half-life (hours)")
    half_life_std: float = Field(ADME_DEFAULTS["HALF_LIFE_STD"], 
                             description="Standard deviation of half-life")
    
    # Excretion
    renal_clearance_ratio: float = Field(ADME_DEFAULTS["RENAL_CLEARANCE_RATIO"], 
                                     description="Ratio of renal to total clearance")

    @model_validator(mode='after')
    def validate_parameters(self) -> 'ADMEConfig':
        """Validate ADME parameters and standard deviations."""
        # Percentage: Parameters that must be between 0 and 100
        percentage_params = [
            ('absorption_mean', self.absorption_mean),
            ('plasma_protein_binding_mean', self.plasma_protein_binding_mean)
        ]
        for param, value in percentage_params:
            if value < 0 or value > 100:
                logger.error(f"Invalid {param}: {value}")
                raise RangeError(param, value, min_val=0, max_val=100)

        # Means: Parameters that must be positive
        positive_means = [
            ('clearance_mean', self.clearance_mean),
            ('half_life_mean', self.half_life_mean)
        ]
        for param, value in positive_means:
            if value <= 0:
                logger.error(f"Invalid {param}: {value}")
                raise RangeError(param, value, min_val=0)

        # Ratios: Parameters that must be between 0 and 1
        ratio_params = [
            ('renal_clearance_ratio', self.renal_clearance_ratio)
        ]
        for param, value in ratio_params:
            if value < 0 or value > 1:
                logger.error(f"Invalid {param}: {value}")
                raise RangeError(param, value, min_val=0, max_val=1)

        # All standard deviations must be positive
        std_params = [
            ('absorption_std', self.absorption_std),
            ('plasma_protein_binding_std', self.plasma_protein_binding_std),
            ('clearance_std', self.clearance_std),
            ('half_life_std', self.half_life_std)
        ]
        for param, value in std_params:
            if value <= 0:
                logger.error(f"Invalid {param}: {value}")
                raise RangeError(param, value, min_val=0)
            
        logger.debug("Validated ADME parameters successfully")
        return self

"""
Configuration schema for molecular descriptor data (version 1.0).
"""

from pydantic import Field, model_validator

from synthbiodata.constants import MOLECULAR_DEFAULTS, TARGET_FAMILIES, TARGET_FAMILY_PROBS
from synthbiodata.exceptions import RangeError, DistributionError
from synthbiodata.logging import logger
from synthbiodata.config.base import BaseConfig

class MolecularConfig(BaseConfig):
    """
    Configuration schema for molecular descriptor data.

    This class defines the configuration options for generating synthetic molecular
    descriptor data, including ranges and distributions for molecular weight (MW),
    LogP, and TPSA, as well as target protein family probabilities.

    Parameters
    ----------
    mw_mean : float
        Mean molecular weight of generated molecules.
    mw_std : float
        Standard deviation of molecular weight.
    mw_min : float
        Minimum allowed molecular weight.
    mw_max : float
        Maximum allowed molecular weight.
    logp_mean : float
        Mean LogP (octanol-water partition coefficient) value.
    logp_std : float
        Standard deviation of LogP.
    logp_min : float
        Minimum allowed LogP value.
    logp_max : float
        Maximum allowed LogP value.
    tpsa_mean : float
        Mean topological polar surface area (TPSA) value.
    tpsa_std : float
        Standard deviation of TPSA.
    tpsa_min : float
        Minimum allowed TPSA value.
    tpsa_max : float
        Maximum allowed TPSA value.
    target_families : list of str
        List of target protein families to sample from.
    target_family_probs : list of float
        Probability distribution for selecting each target family.

    Examples
    --------
    >>> config = MolecularConfig()
    >>> config.mw_mean
    350.0
    >>> config.target_families
    ['GPCR', 'Kinase', 'Protease', 'Ion Channel', 'Nuclear Receptor']
    """
    # Molecular descriptor ranges
    mw_mean: float = Field(MOLECULAR_DEFAULTS["MW_MEAN"], 
                        description="Mean molecular weight")
    mw_std: float = Field(MOLECULAR_DEFAULTS["MW_STD"], 
                       description="Standard deviation of molecular weight")
    mw_min: float = Field(MOLECULAR_DEFAULTS["MW_MIN"], 
                       description="Minimum molecular weight")
    mw_max: float = Field(MOLECULAR_DEFAULTS["MW_MAX"], 
                       description="Maximum molecular weight")
    
    logp_mean: float = Field(MOLECULAR_DEFAULTS["LOGP_MEAN"], 
                          description="Mean LogP value")
    logp_std: float = Field(MOLECULAR_DEFAULTS["LOGP_STD"], 
                         description="Standard deviation of LogP")
    logp_min: float = Field(MOLECULAR_DEFAULTS["LOGP_MIN"], 
                         description="Minimum LogP value")
    logp_max: float = Field(MOLECULAR_DEFAULTS["LOGP_MAX"], 
                         description="Maximum LogP value")
    
    tpsa_mean: float = Field(MOLECULAR_DEFAULTS["TPSA_MEAN"], 
                          description="Mean TPSA value")
    tpsa_std: float = Field(MOLECULAR_DEFAULTS["TPSA_STD"], 
                         description="Standard deviation of TPSA")
    tpsa_min: float = Field(MOLECULAR_DEFAULTS["TPSA_MIN"], 
                         description="Minimum TPSA value")
    tpsa_max: float = Field(MOLECULAR_DEFAULTS["TPSA_MAX"], 
                         description="Maximum TPSA value")
    
    # Target protein families
    target_families: list[str] = Field(
        default=TARGET_FAMILIES,
        description="List of target protein families"
    )
    target_family_probs: list[float] = Field(
        default=TARGET_FAMILY_PROBS,
        description="Probability distribution for target families"
    )

    @model_validator(mode='after')
    def validate_ranges(self) -> 'MolecularConfig':
        """Validate molecular descriptor ranges and standard deviations."""
        # Validate min/max ranges
        for param in ['mw', 'logp', 'tpsa']:
            min_val = getattr(self, f"{param}_min")
            max_val = getattr(self, f"{param}_max")
            if min_val >= max_val:
                logger.error(f"Invalid {param} range: min={min_val}, max={max_val}")
                raise RangeError(f"{param}_min", min_val, max_val=max_val)
                
        # Validate standard deviations
        for param in ['mw', 'logp', 'tpsa']:
            std_val = getattr(self, f"{param}_std")
            if std_val <= 0:
                logger.error(f"Invalid {param} standard deviation: {std_val}")
                raise RangeError(f"{param}_std", std_val, min_val=0)

        # Validate target distributions
        if len(self.target_families) != len(self.target_family_probs):
            logger.error(
                f"Mismatched lengths: target_families={len(self.target_families)}, "
                f"target_family_probs={len(self.target_family_probs)}"
            )
            raise DistributionError(
                f"Length mismatch: target_families ({len(self.target_families)}) "
                f"!= target_family_probs ({len(self.target_family_probs)})"
            )
            
        prob_sum = sum(self.target_family_probs)
        if abs(prob_sum - 1.0) > 1e-6:
            logger.error(f"Target family probabilities sum to {prob_sum}, should be 1.0")
            raise DistributionError(
                f"Target family probabilities must sum to 1.0, got {prob_sum}"
            )
            
        logger.debug("Validated molecular descriptor ranges successfully")
        return self

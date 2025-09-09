"""Tests for molecular configuration schema."""

import pytest
from synthbiodata.config.schema.v1.molecular import MolecularConfig
from synthbiodata.exceptions import RangeError, DistributionError

@pytest.fixture
def molecular_config():
    """Create a molecular configuration for testing."""
    return MolecularConfig()

def test_molecular_config_defaults(molecular_config):
    """Test MolecularConfig default values."""
    # Check molecular weight parameters
    assert molecular_config.mw_mean == 350.0
    assert molecular_config.mw_std == 100.0
    assert molecular_config.mw_min == 150.0
    assert molecular_config.mw_max == 600.0
    
    # Check target families
    assert len(molecular_config.target_families) == 5
    assert len(molecular_config.target_family_probs) == 5
    assert abs(sum(molecular_config.target_family_probs) - 1.0) < 1e-6

def test_molecular_config_validation():
    """Test MolecularConfig validation rules with custom exceptions."""
    # Test invalid molecular weight range
    with pytest.raises(RangeError, match="mw_min must be less than 300.0, got 400.0"):
        MolecularConfig(mw_min=400.0, mw_max=300.0)
    
    # Test invalid target family probabilities
    with pytest.raises(DistributionError, match="Target family probabilities must sum to 1.0, got 1.6"):
        MolecularConfig(
            target_families=['A', 'B'],
            target_family_probs=[0.8, 0.8]
        )
    
    # Test mismatched lengths
    with pytest.raises(DistributionError, 
                      match="Length mismatch: target_families \\(2\\) != target_family_probs \\(1\\)"):
        MolecularConfig(
            target_families=['A', 'B'],
            target_family_probs=[1.0]
        )

@pytest.mark.parametrize("param,value", [
    ("mw_std", 0.0),
    ("logp_std", -1.0),
    ("tpsa_std", 0.0)
])
def test_molecular_config_validation_invalid_standard_deviations(param, value):
    """Test that MolecularConfig rejects invalid standard deviations."""
    with pytest.raises(RangeError, match=f"{param} must be greater than 0, got {value}"):
        MolecularConfig(**{param: value})

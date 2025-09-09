"""Tests for ADME configuration schema."""

import pytest
from synthbiodata.config.schema.v1.adme import ADMEConfig
from synthbiodata.exceptions import RangeError

@pytest.fixture
def adme_config():
    """Create an ADME configuration for testing."""
    return ADMEConfig()

def test_adme_config_defaults(adme_config):
    """Test ADMEConfig default values."""
    # absorption params
    assert adme_config.absorption_mean == 70.0
    assert adme_config.absorption_std == 20.0
    
    # metabolism params
    assert adme_config.clearance_mean == 5.0
    assert adme_config.half_life_mean == 12.0

@pytest.mark.parametrize("param,value", [
    ("absorption_mean", 150.0),
    ("plasma_protein_binding_mean", -10.0)
])
def test_adme_config_validation_invalid_percentages(param, value):
    """Test that ADMEConfig rejects invalid percentage parameters."""
    with pytest.raises(RangeError, match=f"{param} must be between 0 and 100, got {value}"):
        ADMEConfig(**{param: value})

@pytest.mark.parametrize("param,value", [
    ("clearance_mean", -1.0),
    ("half_life_mean", 0.0)
])
def test_adme_config_validation_invalid_means(param, value):
    """Test that ADMEConfig rejects invalid mean parameters."""
    with pytest.raises(RangeError, match=f"{param} must be greater than 0, got {value}"):
        ADMEConfig(**{param: value})

@pytest.mark.parametrize("param,value", [
    ("renal_clearance_ratio", -0.1),
    ("renal_clearance_ratio", 1.5)
])
def test_adme_config_validation_invalid_ratios(param, value):
    """Test that ADMEConfig rejects invalid ratio parameters."""
    with pytest.raises(RangeError, match=f"{param} must be between 0 and 1, got {value}"):
        ADMEConfig(**{param: value})

@pytest.mark.parametrize("param,value", [
    ("absorption_std", 0.0),
    ("plasma_protein_binding_std", -1.0),
    ("clearance_std", 0.0),
    ("half_life_std", -2.0)
])
def test_adme_config_validation_invalid_standard_deviations(param, value):
    """Test that ADMEConfig rejects invalid standard deviations."""
    with pytest.raises(RangeError, match=f"{param} must be greater than 0, got {value}"):
        ADMEConfig(**{param: value})


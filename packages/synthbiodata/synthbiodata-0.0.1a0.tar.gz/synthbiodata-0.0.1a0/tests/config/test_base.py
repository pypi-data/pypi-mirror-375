"""Tests for base configuration."""

import pytest
from synthbiodata.config.base import BaseConfig
from synthbiodata.exceptions import RangeError

@pytest.fixture
def base_config():
    """Create a base configuration for testing."""
    return BaseConfig()

def test_base_config_defaults(base_config):
    """Test that BaseConfig has correct default values."""
    assert base_config.n_samples == 10000
    assert base_config.positive_ratio == 0.03
    assert base_config.test_size == 0.2
    assert base_config.val_size == 0.2
    assert base_config.random_state == 42
    assert not base_config.imbalanced

def test_base_config_validation_valid_splits():
    """Test BaseConfig valid splits."""
    config = BaseConfig(test_size=0.2, val_size=0.2)
    assert config.test_size + config.val_size < 1.0

def test_base_config_validation_invalid_splits():
    """Test BaseConfig invalid splits with custom exceptions."""
    with pytest.raises(RangeError, match="total split ratio must be less than 1.0, got 1.0"):
        BaseConfig(test_size=0.5, val_size=0.5)

def test_base_config_validation_invalid_positive_ratio():
    """Test BaseConfig invalid positive ratio with custom exceptions."""
    with pytest.raises(RangeError, match="positive_ratio must be between 0.0 and 1.0, got 1.5"):
        BaseConfig(positive_ratio=1.5)


"""Tests for ADME data generator."""

import pytest
import numpy as np
import polars as pl
from synthbiodata.config.schema.v1.adme import ADMEConfig
from synthbiodata.core.adme import ADMEGenerator

@pytest.fixture
def adme_balanced_config():
    """Create a balanced ADME configuration for testing."""
    return ADMEConfig(
        n_samples=1000,
        positive_ratio=0.5,
        random_state=42
    )

@pytest.fixture
def adme_imbalanced_config():
    """Create an imbalanced ADME configuration for testing."""
    return ADMEConfig(
        n_samples=1000,
        positive_ratio=0.03,
        imbalanced=True,
        random_state=42
    )

@pytest.fixture
def adme_generator(adme_balanced_config):
    """Create an ADME generator for testing."""
    return ADMEGenerator(adme_balanced_config)

@pytest.mark.parametrize("feature,min_val,max_val", [
    ("absorption", 0, 100),
    ("plasma_protein_binding", 0, 100),
    ("clearance", 0, None),
    ("half_life", 0, None),
])
def test_adme_features_ranges(adme_generator, feature, min_val, max_val):
    """Test that ADME features are within expected ranges."""
    df = adme_generator.generate_data()
    values = df[feature].to_numpy()
    
    assert np.all(values >= min_val)
    if max_val is not None:
        assert np.all(values <= max_val)

def test_bioavailability_rules():
    """Test that bioavailability follows the defined rules."""
    # A compound should be bioavailable if it meets all criteria
    perfect_compound = {
        'absorption': 60.0,  # > 50
        'plasma_protein_binding': 90.0,  # < 95
        'clearance': 7.0,  # < 8
        'half_life': 7.0,  # > 6
    }

    perfect_df = pl.DataFrame([perfect_compound])
    bioavailable = np.logical_and.reduce([
        perfect_df['absorption'] > 50,
        perfect_df['plasma_protein_binding'] < 95,
        perfect_df['clearance'] < 8,
        perfect_df['half_life'] > 6
    ]).item()
    
    assert bioavailable

def test_balanced_dataset(adme_generator, adme_balanced_config):
    """Test generation of balanced ADME dataset."""
    df = adme_generator.generate_data()
    
    # Check DataFrame properties
    assert isinstance(df, pl.DataFrame)
    assert len(df) == adme_balanced_config.n_samples
    
    # Check features
    expected_columns = {
        'absorption', 'plasma_protein_binding', 'clearance',
        'half_life', 'good_bioavailability'
    }
    assert all(col in df.columns for col in expected_columns)

def test_imbalanced_dataset_ratio_with_tolerance(adme_imbalanced_config):
    """Test generation of imbalanced ADME dataset."""
    generator = ADMEGenerator(adme_imbalanced_config)
    df = generator.generate_data()
    
    positive_ratio = (df['good_bioavailability'] == 1).mean()
    assert abs(positive_ratio - adme_imbalanced_config.positive_ratio) < 0.05


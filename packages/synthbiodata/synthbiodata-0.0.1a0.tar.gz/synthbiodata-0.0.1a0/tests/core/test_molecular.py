"""Tests for molecular data generator."""

import pytest
import numpy as np
import polars as pl
from synthbiodata.config.schema.v1.molecular import MolecularConfig
from synthbiodata.core.molecular import MolecularGenerator

@pytest.fixture
def molecular_balanced_config():
    """Create a balanced molecular configuration for testing."""
    return MolecularConfig(
        n_samples=1000,
        positive_ratio=0.5,
        random_state=42
    )

@pytest.fixture
def molecular_imbalanced_config():
    """Create an imbalanced molecular configuration for testing."""
    return MolecularConfig(
        n_samples=1000,
        positive_ratio=0.03,
        imbalanced=True,
        random_state=42
    )

@pytest.fixture
def molecular_generator(molecular_balanced_config):
    """Create a molecular generator for testing."""
    return MolecularGenerator(molecular_balanced_config)

@pytest.mark.parametrize("descriptor,min_attr,max_attr", [
    ("molecular_weight", "mw_min", "mw_max"),
    ("logp", "logp_min", "logp_max"),
    ("tpsa", "tpsa_min", "tpsa_max"),
])
def test_molecular_descriptors_ranges(molecular_generator, molecular_balanced_config, descriptor, min_attr, max_attr):
    """Test that generated molecular descriptors are within expected ranges."""
    descriptors = molecular_generator._generate_molecular_descriptors(molecular_balanced_config.n_samples)
    
    min_val = getattr(molecular_balanced_config, min_attr)
    max_val = getattr(molecular_balanced_config, max_attr)
    
    assert np.all(descriptors[descriptor] >= min_val)
    assert np.all(descriptors[descriptor] <= max_val)

def test_target_features(molecular_generator, molecular_balanced_config):
    """Test generation of target protein features."""
    features = molecular_generator._generate_target_features(molecular_balanced_config.n_samples)
    
    # target families
    unique_families = np.unique(features['target_family'])
    assert all(family in molecular_balanced_config.target_families for family in unique_families)
    
    # Conservation range
    assert np.all(features['target_conservation'] >= 0.3)
    assert np.all(features['target_conservation'] <= 0.95)

def test_chemical_fingerprints_binary(molecular_generator, molecular_balanced_config):
    """Test that chemical fingerprints are binary."""
    fingerprints = molecular_generator._generate_chemical_fingerprints(
        molecular_balanced_config.n_samples,
        n_fingerprints=5
    )
    for fp in fingerprints.values():
        assert np.all(np.isin(fp, [0, 1]))

def test_binding_probabilities(molecular_generator):
    """Test calculation of binding probabilities."""
    data = {
        'molecular_weight': np.array([400, 200]),  # One in range, one out
        'logp': np.array([2, 5]),  # One in range, one out
        'tpsa': np.array([60, 150]),  # One in range, one out
        'hbd': np.array([3, 7]),  # One good, one bad
        'hba': np.array([8, 12]),  # One good, one bad
        'fingerprint_0': np.array([1, 0]),  # One active, one inactive
        'fingerprint_3': np.array([1, 0]),  # One active, one inactive
        'target_family': np.array(['Kinase', 'GPCR'])  # Both druggable
    }
    
    probs = molecular_generator._calculate_binding_probabilities(data)
    assert len(probs) == 2
    assert np.all((probs >= 0) & (probs <= 1))
    # First compound should have higher probability
    assert probs[0] > probs[1]

def test_balanced_dataset_properties(molecular_generator, molecular_balanced_config):
    """Test generation of balanced dataset."""
    df = molecular_generator.generate_data()
    assert isinstance(df, pl.DataFrame)
    assert len(df) == molecular_balanced_config.n_samples
    
    positive_ratio = (df['binds_target'] == 1).mean()
    assert abs(positive_ratio - molecular_balanced_config.positive_ratio) < 0.1

def test_imbalanced_dataset_properties(molecular_imbalanced_config):
    """Test generation of imbalanced dataset."""
    generator = MolecularGenerator(molecular_imbalanced_config)
    df = generator.generate_data()
    positive_ratio = (df['binds_target'] == 1).mean()
    # We add 5% noise in the generator, so tolerance should account for that
    noise_tolerance = 0.05
    assert np.isclose(positive_ratio, molecular_imbalanced_config.positive_ratio, atol=noise_tolerance)


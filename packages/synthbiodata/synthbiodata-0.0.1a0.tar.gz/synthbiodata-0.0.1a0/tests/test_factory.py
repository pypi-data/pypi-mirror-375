"""Tests for factory functions."""

import pytest
from synthbiodata.config.schema.v1.molecular import MolecularConfig
from synthbiodata.config.schema.v1.adme import ADMEConfig
from synthbiodata.factory import create_config, generate_sample_data
from synthbiodata.exceptions import DataTypeError

def test_create_config_molecular_descriptors():
    """Test config factory function for molecular descriptors."""
    mol_config = create_config("molecular-descriptors")
    assert isinstance(mol_config, MolecularConfig)
    
def test_create_config_adme():
    """Test config factory function for adme."""
    adme_config = create_config("adme")
    assert isinstance(adme_config, ADMEConfig)

def test_create_config_adme_imbalanced():   
    """Test config factory function for adme imbalanced."""
    imbal_config = create_config("molecular-descriptors", imbalanced=True)
    assert imbal_config.imbalanced
    assert imbal_config.positive_ratio == 0.03
    
def test_create_config_molecular_descriptors_custom():
    """Test config factory function with custom parameters."""
    custom_config: MolecularConfig = create_config(
        "molecular-descriptors",
        n_samples=5000,
        mw_mean=400.0,
        target_families=['A', 'B'],
        target_family_probs=[0.6, 0.4]
    )
    assert isinstance(custom_config, MolecularConfig)  # Type assertion
    assert custom_config.n_samples == 5000
    assert custom_config.mw_mean == 400.0
    assert custom_config.target_families == ['A', 'B']
    assert custom_config.target_family_probs == [0.6, 0.4]

def test_config_unimplemented_data_types():
    """Test that unimplemented data types raise appropriate errors."""
    with pytest.raises(DataTypeError, match="'something-unexistent' is not a valid DataType"):
        create_config(data_type="something-unexistent")
    
def test_generate_sample_data_unimplemented_data_types():
    """Test that generate_sample_data raises error for unimplemented types."""
    with pytest.raises(DataTypeError, match="'something-unexistent' is not a valid DataType"):
        generate_sample_data(data_type="something-unexistent")

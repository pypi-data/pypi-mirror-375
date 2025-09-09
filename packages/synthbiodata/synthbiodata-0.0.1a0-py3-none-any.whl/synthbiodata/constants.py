"""
Constants used to generate synthetic biological data.

This module contains all the constant values used in data generation and configuration.
"""

# Dataset configuration constants
DATASET_DEFAULTS = {
    "TEST_SIZE": 0.2,
    "VAL_SIZE": 0.2,
    "DEFAULT_SAMPLES": 10000,
    "IMBALANCED_RATIO": 0.03,
    "RANDOM_SEED": 42,
}

# Molecular descriptor defaults based on drug-like molecule statistics
MOLECULAR_DEFAULTS = {
    "MW_MEAN": 350.0,
    "MW_STD": 100.0,
    "MW_MIN": 150.0,
    "MW_MAX": 600.0,
    
    "LOGP_MEAN": 2.5,
    "LOGP_STD": 1.5,
    "LOGP_MIN": -2.0,
    "LOGP_MAX": 6.0,
    
    "TPSA_MEAN": 80.0,
    "TPSA_STD": 40.0,
    "TPSA_MIN": 0.0,
    "TPSA_MAX": 200.0,
}

# ADME (Absorption, Distribution, Metabolism, Excretion) defaults
ADME_DEFAULTS = {
    "ABSORPTION_MEAN": 70.0,
    "ABSORPTION_STD": 20.0,
    
    "PROTEIN_BINDING_MEAN": 85.0,
    "PROTEIN_BINDING_STD": 15.0,
    
    "CLEARANCE_MEAN": 5.0,
    "CLEARANCE_STD": 2.0,
    "HALF_LIFE_MEAN": 12.0,
    "HALF_LIFE_STD": 6.0,
    
    "RENAL_CLEARANCE_RATIO": 0.3,
}

# Target protein family distribution (common drug targets)
TARGET_FAMILIES = [
    'GPCR',
    'Kinase',
    'Protease',
    'Nuclear Receptor',
    'Ion Channel',
]

# Probability distribution for target families
TARGET_FAMILY_PROBS = [0.3, 0.25, 0.2, 0.15, 0.1]

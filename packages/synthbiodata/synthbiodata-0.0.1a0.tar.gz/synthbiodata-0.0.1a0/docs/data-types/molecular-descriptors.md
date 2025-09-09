# Molecular Descriptors

!!! warning 
    This page offers a concise overview of molecular descriptors for reference purposes on how `synthbiodata` generates datasets for each property. It is **not** intended to be a comprehensive educational resource or a detailed scientific guide.

Molecular descriptors are numerical values that characterize the structural and physicochemical properties of chemical compounds. These descriptors are essential in drug discovery, cheminformatics, and machine learning applications for predicting biological activity, drug-likeness, and other molecular properties.

## Physical Properties

Physical properties describe the fundamental characteristics of molecules that affect their behavior in biological systems.

### Molecular Weight

Molecular weight (MW) is the sum of atomic weights of all atoms in a molecule, typically expressed in Daltons (Da). It's a crucial parameter in drug discovery as it affects:

- **Membrane permeability**: Larger molecules have difficulty crossing biological membranes
- **Oral bioavailability**: Very large molecules are poorly absorbed
- **Drug-likeness**: Most successful drugs fall within specific molecular weight ranges
- **Synthetic accessibility**: Larger molecules are often more difficult to synthesize

### LogP (Lipophilicity)

LogP (logarithm of the octanol-water partition coefficient) measures a compound's lipophilicity - its tendency to dissolve in organic solvents versus water. LogP is critical for:

- **Membrane permeability**: Lipophilic compounds cross membranes more easily
- **Oral absorption**: Optimal LogP ranges improve bioavailability
- **Drug distribution**: Affects how drugs distribute throughout the body
- **Toxicity**: High LogP can lead to accumulation in fatty tissues

### TPSA (Topological Polar Surface Area)

TPSA is the sum of surface areas of polar atoms (N, O, S, P) in a molecule. It's a key predictor of:

- **Blood-brain barrier penetration**: Low TPSA facilitates CNS drug delivery
- **Oral bioavailability**: High TPSA often correlates with poor absorption
- **Drug-likeness**: Optimal TPSA ranges improve drug-like properties
- **Solubility**: Affects aqueous solubility and formulation

### SynthBioData - Physical Properties

How does synthbiodata generate data for physical properties?

| Feature                    | Description                                                                                                    |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| **Statistical Modeling**   | Uses normal distributions with configurable mean and standard deviation parameters for MW, LogP, and TPSA     |
| **Realistic Ranges**       | Default values: MW (350±100 Da), LogP (2.5±1.5), TPSA (80±40 Å²) based on drug-like molecule statistics     |
| **Clipping Validation**    | Ensures values stay within biologically meaningful ranges (MW: 150-600, LogP: -2 to 6, TPSA: 0-200)         |
| **Drug-like Properties**   | Ranges optimized for compounds with good drug-like characteristics                                             |
| **Reproducible Generation**| Uses seeded random number generation for consistent results                                                    |

## Structural Features

Structural features describe the molecular architecture and bonding patterns that influence biological activity.

### Hydrogen Bond Donors (HBD)

Hydrogen bond donors are atoms (typically N-H or O-H groups) that can donate hydrogen bonds. They affect:

- **Protein binding**: Form hydrogen bonds with target proteins
- **Solubility**: Increase aqueous solubility
- **Membrane permeability**: Can decrease passive diffusion
- **Drug-likeness**: Optimal HBD counts improve bioavailability

### Hydrogen Bond Acceptors (HBA)

Hydrogen bond acceptors are atoms (N, O, S) that can accept hydrogen bonds. They influence:

- **Protein interactions**: Form hydrogen bonds with binding sites
- **Solubility**: Increase water solubility
- **Lipinski's Rule of Five**: HBA count is a key drug-likeness parameter
- **Molecular recognition**: Critical for specific protein binding

### Rotatable Bonds

Rotatable bonds are single bonds that can rotate freely, affecting molecular flexibility. They impact:

- **Conformational flexibility**: More rotatable bonds increase flexibility
- **Binding entropy**: Flexible molecules may have higher binding entropy
- **Drug-likeness**: Too many rotatable bonds can reduce bioavailability
- **Synthetic complexity**: More rotatable bonds often mean more complex synthesis

### Aromatic Rings

Aromatic rings are cyclic structures with delocalized π-electrons. They contribute to:

- **Protein binding**: Often form π-π interactions with aromatic amino acids
- **Molecular rigidity**: Provide structural stability
- **Drug-likeness**: Most drugs contain aromatic rings
- **Pharmacophore features**: Common in bioactive compounds

### SynthBioData - Structural Features

SynthBioData generates synthetic structural features by:

| Feature                    | Description                                                                                                    |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| **Poisson Distributions**  | Uses Poisson distributions for discrete counts (HBD: λ=2, HBA: λ=5, rotatable bonds: λ=6, aromatic rings: λ=2) |
| **Realistic Counts**       | Default parameters based on typical drug-like molecule statistics                                              |
| **Discrete Values**        | Generates integer counts appropriate for structural features                                                   |
| **Statistical Consistency**| Maintains realistic distribution patterns for molecular diversity                                              |
| **Configurable Parameters**| Allows adjustment of Poisson parameters for different compound classes                                        |

## Chemical Properties

Chemical properties describe the electronic and chemical characteristics that influence molecular behavior.

### Formal Charge

Formal charge is the charge assigned to an atom in a molecule, assuming equal sharing of electrons in covalent bonds. It affects:

- **Ionization state**: Determines whether molecules are charged at physiological pH
- **Solubility**: Charged molecules are more water-soluble
- **Membrane permeability**: Charged species cross membranes poorly
- **Protein binding**: Electrostatic interactions with binding sites

### SynthBioData - Chemical Properties

SynthBioData generates synthetic chemical properties by:

| Feature                    | Description                                                                                                    |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| **Weighted Choice**        | Uses weighted random choice from discrete values (-2, -1, 0, 1, 2) with probabilities (0.05, 0.15, 0.6, 0.15, 0.05) |
| **Realistic Distribution** | Neutral molecules (charge=0) are most common (60%), with decreasing probability for charged species        |
| **Discrete Values**        | Generates integer formal charges appropriate for drug-like molecules                                          |
| **Statistical Validation** | Ensures probability weights sum to 1.0 for proper distribution                                               |
| **Configurable Parameters**| Allows customization of charge distributions for different compound types                                     |

## Target Information

Target information describes the biological targets and binding characteristics that influence drug activity.

### Target Protein Families

Target families are groups of related proteins that share structural and functional similarities. Common families include:

- **GPCRs (G-Protein Coupled Receptors)**: Largest family of drug targets
- **Kinases**: Enzymes that phosphorylate proteins, important in cancer therapy
- **Proteases**: Enzymes that cleave proteins, targets for various diseases
- **Nuclear Receptors**: Transcription factors that regulate gene expression
- **Ion Channels**: Membrane proteins that control ion flow

### Target Conservation

Target conservation measures how conserved a binding site is across different species or protein variants. It affects:

- **Selectivity**: Highly conserved sites may be less selective
- **Drug resistance**: Variable sites may develop resistance mutations
- **Cross-species activity**: Conservation affects translation from animal models
- **Binding affinity**: Conservation often correlates with binding strength

### Binding Site Size

Binding site size describes the volume or surface area of the protein binding pocket. It influences:

- **Ligand size requirements**: Larger sites accommodate bigger molecules
- **Selectivity**: Size constraints can improve selectivity
- **Drug design**: Affects the size of drug candidates
- **Binding affinity**: Larger sites may have different binding characteristics

### SynthBioData - Target Information

SynthBioData generates synthetic target information by:

| Feature                    | Description                                                                                                    |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| **Weighted Family Selection** | Uses configurable target families and probabilities (default: GPCR 30%, Kinase 25%, Protease 20%, etc.)    |
| **Uniform Conservation**   | Generates target conservation values uniformly distributed between 0.3 and 0.95                                 |
| **Normal Distribution**    | Uses normal distribution for binding site size (mean=500, std=150) with realistic protein pocket dimensions   |
| **Configurable Parameters**| Allows customization of family probabilities and conservation ranges                                           |
| **Statistical Validation** | Ensures family probabilities sum to 1.0 and conservation values are within valid ranges                       |

## Chemical Fingerprints

Chemical fingerprints are binary vectors that encode molecular structure information for machine learning applications.

### Fingerprint Generation

Chemical fingerprints represent molecular features as binary strings where each bit indicates the presence or absence of a specific structural feature. They are used for:

- **Similarity searching**: Finding structurally similar compounds
- **Machine learning**: Feature vectors for predictive models
- **Clustering**: Grouping similar molecules
- **Virtual screening**: Rapid filtering of compound libraries

### SynthBioData - Chemical Fingerprints

SynthBioData generates synthetic chemical fingerprints by:

| Feature                    | Description                                                                                                    |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| **Binary Generation**      | Uses binomial distribution (n=1, p=0.3) to generate binary fingerprints with 30% probability of feature presence |
| **Configurable Count**     | Default 10 fingerprint features, customizable for different applications                                       |
| **Independent Features**   | Each fingerprint bit is generated independently for molecular diversity                                        |
| **Machine Learning Ready** | Binary format suitable for ML algorithms and similarity calculations                                          |
| **Reproducible Generation**| Uses seeded random number generation for consistent fingerprint patterns                                      |

## Binding Probability Calculation

SynthBioData calculates realistic binding probabilities based on molecular properties to create meaningful target labels.

### Binding Probability Factors

The binding probability calculation considers multiple molecular properties:

- **Molecular weight**: Optimal range for drug-like molecules
- **LogP**: Lipophilicity affects membrane permeability and binding
- **TPSA**: Polar surface area influences bioavailability
- **Structural features**: HBD, HBA, and aromatic rings affect binding
- **Target characteristics**: Conservation and binding site size influence binding

### SynthBioData - Binding Probability

SynthBioData calculates synthetic binding probabilities by:

| Feature                    | Description                                                                                                    |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| **Multi-factor Model**     | Combines multiple molecular properties using weighted scoring functions                                       |
| **Realistic Thresholds**   | Uses biologically meaningful thresholds for drug-like properties                                              |
| **Target-specific Scoring**| Adjusts probabilities based on target family and conservation characteristics                                 |
| **Binary Classification**  | Creates binary binding labels (binds/doesn't bind) for machine learning applications                          |
| **Configurable Parameters**| Allows adjustment of scoring weights and thresholds for different target types                                |

## Molecular Descriptors in Drug Discovery

Understanding molecular descriptors is crucial throughout drug discovery:

**Hit Identification**: Screening compounds with favorable descriptor profiles
**Lead Optimization**: Modifying structures to improve drug-like properties
**ADMET Prediction**: Using descriptors to predict absorption, distribution, metabolism, excretion, and toxicity
**Machine Learning**: Training models to predict biological activity from molecular structure

Molecular descriptors are fundamental to modern drug discovery, making synthetic molecular descriptor data generation valuable for:
- Training machine learning models for drug discovery
- Testing molecular property prediction algorithms
- Educational purposes in cheminformatics
- Research and development in pharmaceutical sciences

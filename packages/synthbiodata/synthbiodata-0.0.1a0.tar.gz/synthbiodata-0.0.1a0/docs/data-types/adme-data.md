# ADME Data

!!! warning 
    This page offers a concise overview of ADME data for reference purposes on how `synthbiodata` generates datasets for molecular properties. It is **not** intended to be a comprehensive educational resource or a detailed scientific guide.

When developing and testing new drugs, it is essential to understand how a compound behaves within the body to evaluate its safety and potential toxicity.

ADME stands for Absorption, Distribution, Metabolism, and Excretion. These studies focus on how a substance (such as a drug candidate) is taken up, processed, and eliminated by a living organism.

## Absorption

Absorption refers to the process by which a chemical enters the body, specifically the movement of a substance from the site of administration into the bloodstream.

There are four primary ways a substance can be administered:

- Ingestion (through the digestive tract)
- Inhalation (via the respiratory system)
- Dermal application (to the skin or eyes)
- Injection (directly into the bloodstream)

Of these, only injection delivers the compound straight into systemic circulation. For drugs given by ingestion, inhalation, or dermal routes, the substance must first cross a biological membrane before reaching the bloodstream.

The rate and extent of absorption depend on several factors:

- **Physicochemical properties** of the compound (molecular weight, lipophilicity, ionization)
- **Route of administration** and formulation
- **Physiological factors** (pH, blood flow, surface area)
- **First-pass metabolism** in the liver or gut wall

### SynthBioData - Absortion

How does synthbiodata generates data for absortion?

| Feature                    | Description                                                                                                    |
|----------------------------|----------------------------------------------------------------------------------------------------------------|
| **Statistical Modeling**   | Uses normal distributions with configurable mean and standard deviation parameters (`absorption_mean`, `absorption_std`) |
| **Realistic Ranges**       | Default values (70% ± 20%) based on typical oral drug absorption patterns                                      |
| **Percentage Format**      | Values generated as percentages (0-100%) representing bioavailability                                          |
| **Binary Classification**  | Creates binary labels for "bioavailable" vs "non-bioavailable" based on absorption thresholds                  |
| **Reproducible Generation**| Uses seeded random number generation for consistent results                                                    |

## Distribution

Distribution describes the reversible transfer of a drug from one location to another within the body. Once a drug enters the bloodstream, it is distributed throughout the body via the circulatory system.

### Key Distribution Concepts

**Volume of Distribution (Vd)**: The theoretical volume that would be required to contain the total amount of drug in the body at the same concentration as in plasma. It indicates how extensively a drug is distributed in tissues.

**Plasma Protein Binding**: Many drugs bind to plasma proteins (primarily albumin and α1-acid glycoprotein), which affects their distribution and activity. Only unbound (free) drug can cross membranes and exert pharmacological effects.

**Tissue Distribution**: Drugs distribute differently across various tissues based on:
- Blood flow to the tissue
- Tissue composition and pH
- Drug lipophilicity and molecular size
- Presence of specific transporters or receptors

### Distribution Barriers

- **Blood-Brain Barrier**: Highly selective barrier that protects the central nervous system
- **Placental Barrier**: Regulates drug transfer between mother and fetus
- **Mammary Gland**: Can concentrate certain drugs in breast milk

### SynthBioData - Distribution

SynthBioData generates synthetic distribution with:

| Feature                     | Description                                                                                                      |
|-----------------------------|------------------------------------------------------------------------------------------------------------------|
| **Plasma Protein Binding**  | Uses normal distributions (`plasma_protein_binding_mean`, `plasma_protein_binding_std`) with realistic ranges (85% ± 15%) |
| **Percentage Format**       | Values generated as percentages (0-100%) representing protein binding affinity                                   |
| **Validation**              | Ensures values stay within biologically meaningful ranges (0-100%)                                               |
| **Statistical Consistency** | Maintains realistic distribution patterns based on drug-like molecule properties                                 |
| **Configurable Parameters** | Allows customization of mean and standard deviation for different drug classes                                   |

## Metabolism

Metabolism (biotransformation) is the chemical alteration of a drug by the body, primarily in the liver. The main purpose is to make drugs more water-soluble for easier elimination.

### Factors Affecting Metabolism

- **Age**: Metabolic capacity changes throughout life
- **Genetics**: Genetic polymorphisms in drug-metabolizing enzymes
- **Disease states**: Liver disease significantly affects metabolism
- **Drug interactions**: One drug can inhibit or induce another's metabolism
- **Environmental factors**: Diet, smoking, alcohol consumption

### SynthBioData - Metabolism

SynthBioData generates synthetic metabolism data by:

| Feature                  | Description                                                                                                 |
|--------------------------|-------------------------------------------------------------------------------------------------------------|
| **Clearance Rate**       | Uses normal distributions (`clearance_mean`, `clearance_std`) with realistic pharmacokinetic ranges (5.0 ± 2.0 L/h) |
| **Half-Life**            | Generates half-life values (`half_life_mean`, `half_life_std`) in hours (12.0 ± 6.0 hours)                 |
| **Positive Values**      | Ensures all clearance and half-life values are positive (no negative or zero values)                        |
| **Realistic Ranges**     | Based on typical drug metabolism patterns for small molecules                                               |
| **Statistical Validation** | Validates standard deviations are positive to maintain proper distribution shapes                          |
| **Configurable Parameters** | Allows adjustment of metabolic parameters for different drug types                                       |

## Excretion

Excretion is the elimination of drugs and their metabolites from the body. The primary routes are renal (kidney) and biliary (liver), with minor contributions from other routes.

### Renal Excretion

The kidneys are the most important organs for drug elimination. Renal excretion involves:

**Glomerular Filtration**: Passive filtration of small, unbound molecules through the glomerulus.

**Active Tubular Secretion**: Active transport of drugs from blood into urine via specific transporters (OAT, OCT, P-gp).

**Tubular Reabsorption**: Passive reabsorption of lipophilic drugs back into the bloodstream.

### Clearance

**Clearance** is the volume of plasma from which a drug is completely removed per unit time. It's a key parameter that determines:

- How quickly a drug is eliminated
- Dosing frequency requirements
- Drug accumulation potential

**Total Clearance** = Renal Clearance + Hepatic Clearance + Other Clearances

### Synthbiodata - Excretion

SynthBioData generates synthetic excretion data with:

| Feature/Aspect             | Description                                                                                                 |
|----------------------------|-------------------------------------------------------------------------------------------------------------|
| **Renal Clearance Ratio**  | Uses a fixed ratio parameter (`renal_clearance_ratio`) with default value of 0.3 (30% of total clearance)   |
| **Ratio Validation**       | Ensures the renal clearance ratio is between 0 and 1 (0-100%)                                              |
| **Realistic Proportions**  | Based on typical drug elimination patterns where renal excretion accounts for 20-40% of total clearance     |
| **Mathematical Consistency** | Maintains proper relationships between total clearance and renal clearance                                 |
| **Configurable Parameters**| Allows adjustment of renal clearance ratios for different drug classes                                      |
| **Binary Classification**  | Creates bioavailability labels based on overall ADME profile integration                                    |





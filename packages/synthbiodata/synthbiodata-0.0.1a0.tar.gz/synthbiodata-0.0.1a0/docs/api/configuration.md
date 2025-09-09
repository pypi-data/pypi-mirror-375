# Configuration API

The configuration system provides type-safe configuration classes for data generation.

## Configuration Schemas

### Molecular Configuration

::: synthbiodata.config.schema.v1.molecular.MolecularConfig
    options:
      show_source: true
      show_root_heading: true
      show_root_toc_entry: true
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: false
      members_order: source
      filters: ["!^_"]
      show_signature: true
      show_signature_annotations: true
      show_docstring_description: true
      show_docstring_examples: true
      show_docstring_parameters: true
      show_docstring_other_parameters: true
      show_docstring_raises: true
      show_docstring_warns: true
      show_docstring_yields: true
      show_docstring_returns: true

### ADME Configuration

::: synthbiodata.config.schema.v1.adme.ADMEConfig
    options:
      show_source: true
      show_root_heading: true
      show_root_toc_entry: true
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: false
      members_order: source
      filters: ["!^_"]

## Base Configuration

::: synthbiodata.config.base.BaseConfig
    options:
      show_source: true
      show_root_heading: true
      show_root_toc_entry: true
      show_object_full_path: false
      show_category_heading: true
      show_if_no_docstring: false
      members_order: source
      filters: ["!^_"]

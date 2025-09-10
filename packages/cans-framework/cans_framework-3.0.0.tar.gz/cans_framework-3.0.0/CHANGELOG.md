# Changelog

All notable changes to the CANS framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2024-12-09

### Added - Enhanced Causal Inference
- **Causal Assumption Testing**: Automated testing of unconfoundedness, positivity, and SUTVA assumptions
- **Multiple Identification Strategies**: Backdoor criterion, inverse propensity weighting, and doubly robust estimation
- **CATE Estimation**: X-Learner, T-Learner, S-Learner, Neural CATE, and Causal Forest implementations
- **Uncertainty Quantification**: Bayesian methods, ensemble approaches, and conformal prediction
- **Advanced Graph Construction**: Multi-node, temporal, and global graph architectures
- **Causal-Specific Loss Functions**: CFR, IPW, DragonNet, TARNet with representation balancing
- **Comprehensive Evaluation**: PEHE, policy evaluation, calibration metrics, and bootstrap confidence intervals
- **Memory-Efficient Processing**: Lazy loading and batch processing for large datasets
- **CLI Tools**: Command-line interface for assumption validation and model evaluation
- **Enhanced Documentation**: Complete usage examples and API documentation

### Changed
- **Graph Construction**: Replaced single-node isolated graphs with proper multi-node architectures
- **Counterfactual Simulation**: Enhanced with proper causal identification methods
- **Requirements Format**: Fixed RTF format issue in requirements.txt
- **Package Structure**: Improved modular organization with comprehensive __init__.py
- **Error Handling**: Enhanced with specific causal inference exceptions and validations

### Fixed
- **Dummy Data Generation**: Replaced random dummy data with proper synthetic datasets
- **Graph Connectivity**: Fixed isolated node issues preventing effective message passing
- **Requirements Installation**: Corrected requirements.txt format for pip installation
- **Memory Leaks**: Improved memory management for large-scale processing

## [2.0.0] - 2024-08-27

### Added - Production Readiness
- **Configuration Management**: Centralized, validated configs with JSON/YAML support
- **Enhanced Error Handling**: Comprehensive validation with informative error messages  
- **Logging & Checkpointing**: Built-in experiment tracking with automatic model saving
- **Comprehensive Testing**: 100+ unit tests ensuring production reliability
- **Advanced Data Pipeline**: Multi-format loading (CSV, JSON) with automatic preprocessing
- **Enhanced Training**: Early stopping, gradient clipping, multiple loss functions

### Changed
- **Architecture**: Improved modularity and extensibility
- **Data Loading**: Enhanced preprocessing pipeline with validation
- **Training Loop**: More robust with better monitoring and checkpointing

## [1.0.0] - 2024-06-01

### Added - Initial Release
- **Core Architecture**: GNNs + Transformers + CFRNet integration
- **Basic Causal Inference**: Simple counterfactual outcome prediction
- **Graph Processing**: Basic graph construction and processing
- **Text Processing**: BERT integration for textual data
- **Configuration**: Basic configuration management
- **Examples**: Initial usage examples and documentation

### Framework Components
- **Models**: CANS, GCN, GAT implementations
- **Pipeline**: Basic training and evaluation pipeline  
- **Utilities**: Data loading and basic causal analysis
- **Documentation**: README and basic examples

## [Unreleased]

### Planned Features
- **Distributed Training**: Multi-GPU and multi-node training support
- **Advanced Architectures**: Graph Transformers and attention mechanisms
- **Time Series**: Temporal causal inference capabilities
- **AutoML Integration**: Automated hyperparameter tuning
- **Web Interface**: Browser-based analysis dashboard
- **Cloud Integration**: Support for cloud-based training and deployment
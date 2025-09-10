# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-XX

### Added
- Initial release of rouge-torch
- Fully vectorized PyTorch implementation of ROUGE scores
- Support for ROUGE-1, ROUGE-2, and ROUGE-L metrics
- Differentiable loss function for neural network training
- GPU acceleration and batch processing
- Comprehensive test suite with 14 test cases
- Overfit validation test demonstrating convergence to zero loss
- Memory-efficient algorithms for long sequences
- Approximation methods for very long sequences (>100 tokens)
- Multiple reference support
- Configurable reduction modes (mean, sum, none)
- Type hints and comprehensive documentation
- Example utilities for tokenization and text-to-tensor conversion

### Key Features
- **Performance**: Fully vectorized operations with no Python loops
- **Loss Bounds**: Proper loss bounds [0, N] where N = number of ROUGE types
- **Flexibility**: Works with any tokenizer and vocabulary size
- **Validation**: Extensively tested including overfit convergence validation
- **Documentation**: Comprehensive README with usage examples

### Technical Details
- Requires Python 3.8+
- Requires PyTorch 1.9+
- Memory complexity: O(batch_size × seq_len²) for ROUGE-L
- Time complexity: O(batch_size × seq_len) for ROUGE-N, O(batch_size × seq_len²) for ROUGE-L
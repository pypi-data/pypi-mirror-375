"""
ROUGE-Torch: Fast Differentiable ROUGE Scores for PyTorch
========================================================

A fully vectorized PyTorch implementation of ROUGE scores optimized for training
neural networks. Unlike traditional ROUGE implementations that work with discrete 
tokens, rouge-torch operates directly on logits, making it perfect for use as a 
differentiable loss function in neural text generation models.

Key Features:
- ⚡ Fully Vectorized: Batch processing with no Python loops
- 🔥 GPU Accelerated: Native PyTorch tensors with CUDA support  
- 📈 Differentiable: Can be used as a loss function for training
- 🎯 Multiple ROUGE Types: ROUGE-1, ROUGE-2, ROUGE-L support
- 📊 Proper Loss Bounds: Loss ∈ [0, 1] per metric, with 0 = perfect match

Basic Usage:
-----------
>>> import torch
>>> from rouge_torch import ROUGEScoreTorch
>>> 
>>> # Initialize ROUGE scorer
>>> vocab_size = 10000
>>> device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
>>> rouge_scorer = ROUGEScoreTorch(vocab_size, device)
>>> 
>>> # Your model outputs (batch_size, seq_len, vocab_size)
>>> candidate_logits = torch.randn(4, 20, vocab_size, device=device)
>>> reference_logits = [torch.randn(4, 20, vocab_size, device=device)]
>>> 
>>> # Compute ROUGE scores
>>> rouge_1 = rouge_scorer.rouge_n_batch(candidate_logits, reference_logits, n=1)
>>> print(f"ROUGE-1 F1: {rouge_1['f1'].mean():.3f}")
>>> 
>>> # Use as loss function
>>> loss = rouge_scorer.compute_rouge_loss(candidate_logits, reference_logits)
>>> loss.backward()  # Ready for training!

Classes:
--------
- ROUGEScoreTorch: Main class for computing ROUGE scores and losses

Functions:
----------  
- create_vocab_and_tokenizer: Create simple tokenizer for testing/examples
- text_to_logits: Convert text strings to one-hot logit tensors
"""

__version__ = "0.1.0"
__author__ = "Rouge-Torch Contributors"
__email__ = "contact@rouge-torch.dev"
__license__ = "MIT"

# Import main classes and functions
from .core import ROUGEScoreTorch
from .utils import create_vocab_and_tokenizer, text_to_logits

# Define public API
__all__ = [
    "ROUGEScoreTorch",
    "create_vocab_and_tokenizer", 
    "text_to_logits",
    "__version__",
]

# Package metadata
__package_name__ = "rouge-torch"
__description__ = "Fast differentiable ROUGE scores for PyTorch neural network training"
__url__ = "https://github.com/username/rouge-torch"
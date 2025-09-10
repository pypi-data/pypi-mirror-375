
"""
Utility functions for rouge-torch package.

This module contains helper functions for tokenization, text processing,
and converting between text and tensor representations.
"""

import torch
from typing import Dict, List, Callable, Tuple, Optional


def create_vocab_and_tokenizer() -> Tuple[Dict[str, int], Dict[int, str], Callable, Callable]:
    """Create a simple vocabulary and tokenizer for testing."""
    # Common words for testing
    vocab = {
        "<PAD>": 0,
        "<UNK>": 1,
        "the": 2,
        "cat": 3,
        "sat": 4,
        "on": 5,
        "mat": 6,
        "a": 7,
        "dog": 8,
        "ran": 9,
        "in": 10,
        "park": 11,
        "quick": 12,
        "brown": 13,
        "fox": 14,
        "jumps": 15,
        "over": 16,
        "lazy": 17,
        "is": 18,
        "very": 19,
        "good": 20,
        "bad": 21,
        "big": 22,
        "small": 23,
        "red": 24,
        "blue": 25,
        "green": 26,
        "yellow": 27,
        "house": 28,
        "car": 29,
        "tree": 30,
        "water": 31,
        "food": 32,
        "book": 33,
        "computer": 34,
        "phone": 35,
        "table": 36,
        "chair": 37,
    }

    word_to_id = vocab
    id_to_word = {v: k for k, v in vocab.items()}

    def tokenize(text):
        words = text.lower().split()
        return [word_to_id.get(word, word_to_id["<UNK>"]) for word in words]

    def detokenize(tokens):
        return " ".join(
            [
                id_to_word.get(tok, "<UNK>")
                for tok in tokens
                if tok != word_to_id["<PAD>"]
            ]
        )

    return word_to_id, id_to_word, tokenize, detokenize


def text_to_logits(
    text: str, 
    tokenize_fn: Callable[[str], List[int]], 
    vocab_size: int, 
    device: torch.device, 
    max_len: int = 20
) -> torch.Tensor:
    """Convert text to one-hot logits tensor.
    
    Args:
        text: Input text string
        tokenize_fn: Function that converts text to list of token IDs
        vocab_size: Size of the vocabulary
        device: PyTorch device to create tensor on
        max_len: Maximum sequence length (will pad or truncate)
        
    Returns:
        Tensor of shape (1, max_len, vocab_size) with one-hot encoded logits
    """
    tokens = tokenize_fn(text)[:max_len]  # Truncate if too long

    # Pad to max_len
    while len(tokens) < max_len:
        tokens.append(0)  # PAD token

    # Create one-hot logits (very high logit for correct token, low for others)
    logits = torch.full((max_len, vocab_size), -10.0, device=device)
    for i, token in enumerate(tokens):
        logits[i, token] = 10.0  # High logit for correct token

    return logits.unsqueeze(0)  # Add batch dimension

"""
BLEU-Torch - PyTorch module for differentiable BLEU score computation.

This package provides PyTorch modules for computing BLEU scores that support
backpropagation, enabling end-to-end training of neural language models with
BLEU as a loss function.

Main components:
- DifferentiableBLEUModule: Core BLEU computation module
- DifferentiableBLEULoss: Loss function wrapper with proper bounds

Example:
    >>> import torch
    >>> from bleu_torch import DifferentiableBLEUModule, DifferentiableBLEULoss
    >>> 
    >>> # Create BLEU module
    >>> bleu_module = DifferentiableBLEUModule(vocab_size=1000)
    >>> loss_fn = DifferentiableBLEULoss(bleu_module, loss_type="complement")
    >>> 
    >>> # Use in training
    >>> logits = model(input_ids)  # (seq_len, vocab_size)
    >>> references = [ref1, ref2, ref3]  # List of reference token sequences
    >>> loss = loss_fn(logits, references)
    >>> loss.backward()
"""

from .bleu_torch import DifferentiableBLEUModule, DifferentiableBLEULoss

__version__ = "1.0.0"
__author__ = "bleu-torch contributors"
__email__ = "your-email@example.com"

__all__ = [
    "DifferentiableBLEUModule",
    "DifferentiableBLEULoss",
]

# Version info tuple for programmatic access
VERSION_INFO = tuple(int(x) for x in __version__.split("."))

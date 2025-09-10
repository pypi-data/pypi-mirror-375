# BLEU-Torch: Fast Differentiable BLEU Scores for PyTorch

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://pypi.org/project/bleu-torch/)
[![PyTorch](https://img.shields.io/badge/pytorch-1.9%2B-red)](https://pytorch.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-17%2F17%20passing-brightgreen)]()

A **fully differentiable PyTorch implementation** of BLEU scores optimized for training neural networks. Unlike traditional BLEU implementations that work with discrete tokens, `bleu-torch` operates directly on logits, making it perfect for use as a **differentiable loss function** in neural text generation models.

## 🚀 Key Features

- **⚡ Fully Vectorized**: Batch processing with no Python loops
- **🔥 GPU Accelerated**: Native PyTorch tensors with CUDA support  
- **📈 Differentiable**: Can be used as a loss function for training
- **🎯 Multiple Loss Types**: Complement (1-BLEU) and log (-log(BLEU)) loss functions
- **📊 Proper Loss Bounds**: Loss ∈ [0, 1] for complement loss, with 0 = perfect match
- **🧪 Thoroughly Tested**: 17 comprehensive tests including overfit validation
- **🚄 High Performance**: Efficient implementation for large-scale training
- **🌡️ Temperature Control**: Gumbel Softmax with configurable temperature  

## 📦 Installation

```bash
pip install bleu-torch
```

Or install from source:
```bash
git clone https://github.com/Ghost---Shadow/bleu-torch.git
cd bleu-torch
pip install -e .
```

## 💡 Quick Start

### Basic Usage

```python
import torch
from bleu_torch import DifferentiableBLEUModule, DifferentiableBLEULoss

# Initialize BLEU module
vocab_size = 1000
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
bleu_module = DifferentiableBLEUModule(vocab_size=vocab_size, temperature=0.1).to(device)
loss_fn = DifferentiableBLEULoss(bleu_module, loss_type="complement").to(device)

# Training scenario with logits
logits = torch.randn(8, vocab_size, requires_grad=True, device=device)  # (seq_len, vocab_size)
references = [
    torch.randint(0, vocab_size, (8,), device=device),   # Reference 1
    torch.randint(0, vocab_size, (10,), device=device),  # Reference 2  
    torch.randint(0, vocab_size, (6,), device=device),   # Reference 3
]

# Compute loss and backpropagate
loss = loss_fn(logits, references)
loss.backward()

print(f"BLEU Loss: {loss.item():.4f}")
print(f"Gradient norm: {logits.grad.norm().item():.6f}")
```

### Using as a Loss Function

```python
# Perfect for training neural networks!
for batch in dataloader:
    logits = model(batch['input_ids'])  # (seq_len, vocab_size)
    
    # BLEU loss is differentiable and ready for backprop
    loss = loss_fn(logits, batch['references'])
    loss.backward()
    optimizer.step()
```

### Working with Neural Models

```python
import torch.nn as nn
from bleu_torch import DifferentiableBLEUModule, DifferentiableBLEULoss

class MyLanguageModel(nn.Module):
    def __init__(self, vocab_size, hidden_dim=512):
        super().__init__()
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(d_model=hidden_dim, nhead=8),
            num_layers=6
        )
        self.output_proj = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, x):
        x = self.transformer(x)
        return self.output_proj(x)

# Training setup
model = MyLanguageModel(vocab_size=10000)
bleu_module = DifferentiableBLEUModule(vocab_size=10000, temperature=0.1)
bleu_loss = DifferentiableBLEULoss(bleu_module, loss_type="complement")

# Train with BLEU loss
for batch in dataloader:
    logits = model(batch['input_ids'])
    loss = bleu_loss(logits, batch['references'])
    loss.backward()
    optimizer.step()
```

## 📋 API Reference

### `DifferentiableBLEUModule`

Main class for computing differentiable BLEU scores.

```python
bleu_module = DifferentiableBLEUModule(vocab_size: int, max_n: int = 4, 
                                      temperature: float = 1.0, smoothing: float = 1e-10)
```

#### Parameters
- `vocab_size`: Size of the vocabulary
- `max_n`: Maximum n-gram order (default: 4 for BLEU-4)  
- `temperature`: Temperature for Gumbel Softmax during training (default: 1.0)
- `smoothing`: Small value for numerical stability (default: 1e-10)

#### Methods

**`forward(candidate_input, reference_ids_list)`**
- Computes BLEU score for a single candidate
- `candidate_input`: Either `(seq_len, vocab_size)` logits or `(seq_len,)` token IDs
- `reference_ids_list`: List of reference token ID tensors
- Returns: BLEU score tensor (scalar)

**`batch_forward(candidate_inputs, reference_ids_batch)`**
- Computes BLEU scores for a batch of candidates
- Returns: Tensor of BLEU scores with shape `(batch_size,)`

### `DifferentiableBLEULoss`

Loss function wrapper with proper bounds for training.

```python
loss_fn = DifferentiableBLEULoss(bleu_module: DifferentiableBLEUModule, 
                                loss_type: str = "complement")
```

#### Parameters
- `bleu_module`: DifferentiableBLEUModule instance
- `loss_type`: Loss type - `"complement"` (1-BLEU) or `"log"` (-log(BLEU))

#### Methods

**`forward(candidate_input, reference_ids_list)`**
- Computes BLEU-based loss with guaranteed minimum of 0
- Returns differentiable loss tensor

**`batch_forward(candidate_inputs, reference_ids_batch)`**
- Computes batch loss for multiple candidates
- Returns: Mean loss across the batch

## 🎯 Loss Function Details

The BLEU loss is designed for **training neural networks**:

```python
# Single loss computation: loss ∈ [0, 1] for complement loss
loss = loss_fn(logits, references)

# Different loss types
complement_loss = DifferentiableBLEULoss(bleu_module, "complement")  # loss = 1 - BLEU
log_loss = DifferentiableBLEULoss(bleu_module, "log")               # loss = -log(BLEU)
```

**Loss Properties:**
- ✅ **Differentiable**: Use with any PyTorch optimizer
- ✅ **Proper Bounds**: Always ≥ 0, with 0 = perfect match  
- ✅ **Intuitive**: Lower loss = better BLEU scores
- ✅ **Validated**: Tested with overfit experiments reaching ~0.0 loss

## Requirements

- Python >= 3.8
- PyTorch >= 1.9.0
- NumPy >= 1.19.0

## Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/ -v
# Or run directly:
python tests/test_bleu_torch.py
```

The test suite includes:
- 7 unit tests for basic functionality
- 5 comprehensive overfitting tests  
- 5 training scenario tests
- GPU/CPU compatibility tests

## License

MIT License - see LICENSE file for details.

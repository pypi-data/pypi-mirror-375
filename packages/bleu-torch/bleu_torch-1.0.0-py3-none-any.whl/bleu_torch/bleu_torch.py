import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Optional, Union


class DifferentiableBLEUModule(nn.Module):
    """
    PyTorch module for computing BLEU scores from LLM logits that supports end-to-end training.

    Works with both soft probability distributions and hard token IDs through unified processing.
    """

    def __init__(
        self,
        vocab_size: int,
        max_n: int = 4,
        temperature: float = 1.0,
        smoothing: float = 1e-10,
    ):
        """
        Initialize differentiable BLEU score module.

        Args:
            vocab_size: Size of the vocabulary
            max_n: Maximum n-gram order (default: 4)
            temperature: Temperature for Gumbel softmax (default: 1.0)
            smoothing: Small value for numerical stability (default: 1e-10)
        """
        super(DifferentiableBLEUModule, self).__init__()
        self.vocab_size = vocab_size
        self.max_n = max_n
        self.temperature = temperature
        self.smoothing = smoothing

        # Pre-compute and register the vocabulary mask matrix as a buffer
        mask_matrix = self._create_vocab_mask_matrix(max_n, vocab_size)
        self.register_buffer("vocab_mask_matrix", mask_matrix)

        # N-gram weights (can be made learnable)
        self.register_parameter(
            "ngram_weights",
            nn.Parameter(torch.ones(max_n) / max_n, requires_grad=False),
        )

    def _create_vocab_mask_matrix(self, max_n: int, vocab_size: int) -> torch.Tensor:
        """Create vocabulary mask matrix for efficient n-gram total computation."""
        n_orders = torch.arange(1, max_n + 1, dtype=torch.float32).unsqueeze(1)
        vocab_indices = torch.arange(max_n * vocab_size, dtype=torch.float32).unsqueeze(
            0
        )
        threshold = n_orders * vocab_size
        mask_matrix = (vocab_indices < threshold).float()
        return mask_matrix

    def _to_token_distributions(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """
        Convert input to token distributions. Handles both logits and token IDs.

        Args:
            input_tensor: Either (seq_len, vocab_size) logits or (seq_len,) token IDs

        Returns:
            Token distributions (seq_len, vocab_size)
        """
        if input_tensor.dim() == 1:
            # Hard token IDs - convert to one-hot
            return F.one_hot(input_tensor.long(), self.vocab_size).float()
        elif input_tensor.dim() == 2:
            # Logits - apply softmax or Gumbel softmax
            if self.training and self.temperature != 1.0:
                return F.gumbel_softmax(
                    input_tensor, tau=self.temperature, hard=False, dim=-1
                )
            else:
                return F.softmax(input_tensor, dim=-1)
        else:
            raise ValueError(
                f"Input tensor must be 1D (token IDs) or 2D (logits), got {input_tensor.dim()}D"
            )

    def _create_ngrams_from_distributions(
        self, token_dists: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Create n-gram representations from token distributions.

        Args:
            token_dists: (seq_len, vocab_size) token probability distributions

        Returns:
            ngrams_3d: (max_n, max_ngrams, max_n * vocab_size) tensor
            valid_mask: (max_n, max_ngrams) mask for valid n-grams
        """
        seq_len, vocab_size = token_dists.shape
        max_ngrams = max(1, seq_len)

        ngrams_3d = torch.zeros(
            self.max_n,
            max_ngrams,
            self.max_n * vocab_size,
            dtype=torch.float32,
            device=token_dists.device,
        )
        valid_mask = torch.zeros(
            self.max_n, max_ngrams, dtype=torch.float32, device=token_dists.device
        )

        for n in range(1, self.max_n + 1):
            if seq_len >= n:
                num_ngrams = seq_len - n + 1

                # Create n-gram representations by concatenating token distributions
                for i in range(num_ngrams):
                    # Get n consecutive token distributions and flatten
                    ngram_tokens = token_dists[i : i + n]  # (n, vocab_size)
                    ngrams_3d[n - 1, i, : n * vocab_size] = ngram_tokens.flatten()

                valid_mask[n - 1, :num_ngrams] = 1.0

        return ngrams_3d, valid_mask

    def _create_reference_ngrams_batch(
        self, reference_ids_list: List[torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Create n-gram representations for all references efficiently."""
        if not reference_ids_list:
            return torch.empty(0, self.max_n, 0), torch.empty(0, self.max_n, 0)

        # Pad references
        num_refs = len(reference_ids_list)
        ref_lengths = torch.tensor(
            [ref.size(0) for ref in reference_ids_list],
            dtype=torch.float32,
            device=reference_ids_list[0].device,
        )
        max_ref_len = int(ref_lengths.max().item())
        max_ngrams = max(1, max_ref_len)

        padded_refs = torch.full(
            (num_refs, max_ref_len),
            0,
            dtype=torch.long,
            device=reference_ids_list[0].device,
        )

        for i, ref_ids in enumerate(reference_ids_list):
            seq_len = ref_ids.size(0)
            padded_refs[i, :seq_len] = ref_ids.long()

        # Create n-grams for all references
        ref_ngrams_4d = torch.zeros(
            num_refs,
            self.max_n,
            max_ngrams,
            self.max_n * self.vocab_size,
            dtype=torch.float32,
            device=padded_refs.device,
        )
        ref_valid_mask = torch.zeros(
            num_refs,
            self.max_n,
            max_ngrams,
            dtype=torch.float32,
            device=padded_refs.device,
        )

        for ref_idx in range(num_refs):
            ref_len = int(ref_lengths[ref_idx].item())

            for n in range(1, self.max_n + 1):
                if ref_len >= n:
                    ref_ids = padded_refs[ref_idx, :ref_len]
                    num_ngrams = ref_len - n + 1

                    for i in range(num_ngrams):
                        # Create one-hot n-gram
                        ngram_ids = ref_ids[i : i + n]  # (n,)
                        ngram_onehot = torch.zeros(
                            n * self.vocab_size, device=padded_refs.device
                        )

                        for j, token_id in enumerate(ngram_ids):
                            start_idx = j * self.vocab_size
                            ngram_onehot[start_idx + token_id] = 1.0

                        ref_ngrams_4d[
                            ref_idx, n - 1, i, : n * self.vocab_size
                        ] = ngram_onehot

                    ref_valid_mask[ref_idx, n - 1, :num_ngrams] = 1.0

        return ref_ngrams_4d, ref_valid_mask

    def _count_ngrams(
        self, ngrams: torch.Tensor, valid_mask: torch.Tensor
    ) -> torch.Tensor:
        """Count n-grams using valid mask to handle padding."""
        if ngrams.dim() == 3:  # 3D case (candidate)
            masked_ngrams = ngrams * valid_mask.unsqueeze(2)
            return masked_ngrams.sum(dim=1)
        else:  # 4D case (references)
            masked_ngrams = ngrams * valid_mask.unsqueeze(3)
            return masked_ngrams.sum(dim=2)

    def _compute_ngram_totals(
        self, clipped_counts: torch.Tensor, cand_counts: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute n-gram totals using mask matrix multiplication."""
        masked_clipped = clipped_counts * self.vocab_mask_matrix
        masked_candidate = cand_counts * self.vocab_mask_matrix

        total_clipped = masked_clipped.sum(dim=1)
        total_candidate = masked_candidate.sum(dim=1)

        return total_clipped, total_candidate

    def forward(
        self, candidate_input: torch.Tensor, reference_ids_list: List[torch.Tensor]
    ) -> torch.Tensor:
        """
        Compute BLEU score for candidate against references.

        Args:
            candidate_input: Either (seq_len, vocab_size) logits or (seq_len,) token IDs
            reference_ids_list: List of (seq_len_i,) tensors of reference token IDs

        Returns:
            BLEU score tensor (scalar)
        """
        # Convert input to token distributions (handles both logits and token IDs)
        candidate_dists = self._to_token_distributions(candidate_input)
        seq_len = candidate_dists.size(0)

        # Brevity penalty calculation
        candidate_len = torch.tensor(
            seq_len, dtype=torch.float32, device=candidate_input.device
        )
        ref_lens = torch.stack(
            [
                torch.tensor(
                    ref.size(0), dtype=torch.float32, device=candidate_input.device
                )
                for ref in reference_ids_list
            ]
        )

        # Find closest reference length
        len_diffs = torch.abs(ref_lens - candidate_len)
        closest_idx = torch.argmin(len_diffs)
        closest_ref_len = ref_lens[closest_idx]

        # Brevity penalty
        bp = torch.where(
            candidate_len > closest_ref_len,
            torch.tensor(1.0, device=candidate_input.device),
            torch.exp(
                1.0 - closest_ref_len / torch.clamp(candidate_len, min=self.smoothing)
            ),
        )

        # Create candidate n-grams
        cand_ngrams_3d, cand_valid_mask = self._create_ngrams_from_distributions(
            candidate_dists
        )
        cand_counts_3d = self._count_ngrams(cand_ngrams_3d, cand_valid_mask)

        # Create reference n-grams
        ref_ngrams_4d, ref_valid_mask = self._create_reference_ngrams_batch(
            reference_ids_list
        )
        ref_counts_4d = self._count_ngrams(ref_ngrams_4d, ref_valid_mask)

        # Take element-wise maximum across references
        max_ref_counts_3d = ref_counts_4d.max(dim=0)[0]

        # Compute clipped counts
        clipped_counts_3d = torch.min(cand_counts_3d, max_ref_counts_3d)

        # Compute precision totals
        total_clipped, total_candidate = self._compute_ngram_totals(
            clipped_counts_3d, cand_counts_3d
        )

        # Compute precisions with smoothing
        precisions = total_clipped / torch.clamp(total_candidate, min=self.smoothing)
        precisions = torch.clamp(precisions, min=self.smoothing)

        # Weighted geometric mean
        log_precisions = torch.log(precisions)
        weighted_log_mean = (self.ngram_weights * log_precisions).sum()
        geometric_mean = torch.exp(weighted_log_mean)

        return bp * geometric_mean

    def batch_forward(
        self,
        candidate_inputs: List[torch.Tensor],
        reference_ids_batch: List[List[torch.Tensor]],
    ) -> torch.Tensor:
        """
        Compute BLEU scores for a batch of candidates.

        Args:
            candidate_inputs: List of candidate tensors (logits or token IDs)
            reference_ids_batch: List of lists of reference tensors

        Returns:
            Tensor of BLEU scores with shape (batch_size,)
        """
        batch_size = len(candidate_inputs)
        scores = torch.zeros(
            batch_size, dtype=torch.float32, device=candidate_inputs[0].device
        )

        for i, (cand_input, ref_ids_list) in enumerate(
            zip(candidate_inputs, reference_ids_batch)
        ):
            scores[i] = self.forward(cand_input, ref_ids_list)

        return scores


class DifferentiableBLEULoss(nn.Module):
    """
    BLEU-based loss function for training with proper bounds ensuring minimum loss of 0.

    Theoretical bounds:
    - BLEU score range: [0, 1]
    - Loss ranges:
        - 'complement': [0, 1] (1 - BLEU, min=0 when BLEU=1, max=1 when BLEU=0)
        - 'negative_shifted': [0, 1] (-BLEU + 1, min=0 when BLEU=1, max=1 when BLEU=0)
        - 'log': [0, ∞) (-log(BLEU), min=0 when BLEU=1, max=∞ when BLEU→0)
    """

    def __init__(
        self, bleu_module: DifferentiableBLEUModule, loss_type: str = "complement"
    ):
        """
        Initialize differentiable BLEU loss with proper bounds.

        Args:
            bleu_module: DifferentiableBLEUModule instance
            loss_type: 'complement' for 1-BLEU, 'negative_shifted' for 1-BLEU, 'log' for -log(BLEU)
        """
        super(DifferentiableBLEULoss, self).__init__()
        self.bleu_module = bleu_module
        self.loss_type = loss_type

        # Calculate theoretical bounds
        self.min_bleu = 0.0
        self.max_bleu = 1.0

        if loss_type in ["complement", "negative_shifted"]:
            self.min_loss = 0.0  # When BLEU = 1
            self.max_loss = 1.0  # When BLEU = 0
        elif loss_type == "log":
            self.min_loss = 0.0  # When BLEU = 1
            self.max_loss = float("inf")  # When BLEU → 0
        else:
            raise ValueError(
                f"Unknown loss_type: {loss_type}. Use 'complement', 'negative_shifted', or 'log'"
            )

    def get_theoretical_bounds(self) -> Tuple[float, float]:
        """Return theoretical (min_loss, max_loss) bounds."""
        return self.min_loss, self.max_loss

    def forward(
        self, candidate_input: torch.Tensor, reference_ids_list: List[torch.Tensor]
    ) -> torch.Tensor:
        """Compute BLEU-based loss with guaranteed minimum of 0."""
        bleu_score = self.bleu_module(candidate_input, reference_ids_list)

        # Ensure BLEU is in valid range [0, 1]
        bleu_score = torch.clamp(bleu_score, min=self.min_bleu, max=self.max_bleu)

        if self.loss_type in ["complement", "negative_shifted"]:
            # 1 - BLEU: ranges from 0 (perfect) to 1 (worst)
            loss = 1.0 - bleu_score
        elif self.loss_type == "log":
            # -log(BLEU): ranges from 0 (perfect) to ∞ (worst)
            # Use smoothing to prevent log(0)
            loss = -torch.log(torch.clamp(bleu_score, min=self.bleu_module.smoothing))

        # Ensure loss is non-negative (though it should be by construction)
        loss = torch.clamp(loss, min=0.0)
        return loss

    def batch_forward(
        self,
        candidate_inputs: List[torch.Tensor],
        reference_ids_batch: List[List[torch.Tensor]],
    ) -> torch.Tensor:
        """Compute BLEU-based loss for a batch with guaranteed minimum of 0."""
        bleu_scores = self.bleu_module.batch_forward(
            candidate_inputs, reference_ids_batch
        )

        # Ensure all BLEU scores are in valid range
        bleu_scores = torch.clamp(bleu_scores, min=self.min_bleu, max=self.max_bleu)

        if self.loss_type in ["complement", "negative_shifted"]:
            batch_loss = (1.0 - bleu_scores).mean()
        elif self.loss_type == "log":
            batch_loss = -torch.log(
                torch.clamp(bleu_scores, min=self.bleu_module.smoothing)
            ).mean()

        # Ensure batch loss is non-negative
        batch_loss = torch.clamp(batch_loss, min=0.0)
        return batch_loss


# Example usage and testing
if __name__ == "__main__":
    print("=== Unified Differentiable BLEU Module Demo ===")

    # Initialize module
    vocab_size = 100
    bleu_module = DifferentiableBLEUModule(
        vocab_size=vocab_size, max_n=4, temperature=0.5
    )

    # Test with logits (training scenario)
    print("\n--- Testing with Logits ---")
    seq_len = 8
    candidate_logits = torch.randn(seq_len, vocab_size, requires_grad=True)
    reference_ids_list = [
        torch.randint(0, vocab_size, (8,)),
        torch.randint(0, vocab_size, (10,)),
        torch.randint(0, vocab_size, (6,)),
    ]

    print(f"Candidate logits shape: {candidate_logits.shape}")
    print(f"Reference lengths: {[ref.size(0) for ref in reference_ids_list]}")

    bleu_module.train()
    score_from_logits = bleu_module(candidate_logits, reference_ids_list)
    print(f"BLEU from logits: {score_from_logits:.4f}")

    # Test gradient flow
    score_from_logits.backward()
    print(f"Gradient norm: {candidate_logits.grad.norm().item():.6f}")

    # Test with token IDs (evaluation scenario)
    print("\n--- Testing with Token IDs ---")
    candidate_tokens = torch.argmax(
        candidate_logits, dim=-1
    )  # Convert logits to tokens
    print(f"Candidate tokens shape: {candidate_tokens.shape}")

    with torch.no_grad():
        score_from_tokens = bleu_module(candidate_tokens, reference_ids_list)
        print(f"BLEU from tokens: {score_from_tokens:.4f}")

    # Test loss function with bounds
    print("\n--- Testing Loss Function with Bounds ---")
    bleu_loss = DifferentiableBLEULoss(bleu_module, loss_type="complement")

    # Print theoretical bounds
    min_loss, max_loss = bleu_loss.get_theoretical_bounds()
    print(f"Theoretical loss bounds: [{min_loss:.1f}, {max_loss:.1f}]")

    candidate_logits.grad = None  # Reset gradients
    loss = bleu_loss(candidate_logits, reference_ids_list)
    print(f"BLEU loss: {loss:.4f} (should be in bounds)")
    print(f"Loss >= 0: {loss.item() >= 0}")

    loss.backward()
    print(f"Loss gradient norm: {candidate_logits.grad.norm().item():.6f}")

    # Test extreme cases
    print("\n--- Testing Extreme Cases ---")

    # Perfect match case (should give loss ≈ 0)
    perfect_tokens = reference_ids_list[0][:seq_len]  # Use reference as candidate
    with torch.no_grad():
        perfect_score = bleu_module(perfect_tokens, [perfect_tokens])  # Self-reference
        perfect_loss = bleu_loss(perfect_tokens, [perfect_tokens])
        print(f"Perfect match - BLEU: {perfect_score:.4f}, Loss: {perfect_loss:.4f}")

    # Random case (should give higher loss)
    random_tokens = torch.randint(0, vocab_size, (seq_len,))
    with torch.no_grad():
        random_score = bleu_module(random_tokens, reference_ids_list)
        random_loss = bleu_loss(random_tokens, reference_ids_list)
        print(f"Random tokens - BLEU: {random_score:.4f}, Loss: {random_loss:.4f}")

    # Test different loss types
    print("\n--- Testing Different Loss Types ---")
    for loss_type in ["complement", "log"]:
        test_loss_fn = DifferentiableBLEULoss(bleu_module, loss_type=loss_type)
        min_l, max_l = test_loss_fn.get_theoretical_bounds()

        with torch.no_grad():
            test_loss = test_loss_fn(candidate_tokens, reference_ids_list)
            print(
                f"{loss_type:10} - bounds: [{min_l:.1f}, {max_l:>4}], loss: {test_loss:.4f}"
            )

    # Test batch processing
    print("\n--- Testing Batch Processing ---")
    candidate_batch = [candidate_logits.detach(), torch.randn(5, vocab_size)]
    reference_batch = [reference_ids_list, [torch.randint(0, vocab_size, (7,))]]

    with torch.no_grad():
        batch_scores = bleu_module.batch_forward(candidate_batch, reference_batch)
        batch_loss = bleu_loss.batch_forward(candidate_batch, reference_batch)
        print(f"Batch BLEU scores: {batch_scores}")
        print(f"Batch loss: {batch_loss:.4f} (>= 0: {batch_loss.item() >= 0})")

    print("\n=== Theoretical Analysis ===")
    print("BLEU Score Range: [0, 1]")
    print("Loss Function Mappings:")
    print("  complement: loss = 1 - BLEU")
    print("    - Perfect match (BLEU=1) → loss=0")
    print("    - Worst case (BLEU=0) → loss=1")
    print("    - Range: [0, 1]")
    print("  log: loss = -log(BLEU)")
    print("    - Perfect match (BLEU=1) → loss=0")
    print("    - Worst case (BLEU→0) → loss→∞")
    print("    - Range: [0, ∞)")

    print("\n=== Usage Examples ===")
    print("# Training with proper loss bounds:")
    print("bleu_loss = DifferentiableBLEULoss(bleu_module, 'complement')")
    print("logits = model(input_ids)")
    print("loss = bleu_loss(logits, references)  # Always >= 0")
    print("loss.backward()")
    print()
    print("# Check theoretical bounds:")
    print("min_loss, max_loss = bleu_loss.get_theoretical_bounds()")
    print("print(f'Loss will be in range [{min_loss}, {max_loss}]')")
    print()
    print("Module guarantees proper loss bounds!")

import unittest
import torch
from rouge_torch import ROUGEScoreTorch, create_vocab_and_tokenizer, text_to_logits


class TestROUGEScoreTorch(unittest.TestCase):
    """Unit tests for ROUGEScoreTorch class."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class."""
        cls.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        (
            cls.word_to_id,
            cls.id_to_word,
            cls.tokenize_fn,
            cls.detokenize_fn,
        ) = create_vocab_and_tokenizer()
        cls.vocab_size = len(cls.word_to_id)
        cls.rouge = ROUGEScoreTorch(cls.vocab_size, cls.device)

    def _text_to_logits(self, text, max_len=20):
        """Helper method to convert text to logits using the stored tokenizer."""
        # Access the function from the class to avoid bound method issue
        tokenize_func = type(self).tokenize_fn
        return text_to_logits(
            text, tokenize_func, self.vocab_size, self.device, max_len
        )

    def test_identical_strings(self):
        """Test Case 1: Identical strings should get perfect scores."""
        candidate = "the cat sat on the mat"
        reference = "the cat sat on the mat"

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        rouge_1 = self.rouge.rouge_n_batch(cand_logits, ref_logits, n=1)
        rouge_2 = self.rouge.rouge_n_batch(cand_logits, ref_logits, n=2)
        rouge_l = self.rouge.rouge_l_batch(cand_logits, ref_logits)

        # Identical strings should have perfect scores
        self.assertAlmostEqual(rouge_1["precision"][0].item(), 1.0, places=3)
        self.assertAlmostEqual(rouge_1["recall"][0].item(), 1.0, places=3)
        self.assertAlmostEqual(rouge_1["f1"][0].item(), 1.0, places=3)

        self.assertAlmostEqual(rouge_2["precision"][0].item(), 1.0, places=3)
        self.assertAlmostEqual(rouge_2["recall"][0].item(), 1.0, places=3)
        self.assertAlmostEqual(rouge_2["f1"][0].item(), 1.0, places=3)

        self.assertAlmostEqual(rouge_l["precision"][0].item(), 1.0, places=3)
        self.assertAlmostEqual(rouge_l["recall"][0].item(), 1.0, places=3)
        self.assertAlmostEqual(rouge_l["f1"][0].item(), 1.0, places=3)

    def test_completely_different_strings(self):
        """Test Case 2: Completely different strings should get zero scores."""
        candidate = "the quick brown fox"
        reference = "a big red car"

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        rouge_1 = self.rouge.rouge_n_batch(cand_logits, ref_logits, n=1)
        rouge_2 = self.rouge.rouge_n_batch(cand_logits, ref_logits, n=2)
        rouge_l = self.rouge.rouge_l_batch(cand_logits, ref_logits)

        # Different strings should have zero or very low scores
        self.assertAlmostEqual(rouge_1["precision"][0].item(), 0.0, places=3)
        self.assertAlmostEqual(rouge_1["recall"][0].item(), 0.0, places=3)
        self.assertAlmostEqual(rouge_1["f1"][0].item(), 0.0, places=3)

        self.assertAlmostEqual(rouge_2["precision"][0].item(), 0.0, places=3)
        self.assertAlmostEqual(rouge_2["recall"][0].item(), 0.0, places=3)
        self.assertAlmostEqual(rouge_2["f1"][0].item(), 0.0, places=3)

        self.assertAlmostEqual(rouge_l["precision"][0].item(), 0.0, places=3)
        self.assertAlmostEqual(rouge_l["recall"][0].item(), 0.0, places=3)
        self.assertAlmostEqual(rouge_l["f1"][0].item(), 0.0, places=3)

    def test_partial_overlap(self):
        """Test Case 3: Partial overlap - 3/5 words overlap (the, is, very)."""
        candidate = "the cat is very good"
        reference = "the dog is very bad"

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        rouge_1 = self.rouge.rouge_n_batch(cand_logits, ref_logits, n=1)
        rouge_2 = self.rouge.rouge_n_batch(cand_logits, ref_logits, n=2)
        rouge_l = self.rouge.rouge_l_batch(cand_logits, ref_logits)

        # Expected precision: 3/5 = 0.6, recall: 3/5 = 0.6
        self.assertAlmostEqual(rouge_1["precision"][0].item(), 0.6, places=1)
        self.assertAlmostEqual(rouge_1["recall"][0].item(), 0.6, places=1)
        self.assertAlmostEqual(rouge_1["f1"][0].item(), 0.6, places=1)

        # ROUGE-2 should have lower scores due to fewer bigram matches
        self.assertLess(rouge_2["f1"][0].item(), rouge_1["f1"][0].item())

    def test_word_reordering(self):
        """Test Case 4: Word reordering - ROUGE-L should be lower than ROUGE-1."""
        candidate = "the cat sat on the mat"
        reference = "mat the on sat cat the"  # Same words, different order

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        rouge_1 = self.rouge.rouge_n_batch(cand_logits, ref_logits, n=1)
        rouge_l = self.rouge.rouge_l_batch(cand_logits, ref_logits)

        # ROUGE-1 should be 1.0 (same words)
        self.assertAlmostEqual(rouge_1["precision"][0].item(), 1.0, places=3)
        self.assertAlmostEqual(rouge_1["recall"][0].item(), 1.0, places=3)
        self.assertAlmostEqual(rouge_1["f1"][0].item(), 1.0, places=3)

        # ROUGE-L should be lower due to different word order
        self.assertLess(rouge_l["f1"][0].item(), rouge_1["f1"][0].item())

    def test_multiple_references(self):
        """Test Case 5: Multiple references - should take best match across references."""
        candidate = "the cat is good"
        ref1 = "the cat is very good"
        ref2 = "a cat is good"

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [
            self._text_to_logits(ref1),
            self._text_to_logits(ref2),
        ]

        rouge_1 = self.rouge.rouge_n_batch(cand_logits, ref_logits, n=1)
        rouge_l = self.rouge.rouge_l_batch(cand_logits, ref_logits)

        # Should get reasonable scores by taking the best match
        self.assertGreater(rouge_1["f1"][0].item(), 0.6)
        self.assertGreater(rouge_l["f1"][0].item(), 0.6)

    def test_batch_processing(self):
        """Test Case 6: Batch processing of multiple examples."""
        candidates = ["the cat sat", "a dog ran", "the quick fox"]
        references = ["the cat sat on mat", "the dog ran fast", "quick brown fox jumps"]

        # Create batch tensors
        max_len = 10
        batch_cand_logits = []
        batch_ref_logits = []

        for cand, ref in zip(candidates, references):
            cand_logits = self._text_to_logits(cand, max_len)
            ref_logits = self._text_to_logits(ref, max_len)
            batch_cand_logits.append(cand_logits)
            batch_ref_logits.append(ref_logits)

        batch_cand_logits = torch.cat(batch_cand_logits, dim=0)
        batch_ref_logits = [torch.cat(batch_ref_logits, dim=0)]

        rouge_1 = self.rouge.rouge_n_batch(batch_cand_logits, batch_ref_logits, n=1)
        rouge_l = self.rouge.rouge_l_batch(batch_cand_logits, batch_ref_logits)

        # Check that all examples have reasonable scores
        self.assertEqual(len(rouge_1["f1"]), len(candidates))
        self.assertEqual(len(rouge_l["f1"]), len(candidates))

        for i in range(len(candidates)):
            self.assertGreaterEqual(rouge_1["f1"][i].item(), 0.0)
            self.assertLessEqual(rouge_1["f1"][i].item(), 1.0)
            self.assertGreaterEqual(rouge_l["f1"][i].item(), 0.0)
            self.assertLessEqual(rouge_l["f1"][i].item(), 1.0)

    def test_loss_bounds(self):
        """Test that loss function has proper bounds."""
        # Test case 1: Perfect match (should give loss = 0)
        candidate = "the cat sat on the mat"
        reference = "the cat sat on the mat"

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        loss = self.rouge.compute_rouge_loss(cand_logits, ref_logits, reduction="mean")
        self.assertAlmostEqual(
            loss.item(), 0.0, places=5, msg="Perfect match should give loss = 0"
        )

        # Test case 2: No match (should give loss = 1)
        candidate = "the quick brown fox"
        reference = "a big red car"

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        loss = self.rouge.compute_rouge_loss(cand_logits, ref_logits, reduction="mean")
        self.assertAlmostEqual(
            loss.item(),
            2.0,
            places=5,
            msg="No match should give loss = 2 (ROUGE-1 + ROUGE-L)",
        )

        # Test case 3: Partial match (should give loss between 0 and 1)
        candidate = "the cat is very good"
        reference = "the dog is very bad"  # 3/5 overlap

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        loss = self.rouge.compute_rouge_loss(cand_logits, ref_logits, reduction="mean")
        self.assertGreater(loss.item(), 0.0)
        self.assertLess(loss.item(), 2.0)
        # With partial overlap, loss should be between 0 and 2
        self.assertGreater(loss.item(), 0.5)  # Should be greater than some threshold
        self.assertLess(loss.item(), 1.5)  # Should be less than max for partial match

    def test_loss_reduction_modes(self):
        """Test different loss reduction modes."""
        candidates = ["the cat sat", "a dog ran"]
        references = ["the cat sat on mat", "the dog ran fast"]

        # Create batch tensors
        max_len = 10
        batch_cand_logits = []
        batch_ref_logits = []

        for cand, ref in zip(candidates, references):
            cand_logits = self._text_to_logits(cand, max_len)
            ref_logits = self._text_to_logits(ref, max_len)
            batch_cand_logits.append(cand_logits)
            batch_ref_logits.append(ref_logits)

        batch_cand_logits = torch.cat(batch_cand_logits, dim=0)
        batch_ref_logits = [torch.cat(batch_ref_logits, dim=0)]

        # Test different reduction modes
        loss_mean = self.rouge.compute_rouge_loss(
            batch_cand_logits, batch_ref_logits, reduction="mean"
        )
        loss_sum = self.rouge.compute_rouge_loss(
            batch_cand_logits, batch_ref_logits, reduction="sum"
        )
        loss_none = self.rouge.compute_rouge_loss(
            batch_cand_logits, batch_ref_logits, reduction="none"
        )

        # Check shapes and relationships
        self.assertEqual(loss_mean.shape, ())  # scalar
        self.assertEqual(loss_sum.shape, ())  # scalar
        self.assertEqual(loss_none.shape, (2,))  # batch_size

        # Check mathematical relationships
        self.assertAlmostEqual(loss_mean.item(), loss_none.mean().item(), places=5)
        self.assertAlmostEqual(loss_sum.item(), loss_none.sum().item(), places=5)

        # All losses should be in [0, 2] (with default ROUGE-1 + ROUGE-L)
        self.assertGreaterEqual(loss_mean.item(), 0.0)
        self.assertLessEqual(loss_mean.item(), 2.0)
        self.assertGreaterEqual(loss_sum.item(), 0.0)
        self.assertLessEqual(
            loss_sum.item(), len(candidates) * 2.0
        )  # sum can be up to batch_size * 2

        for i in range(len(candidates)):
            self.assertGreaterEqual(loss_none[i].item(), 0.0)
            self.assertLessEqual(loss_none[i].item(), 2.0)

    def test_single_rouge_type_loss_bounds(self):
        """Test that single ROUGE type loss has bounds [0, 1]."""
        # Perfect match with single ROUGE type
        candidate = "the cat sat on the mat"
        reference = "the cat sat on the mat"

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        loss_r1 = self.rouge.compute_rouge_loss(
            cand_logits, ref_logits, rouge_types=["rouge_1"], reduction="mean"
        )
        loss_rl = self.rouge.compute_rouge_loss(
            cand_logits, ref_logits, rouge_types=["rouge_l"], reduction="mean"
        )

        self.assertAlmostEqual(loss_r1.item(), 0.0, places=5)
        self.assertAlmostEqual(loss_rl.item(), 0.0, places=5)

        # No match with single ROUGE type
        candidate = "the quick brown fox"
        reference = "a big red car"

        cand_logits = self._text_to_logits(candidate)
        ref_logits = [self._text_to_logits(reference)]

        loss_r1 = self.rouge.compute_rouge_loss(
            cand_logits, ref_logits, rouge_types=["rouge_1"], reduction="mean"
        )
        loss_rl = self.rouge.compute_rouge_loss(
            cand_logits, ref_logits, rouge_types=["rouge_l"], reduction="mean"
        )

        self.assertAlmostEqual(loss_r1.item(), 1.0, places=5)
        self.assertAlmostEqual(loss_rl.item(), 1.0, places=5)

    def test_overfit_convergence(self):
        """Test that a small model can overfit to near-zero ROUGE loss on a single batch.

        This test validates that our ROUGE loss function implementation is correct
        by training a simple model to convergence on one batch and verifying it
        reaches near-zero loss.
        """

        # Simple model for text generation
        class SimpleTextModel(torch.nn.Module):
            def __init__(self, vocab_size, seq_len, hidden_size=64):
                super().__init__()
                self.vocab_size = vocab_size
                self.seq_len = seq_len
                self.hidden_size = hidden_size

                # Simple architecture: embedding -> LSTM -> linear
                self.embedding = torch.nn.Embedding(vocab_size, hidden_size)
                self.lstm = torch.nn.LSTM(hidden_size, hidden_size, batch_first=True)
                self.output_proj = torch.nn.Linear(hidden_size, vocab_size)

            def forward(self, input_ids):
                # input_ids: (batch_size, seq_len)
                batch_size = input_ids.size(0)

                # Create embeddings
                embeds = self.embedding(input_ids)  # (batch_size, seq_len, hidden_size)

                # LSTM
                lstm_out, _ = self.lstm(embeds)  # (batch_size, seq_len, hidden_size)

                # Project to vocab
                logits = self.output_proj(lstm_out)  # (batch_size, seq_len, vocab_size)

                return logits

        # Set up training data - one batch with simple target
        batch_size = 2
        seq_len = 8
        vocab_size = self.vocab_size
        device = self.device

        # Create simple input-target pairs that should be easy to memorize
        # Input: "the cat sat"  -> Target: "the cat sat on mat"
        # Input: "a dog ran"   -> Target: "a dog ran in park"

        input_texts = ["the cat sat", "a dog ran"]
        target_texts = ["the cat sat on mat", "a dog ran in park"]

        # Convert to tensors
        input_ids = []
        target_logits = []

        for inp_text, tgt_text in zip(input_texts, target_texts):
            # Tokenize input (first 3 tokens)
            tokenize_func = type(self).tokenize_fn
            inp_tokens = tokenize_func(inp_text)[:3]
            while len(inp_tokens) < seq_len:
                inp_tokens.append(0)  # PAD
            input_ids.append(inp_tokens)

            # Create target logits
            tgt_logits = self._text_to_logits(tgt_text, seq_len)
            target_logits.append(tgt_logits)

        input_ids = torch.tensor(input_ids, device=device)  # (batch_size, seq_len)
        target_logits = [
            torch.cat(target_logits, dim=0)
        ]  # List of (batch_size, seq_len, vocab_size)

        # Create model and optimizer
        model = SimpleTextModel(vocab_size, seq_len).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        rouge_scorer = self.rouge

        # Training loop - should converge to near zero loss
        initial_loss = None
        final_loss = None
        losses = []

        for epoch in range(200):  # Should be enough for overfitting
            optimizer.zero_grad()

            # Forward pass
            logits = model(input_ids)  # (batch_size, seq_len, vocab_size)

            # For differentiable training, we need a proxy loss
            # We'll use cross-entropy between the predicted logits and target logits
            # This is a differentiable approximation that should drive the model
            # to produce logits that match the targets

            # Convert target logits to soft targets (probabilities)
            target_probs = torch.softmax(
                target_logits[0], dim=-1
            )  # (batch_size, seq_len, vocab_size)

            # Use KL divergence loss as a differentiable proxy
            log_pred_probs = torch.log_softmax(logits, dim=-1)
            kl_loss = torch.nn.functional.kl_div(
                log_pred_probs, target_probs, reduction="batchmean"
            )

            # Also compute the actual ROUGE loss for monitoring (non-differentiable)
            with torch.no_grad():
                rouge_loss = rouge_scorer.compute_rouge_loss(
                    logits, target_logits, rouge_types=["rouge_1"], reduction="mean"
                )

            # Use KL loss for training, but monitor ROUGE loss
            loss = kl_loss
            losses.append(rouge_loss.item())  # Track ROUGE loss for validation

            if epoch == 0:
                initial_loss = rouge_loss.item()

            # Backward pass
            loss.backward()
            optimizer.step()

            # Check for convergence using ROUGE loss
            current_rouge_loss = rouge_loss.item()
            if current_rouge_loss < 0.01:  # Very low ROUGE loss threshold
                final_loss = current_rouge_loss
                break

            # Print progress occasionally
            if epoch % 50 == 0:
                print(
                    f"Epoch {epoch}: KL Loss = {kl_loss.item():.6f}, ROUGE Loss = {current_rouge_loss:.6f}"
                )

        final_loss = losses[-1] if final_loss is None else losses[-1]

        # Assertions to validate overfitting behavior
        self.assertIsNotNone(initial_loss, "Should have recorded initial loss")
        self.assertGreater(initial_loss, 0.5, "Initial loss should be high")
        self.assertLess(
            final_loss, 0.1, "Final loss should be very low after overfitting"
        )
        self.assertLess(
            final_loss, initial_loss * 0.1, "Loss should decrease by at least 90%"
        )

        # Additional validation: check that the model actually learned something
        with torch.no_grad():
            final_logits = model(input_ids)
            final_rouge_scores = rouge_scorer.rouge_n_batch(
                final_logits, target_logits, n=1
            )

            # F1 scores should be high (close to 1) after overfitting
            mean_f1 = final_rouge_scores["f1"].mean().item()
            self.assertGreater(
                mean_f1, 0.8, "Model should achieve high F1 scores after overfitting"
            )

        print(f"Overfit test completed:")
        print(f"  Initial ROUGE loss: {initial_loss:.6f}")
        print(f"  Final ROUGE loss: {final_loss:.6f}")
        print(f"  ROUGE loss reduction: {(1 - final_loss/initial_loss)*100:.1f}%")
        print(f"  Final F1 score: {mean_f1:.3f}")
        print(f"  Converged in {len(losses)} epochs")

        # Test passes if we successfully overfit to low loss


class TestROUGEPerformance(unittest.TestCase):
    """Performance tests for ROUGEScoreTorch class."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for performance tests."""
        cls.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        cls.vocab_size = 1000
        cls.rouge = ROUGEScoreTorch(cls.vocab_size, cls.device)

    def test_small_batch_short_sequences(self):
        """Test performance with small batch and short sequences."""
        batch_size, seq_len = 4, 20
        self._run_performance_test(batch_size, seq_len)

    def test_medium_batch_medium_sequences(self):
        """Test performance with medium batch and medium sequences."""
        batch_size, seq_len = 8, 50
        self._run_performance_test(batch_size, seq_len)

    def test_large_batch_short_sequences(self):
        """Test performance with large batch and short sequences."""
        batch_size, seq_len = 16, 30
        self._run_performance_test(batch_size, seq_len)

    def test_small_batch_long_sequences(self):
        """Test performance with small batch and long sequences."""
        batch_size, seq_len = 4, 100
        self._run_performance_test(batch_size, seq_len)

    def _run_performance_test(self, batch_size, seq_len):
        """Helper method to run performance test with given configuration."""
        import time

        # Create test data
        candidate_logits = torch.randn(
            batch_size, seq_len, self.vocab_size, device=self.device
        )
        reference_logits = [
            torch.randn(batch_size, seq_len, self.vocab_size, device=self.device),
            torch.randn(batch_size, seq_len, self.vocab_size, device=self.device),
        ]

        # Warm up
        _ = self.rouge.rouge_n_batch(candidate_logits, reference_logits, n=1)

        # Benchmark
        start = time.time()

        rouge_1_scores = self.rouge.rouge_n_batch(
            candidate_logits, reference_logits, n=1
        )
        rouge_2_scores = self.rouge.rouge_n_batch(
            candidate_logits, reference_logits, n=2
        )
        rouge_l_scores = self.rouge.rouge_l_batch(candidate_logits, reference_logits)
        loss = self.rouge.compute_rouge_loss(candidate_logits, reference_logits)

        end = time.time()

        # Check that computations complete within reasonable time
        elapsed_time = end - start
        self.assertLess(elapsed_time, 10.0)  # Should complete within 10 seconds

        # Check that scores are valid tensors with correct shapes
        self.assertEqual(rouge_1_scores["f1"].shape, (batch_size,))
        self.assertEqual(rouge_2_scores["f1"].shape, (batch_size,))
        self.assertEqual(rouge_l_scores["f1"].shape, (batch_size,))
        self.assertTrue(torch.isfinite(loss))

        # Check that all scores are in valid range [0, 1]
        self.assertTrue(
            torch.all(rouge_1_scores["f1"] >= 0)
            and torch.all(rouge_1_scores["f1"] <= 1)
        )
        self.assertTrue(
            torch.all(rouge_2_scores["f1"] >= 0)
            and torch.all(rouge_2_scores["f1"] <= 1)
        )
        self.assertTrue(
            torch.all(rouge_l_scores["f1"] >= 0)
            and torch.all(rouge_l_scores["f1"] <= 1)
        )

        # Check that loss is in valid range [0, 2] with 0 being best and 2 being worst (ROUGE-1 + ROUGE-L)
        self.assertGreaterEqual(loss.item(), 0.0)
        self.assertLessEqual(loss.item(), 2.0)


if __name__ == "__main__":
    unittest.main()

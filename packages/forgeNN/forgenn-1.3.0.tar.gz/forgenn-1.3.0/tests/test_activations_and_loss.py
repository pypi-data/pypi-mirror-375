"""Tests for activation functions and loss implementations.

Covers:
- Basic forward correctness of relu/sigmoid/tanh/leaky_relu/swish/gelu
- Gradient flow for each activation (sum backward -> non-zero grads where expected)
- Softmax normalization and stability
- cross_entropy_loss (vectorized) gradient shape
- tensor-level cross_entropy_loss (no full graph) basic shape and numeric sanity
- mse (vectorized) with:
  * regression (N,1) + (N,)
  * multi-class logits (N,C) + class indices (auto one-hot path)
  * direct full-shape targets
"""
import unittest
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import forgeNN as fnn
from forgeNN.tensor import Tensor
from forgeNN.vectorized import cross_entropy_loss, mse


class TestActivations(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)

    def test_relu_forward_and_grad(self):
        x = Tensor(np.array([-2., -0.5, 0., 1., 3.]), requires_grad=True)
        y = x.relu()
        self.assertTrue(np.all(y.data[:2] == 0))
        self.assertEqual(y.data[-1], 3.)
        y.sum().backward()
        # Grad passes only where input >0
        expected = np.array([0,0,0,1,1], dtype=np.float32)
        np.testing.assert_array_equal(x.grad, expected)

    def test_sigmoid_bounds_and_grad(self):
        x = Tensor(np.array([-10., 0., 10.]), requires_grad=True)
        y = x.sigmoid()
        self.assertTrue((y.data > 0).all() and (y.data < 1).all())
        y.sum().backward()
        self.assertEqual(x.grad.shape, x.shape)

    def test_tanh_range(self):
        x = Tensor(np.array([-3., 0., 3.]), requires_grad=True)
        y = x.tanh()
        self.assertTrue(np.all(y.data <= 1) and np.all(y.data >= -1))
        y.sum().backward()
        self.assertEqual(x.grad.shape, x.shape)

    def test_leaky_relu_negative_slope(self):
        x = Tensor(np.array([-2., -1., 0., 1.]), requires_grad=True)
        y = x.leaky_relu(alpha=0.1)
        self.assertAlmostEqual(y.data[0], -0.2)
        self.assertEqual(y.data[-1], 1.)
        y.sum().backward()
        # Grad should be alpha for negatives, 1 for positives, gradient of constant path 1 at 0 treated as negative or positive? Here 0 -> alpha branch currently (implementation dependent)
        self.assertEqual(x.grad.shape, x.shape)

    def test_swish_monotonic_and_grad(self):
        """Swish should be roughly monotonic; allow tiny numerical dips."""
        x = Tensor(np.linspace(-3, 3, 7), requires_grad=True)
        y = x.swish()
        diffs = np.diff(y.data)
    # Allow larger numerical / functional slight dip (swish not strictly monotonic for small sample);
    # just ensure it isn't wildly decreasing.
        self.assertGreaterEqual(float(diffs.min()), -0.2)
        y.sum().backward()
        self.assertEqual(x.grad.shape, x.shape)

    def test_gelu_forward_grad(self):
        x = Tensor(np.random.randn(10), requires_grad=True)
        y = x.gelu()
        y.sum().backward()
        self.assertEqual(x.grad.shape, x.shape)

    def test_softmax_normalization(self):
        x = Tensor(np.array([[1000., 1000.],[0.,0.]], dtype=np.float32))
        probs = x.softmax(axis=1)
        sums = probs.data.sum(axis=1)
        np.testing.assert_allclose(sums, np.array([1.,1.], dtype=np.float32), rtol=1e-5, atol=1e-5)


class TestLosses(unittest.TestCase):
    def setUp(self):
        np.random.seed(0)

    def test_cross_entropy_vectorized_shapes_and_grad(self):
        logits = Tensor(np.random.randn(5,4).astype(np.float32), requires_grad=True)
        y = np.array([0,1,2,3,1])
        loss = cross_entropy_loss(logits, y)
        self.assertEqual(loss.shape, ())
        loss.backward()
        self.assertEqual(logits.grad.shape, logits.shape)

    def test_tensor_cross_entropy_basic(self):
        logits = Tensor(np.random.randn(3,3).astype(np.float32), requires_grad=True)
        y = np.array([0,2,1])
        loss = logits.cross_entropy_loss(y)
        self.assertEqual(loss.shape, ())
        # Not full graph so backward won't propagate; ensure calling backward does not error
        loss.backward()

    def test_mse_regression_vector(self):
        preds = Tensor(np.random.randn(6,1).astype(np.float32), requires_grad=True)
        targets = np.random.randn(6).astype(np.float32)
        loss = mse(preds, targets)
        self.assertEqual(loss.shape, ())
        loss.backward()
        self.assertEqual(preds.grad.shape, preds.shape)

    def test_mse_multiclass_auto_one_hot(self):
        logits = Tensor(np.random.randn(5,3).astype(np.float32), requires_grad=True)
        y = np.array([0,1,2,1,0])
        loss = mse(logits, y)
        self.assertEqual(loss.shape, ())
        loss.backward()
        self.assertEqual(logits.grad.shape, logits.shape)

    def test_mse_full_shape_targets(self):
        logits = Tensor(np.random.randn(4,3).astype(np.float32), requires_grad=True)
        targets = np.random.randn(4,3).astype(np.float32)
        loss = mse(logits, targets)
        loss.backward()
        self.assertEqual(logits.grad.shape, logits.shape)


if __name__ == '__main__':
    unittest.main(verbosity=2)

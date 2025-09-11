"""Tests for SGD, Adam, and AdamW optimizers.

Covers:
- SGD parameter update with/without momentum & weight decay
- Adam bias correction (timestep t=1 vs corrected m_hat/v_hat)
- AdamW decoupled weight decay vs Adam L2 path
- Deferred binding (construct without params then set_params)
"""
import unittest
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import forgeNN as fnn
from forgeNN.tensor import Tensor


class TestSGD(unittest.TestCase):
    def test_basic_sgd_step(self):
        p = Tensor(np.array([1.0, -2.0], dtype=np.float32), requires_grad=True)
        p.grad = np.array([0.5, -0.5], dtype=np.float32)
        opt = fnn.SGD([p], lr=0.1)
        opt.step()
        np.testing.assert_allclose(p.data, np.array([1.0, -2.0]) - 0.1 * np.array([0.5, -0.5]), rtol=1e-6)

    def test_momentum(self):
        p = Tensor(np.array([0.0, 0.0], dtype=np.float32), requires_grad=True)
        opt = fnn.SGD([p], lr=0.1, momentum=0.9)
        # First grad
        p.grad = np.array([1.0, -1.0], dtype=np.float32)
        opt.step()  # buf = 1 * grad
        first = p.data.copy()
        # Second grad identical -> buf = 0.9*grad + grad = 1.9 * grad
        p.grad = np.array([1.0, -1.0], dtype=np.float32)
        opt.step()
        # Displacement second step should be larger than first (due to accumulated momentum)
        disp1 = np.abs(first - 0.0).mean()
        disp2 = np.abs(p.data - first).mean()
        self.assertGreater(disp2, disp1 * 0.9)  # loose inequality

    def test_weight_decay(self):
        p = Tensor(np.array([1.0], dtype=np.float32), requires_grad=True)
        p.grad = np.array([0.0], dtype=np.float32)
        opt = fnn.SGD([p], lr=0.1, weight_decay=0.5)
        before = p.data.copy()
        opt.step()
        # Update should include L2 term: grad + wd * param -> 0 + 0.5*1.0 =0.5 -> param -= 0.1*0.5
        expected = before - 0.05
        self.assertAlmostEqual(p.data.item(), expected.item(), places=6)


class TestAdam(unittest.TestCase):
    def test_bias_correction_first_step(self):
        p = Tensor(np.array([1.0, 2.0], dtype=np.float32), requires_grad=True)
        p.grad = np.array([0.1, -0.2], dtype=np.float32)
        opt = fnn.Adam([p], lr=0.001, betas=(0.9, 0.999), eps=1e-8)
        opt.step()  # t=1
        # After first step, m_hat should equal grad, v_hat should equal grad^2
        # Update ~ lr * grad / (sqrt(grad^2)+eps) ~= lr * sign(grad)
        # So parameter should decrease by ~0.001 * sign(grad)
        # For 0.1 -> sign positive, for -0.2 -> sign negative (so increase)
        self.assertLess(p.data[0], 1.0)
        self.assertGreater(p.data[1], 2.0)

    def test_weight_decay_classic(self):
        p = Tensor(np.array([2.0], dtype=np.float32), requires_grad=True)
        p.grad = np.array([0.0], dtype=np.float32)
        opt = fnn.Adam([p], lr=0.01, weight_decay=0.1)
        opt.step()
        # With classic L2, effective grad = 0 + 0.1 * 2.0 = 0.2 -> update ~ lr * 0.2
        self.assertLess(p.data.item(), 2.0)


class TestAdamW(unittest.TestCase):
    def test_decoupled_weight_decay(self):
        p1 = Tensor(np.array([1.0], dtype=np.float32), requires_grad=True)
        p1.grad = np.array([0.0], dtype=np.float32)
        aw = fnn.AdamW([p1], lr=0.01, weight_decay=0.1)
        aw.step()
        # AdamW decays directly: p -= lr * wd * p -> 1 - 0.01*0.1*1 = 0.999
        self.assertAlmostEqual(p1.data.item(), 0.999, places=6)

    def test_diff_vs_adam_classic_decay(self):
        # Show AdamW decay larger magnitude difference vs same Adam config with weight_decay
        p_adam = Tensor(np.array([1.0], dtype=np.float32), requires_grad=True)
        p_adam.grad = np.array([0.0], dtype=np.float32)
        opt_adam = fnn.Adam([p_adam], lr=0.01, weight_decay=0.1)
        opt_adam.step()  # update ~ lr*wd*param (through gradient path)

        p_adamw = Tensor(np.array([1.0], dtype=np.float32), requires_grad=True)
        p_adamw.grad = np.array([0.0], dtype=np.float32)
        opt_adamw = fnn.AdamW([p_adamw], lr=0.01, weight_decay=0.1)
        opt_adamw.step()
        # Values should differ slightly (due to epsilon / moment initialization differences)
        self.assertNotAlmostEqual(p_adam.data.item(), p_adamw.data.item(), places=8)


class TestDeferredBinding(unittest.TestCase):
    def test_deferred_binding_sets_state(self):
        # Construct Adam without params
        opt = fnn.Adam(lr=1e-3)
        model = fnn.Sequential([
            fnn.Dense(8, in_features=4) @ 'relu',
            fnn.Dense(3)
        ])
        # forward to init params
        _ = model(Tensor(np.random.randn(2,4).astype(np.float32)))
        params = model.parameters()
        opt.set_params(params)
        # m and v buffers should now match param shapes
        self.assertEqual(len(opt.m), len(params))
        self.assertTrue(all(m.shape == p.data.shape for m, p in zip(opt.m, params)))


if __name__ == '__main__':
    unittest.main(verbosity=2)

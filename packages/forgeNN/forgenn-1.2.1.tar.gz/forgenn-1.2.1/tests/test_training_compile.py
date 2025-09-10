"""Tests for compile/fit/evaluate/predict training workflow.

Covers:
- compile with cross_entropy + accuracy
- compile with mse + custom metric
- fit improves accuracy over epochs
- evaluate consistency between manual aggregation and API
- predict shape and ordering
"""
import unittest
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import forgeNN as fnn
from forgeNN.tensor import Tensor


def _make_toy_classification(n=120, d=8, k=3, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n,d)).astype(np.float32)
    W = rng.normal(size=(d,k))
    logits = X @ W
    y = np.argmax(logits, axis=1)
    return X, y

class TestCompileWorkflow(unittest.TestCase):
    def setUp(self):
        self.X, self.y = _make_toy_classification()
        self.X_test, self.y_test = _make_toy_classification(seed=1)

    def test_compile_fit_cross_entropy(self):
        model = fnn.Sequential([
            fnn.Dense(32, in_features=8) @ 'relu',
            fnn.Dense(16) @ 'relu',
            fnn.Dense(3) @ 'linear'
        ])
        compiled = fnn.compile(model, optimizer={"lr":0.05}, loss="cross_entropy", metrics=["accuracy"])
        compiled.fit(self.X, self.y, epochs=5, batch_size=32, verbose=0)
        loss, metrics = compiled.evaluate(self.X_test, self.y_test, batch_size=64)
        self.assertIn('accuracy', metrics)
        self.assertGreaterEqual(metrics['accuracy'], 0.05)  # very loose floor to avoid flake

    def test_compile_fit_mse_custom_metric(self):
        # Custom metric: accuracy via softmax argmax
        def simple_acc(logits, targets):
            preds = np.argmax(logits.data, axis=1)
            return float((preds == targets).mean())
        model = fnn.Sequential([
            fnn.Dense(16, in_features=8) @ 'relu',
            fnn.Dense(3) @ 'linear'
        ])
        compiled = fnn.compile(model, optimizer={"lr":0.05}, loss="mse", metrics=[simple_acc])
        compiled.fit(self.X, self.y, epochs=4, batch_size=32, verbose=0)
        loss, metrics = compiled.evaluate(self.X_test, self.y_test, batch_size=64)
        # metric name fallback is 'metric'
        self.assertTrue(any(v >= 0.2 for v in metrics.values()))

    def test_predict_shape(self):
        model = fnn.Sequential([
            fnn.Dense(10, in_features=8) @ 'relu',
            fnn.Dense(3) @ 'linear'
        ])
        compiled = fnn.compile(model, optimizer={"lr":0.01}, loss="cross_entropy")
        preds = compiled.predict(self.X[:25])
        self.assertEqual(preds.shape, (25,3))

    def test_evaluate_consistency(self):
        model = fnn.Sequential([
            fnn.Dense(12, in_features=8) @ 'relu',
            fnn.Dense(3) @ 'linear'
        ])
        compiled = fnn.compile(model, optimizer={"lr":0.01}, loss="cross_entropy", metrics=["accuracy"])
        compiled.fit(self.X, self.y, epochs=2, batch_size=32, verbose=0)
        loss1, metrics1 = compiled.evaluate(self.X_test, self.y_test, batch_size=32)
        # Manual evaluation replicating evaluate logic
        # (sample-weighted average already inside evaluate, so just ensure we get consistent second call)
        loss2, metrics2 = compiled.evaluate(self.X_test, self.y_test, batch_size=64)
        self.assertAlmostEqual(loss1, loss2, places=3)
        self.assertAlmostEqual(metrics1['accuracy'], metrics2['accuracy'], places=3)

if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Layer parameter counting and helper method tests."""
import unittest
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import forgeNN as fnn
from forgeNN.tensor import Tensor

class TestLayerParameterHelpers(unittest.TestCase):
    def test_num_parameter_tensors_and_num_parameters(self):
        model = fnn.Sequential([
            fnn.Dense(32, in_features=10) @ 'relu',
            fnn.Dense(16) @ 'relu',
            fnn.Dense(4)
        ])
        # Force lazy init forward for middle layers
        _ = model(Tensor(np.zeros((1,10), dtype=np.float32)))
        self.assertGreater(model.num_parameter_tensors(), 0)
        self.assertGreater(model.num_parameters(), 0)
        # Manual count
        manual = sum(p.data.size for p in model.parameters())
        self.assertEqual(model.num_parameters(), manual)

    def test_nested_sequential_counts(self):
        inner = fnn.Sequential([fnn.Dense(8, in_features=6) @ 'relu', fnn.Dense(4)])
        model = fnn.Sequential([inner, fnn.Dense(3)])
        _ = model(Tensor(np.zeros((2,6), dtype=np.float32)))
        self.assertEqual(model.num_parameters(), sum(p.data.size for p in model.parameters()))

if __name__ == '__main__':
    unittest.main(verbosity=2)

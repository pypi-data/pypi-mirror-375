"""
Unit Tests for forgeNN Tensor Shape Operations and Matrix Operations
===================================================================

Comprehensive test suite for tensor operations including:
- Shape operations: reshape(), view(), flatten(), contiguous(), transpose(), squeeze(), unsqueeze()
- Matrix operations: matmul() / @ operator
- Proper test isolation, gradient flow validation, and edge case coverage
"""

import unittest
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from forgeNN.tensor import Tensor
from forgeNN import Sequential, Dense, Flatten, VectorizedOptimizer
from forgeNN.functions.activation import RELU


class TestTensorShapeOperations(unittest.TestCase):
    """Test suite for tensor shape manipulation operations."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Standard test tensors
        self.tensor_1d = Tensor(np.arange(6, dtype=np.float32))
        self.tensor_2d = Tensor(np.arange(12, dtype=np.float32).reshape(3, 4))
        self.tensor_3d = Tensor(np.arange(24, dtype=np.float32).reshape(2, 3, 4))
        self.empty_tensor = Tensor(np.array([], dtype=np.float32))
        self.single_tensor = Tensor(np.array([42.0], dtype=np.float32))
        
    def tearDown(self):
        """Clean up after each test method."""
        # Reset gradients
        for tensor in [self.tensor_1d, self.tensor_2d, self.tensor_3d, 
                      self.empty_tensor, self.single_tensor]:
            if tensor.grad is not None:
                tensor.zero_grad()


class TestReshape(TestTensorShapeOperations):
    """Test cases for reshape() method."""
    
    def test_basic_reshape(self):
        """Test basic reshape functionality."""
        # 1D to 2D
        reshaped = self.tensor_1d.reshape(2, 3)
        self.assertEqual(reshaped.shape, (2, 3))
        self.assertEqual(reshaped.size, 6)
        
        # 2D to 1D
        reshaped = self.tensor_2d.reshape(12)
        self.assertEqual(reshaped.shape, (12,))
        self.assertEqual(reshaped.size, 12)
        
        # 3D to 2D
        reshaped = self.tensor_3d.reshape(6, 4)
        self.assertEqual(reshaped.shape, (6, 4))
        self.assertEqual(reshaped.size, 24)
    
    def test_reshape_with_inference(self):
        """Test reshape with -1 dimension inference."""
        # Infer last dimension
        reshaped = self.tensor_1d.reshape(2, -1)
        self.assertEqual(reshaped.shape, (2, 3))
        
        # Infer first dimension
        reshaped = self.tensor_2d.reshape(-1, 4)
        self.assertEqual(reshaped.shape, (3, 4))
        
        # Infer middle dimension
        reshaped = self.tensor_3d.reshape(2, -1, 4)
        self.assertEqual(reshaped.shape, (2, 3, 4))
        
        # Infer to 1D
        reshaped = self.tensor_2d.reshape(-1)
        self.assertEqual(reshaped.shape, (12,))
    
    def test_reshape_tuple_input(self):
        """Test reshape with tuple input."""
        # Test both syntaxes
        reshaped1 = self.tensor_1d.reshape((2, 3))
        reshaped2 = self.tensor_1d.reshape(2, 3)
        
        self.assertEqual(reshaped1.shape, reshaped2.shape)
        np.testing.assert_array_equal(reshaped1.data, reshaped2.data)
    
    def test_reshape_gradient_flow(self):
        """Test gradient flow through reshape operations."""
        x = Tensor(np.random.randn(6), requires_grad=True)
        y = x.reshape(2, 3)
        z = y.sum()
        z.backward()
        
        # Check gradient shape and values
        self.assertEqual(x.grad.shape, x.shape)
        np.testing.assert_array_equal(x.grad, np.ones_like(x.data))
    
    def test_reshape_chaining(self):
        """Test chaining multiple reshape operations."""
        result = self.tensor_1d.reshape(2, 3).reshape(6, 1).reshape(3, 2)
        self.assertEqual(result.shape, (3, 2))
        
        # Gradient flow through chain
        result.sum().backward()
        self.assertEqual(self.tensor_1d.grad.shape, self.tensor_1d.shape)
    
    def test_reshape_empty_tensor(self):
        """Test reshape with empty tensors."""
        reshaped = self.empty_tensor.reshape(0, 5)
        self.assertEqual(reshaped.shape, (0, 5))
        self.assertEqual(reshaped.size, 0)
        
        # Gradient flow with empty
        reshaped.sum().backward()
        self.assertEqual(self.empty_tensor.grad.shape, (0,))
    
    def test_reshape_single_element(self):
        """Test reshape with single element tensor."""
        # Various single element shapes
        shapes = [(1,), (1, 1), (1, 1, 1)]
        for shape in shapes:
            reshaped = self.single_tensor.reshape(shape)
            self.assertEqual(reshaped.shape, shape)
            self.assertEqual(reshaped.size, 1)
    
    def test_reshape_error_cases(self):
        """Test reshape error handling."""
        # Multiple -1s
        with self.assertRaises(ValueError):
            self.tensor_1d.reshape(-1, -1)
        
        # Incompatible size
        with self.assertRaises(ValueError):
            self.tensor_1d.reshape(2, 4)  # 6 elements can't fit 2x4=8
        
        # Zero dimension with non-empty tensor
        with self.assertRaises(ValueError):
            self.tensor_1d.reshape(-1, 0)
    
    def test_reshape_dtype_preservation(self):
        """Test that reshape preserves data type."""
        reshaped = self.tensor_1d.reshape(2, 3)
        self.assertEqual(reshaped.data.dtype, np.float32)
        self.assertEqual(reshaped.data.dtype, self.tensor_1d.data.dtype)


class TestView(TestTensorShapeOperations):
    """Test cases for view() method."""
    
    def test_basic_view(self):
        """Test basic view functionality."""
        # 1D to 2D view
        viewed = self.tensor_1d.view(2, 3)
        self.assertEqual(viewed.shape, (2, 3))
        self.assertEqual(viewed.size, 6)
        
        # Test memory sharing
        self.tensor_1d.data[0] = 999
        self.assertEqual(viewed.data[0, 0], 999)
    
    def test_view_memory_sharing(self):
        """Test that view shares memory with original tensor."""
        viewed = self.tensor_2d.view(12)
        
        # Modify original
        original_value = self.tensor_2d.data[0, 0]
        self.tensor_2d.data[0, 0] = 888
        self.assertEqual(viewed.data[0], 888)
        
        # Modify view
        viewed.data[1] = 777
        self.assertEqual(self.tensor_2d.data[0, 1], 777)
        
        # Restore original value
        self.tensor_2d.data[0, 0] = original_value
    
    def test_view_with_inference(self):
        """Test view with -1 dimension inference."""
        viewed = self.tensor_1d.view(-1, 2)
        self.assertEqual(viewed.shape, (3, 2))
        
        viewed = self.tensor_2d.view(2, -1)
        self.assertEqual(viewed.shape, (2, 6))
    
    def test_view_gradient_flow(self):
        """Test gradient flow through view operations."""
        x = Tensor(np.random.randn(6), requires_grad=True)
        y = x.view(2, 3)
        z = y.sum()
        z.backward()
        
        self.assertEqual(x.grad.shape, x.shape)
        np.testing.assert_array_equal(x.grad, np.ones_like(x.data))
    
    def test_view_contiguous_requirement(self):
        """Test that view requires contiguous tensors."""
        # Create non-contiguous tensor manually
        noncontiguous = Tensor.__new__(Tensor)
        noncontiguous.data = self.tensor_2d.data.T  # Non-contiguous
        noncontiguous.grad = None
        noncontiguous.requires_grad = True
        noncontiguous.shape = noncontiguous.data.shape
        noncontiguous.size = noncontiguous.data.size
        noncontiguous._children = set()
        noncontiguous._op = ''
        noncontiguous._backward = lambda: None
        
        # Should raise error for non-contiguous
        with self.assertRaises(RuntimeError):
            noncontiguous.view(-1)
    
    def test_view_error_cases(self):
        """Test view error handling."""
        # Multiple -1s
        with self.assertRaises(ValueError):
            self.tensor_1d.view(-1, -1)
        
        # Incompatible size
        with self.assertRaises(ValueError):
            self.tensor_1d.view(2, 4)


class TestSequentialAndLayers(unittest.TestCase):
    """Tests for Sequential, Dense, Flatten, and ActivationWrapper."""

    def test_dense_lazy_init_and_forward(self):
        x = Tensor(np.random.randn(4, 3).astype(np.float32))
        dense = Dense(5)  # in_features inferred on first forward
        y = dense(x)
        self.assertEqual(y.shape, (4, 5))
        params = dense.parameters()
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0].shape, (3, 5))
        self.assertEqual(params[1].shape, (5,))

    def test_activation_wrapper_with_string(self):
        x = Tensor(np.array([[-1.0, 2.0, -3.0]], dtype=np.float32))
        layer = Dense(3)
        wrapped = layer @ 'relu'
        y = wrapped(x)
        self.assertEqual(y.shape, (1, 3))

    def test_activation_wrapper_with_callable(self):
        x = Tensor(np.array([[-1.0, 2.0, -3.0]], dtype=np.float32))
        layer = Dense(3)
        wrapped = layer @ (lambda t: t.relu())
        y = wrapped(x)
        self.assertEqual(y.shape, (1, 3))

    def test_activation_wrapper_with_class_instance(self):
        x = Tensor(np.array([[-1.0, 2.0, -3.0]], dtype=np.float32))
        layer = Dense(3)
        wrapped = layer @ RELU()
        y = wrapped(x)
        self.assertEqual(y.shape, (1, 3))

    def test_sequential_forward_and_params(self):
        model = Sequential([
            Dense(4) @ 'relu',
            Flatten(),
            Dense(2) @ 'linear',
        ])
        x = Tensor(np.random.randn(3, 4).astype(np.float32))
        out = model(x)
        self.assertEqual(out.shape, (3, 2))
        # parameters should aggregate from both Dense layers (2 layers x [W,b])
        self.assertEqual(len(model.parameters()), 4)

    def test_sequential_with_flatten_on_3d_input(self):
        model = Sequential([
            Flatten(),
            Dense(5)  # will lazy-init to last dim size 2*3=6
        ])
        x = Tensor(np.random.randn(2, 2, 3).astype(np.float32))
        y = model(x)
        self.assertEqual(y.shape, (2, 5))

    def test_sequential_zero_grad(self):
        model = Sequential([Dense(3) @ 'relu', Dense(1)])
        x = Tensor(np.random.randn(2, 3).astype(np.float32))
        y = model(x).sum()
        y.backward()
        # then zero gradients
        model.zero_grad()
        for p in model.parameters():
            self.assertTrue(np.allclose(p.grad, 0))

    def test_nested_sequential_zero_grad(self):
        inner = Sequential([Dense(4) @ 'relu'])
        model = Sequential([inner, Dense(2)])
        x = Tensor(np.random.randn(3, 4).astype(np.float32))
        loss = model(x).sum()
        loss.backward()
        model.zero_grad()
        for p in model.parameters():
            self.assertTrue(np.allclose(p.grad, 0))

    def test_optimizer_works_with_sequential(self):
        model = Sequential([Dense(4) @ 'relu', Dense(2)])
        # Initialize lazy parameters with a dummy forward before creating optimizer
        _ = model(Tensor(np.random.randn(1, 4).astype(np.float32)))
        opt = VectorizedOptimizer(model.parameters(), lr=0.01)
        x = Tensor(np.random.randn(5, 4).astype(np.float32))
        y = model(x)
        loss = y.sum()
        opt.zero_grad()
        loss.backward()
        # capture param snapshot
        before = [p.data.copy() for p in model.parameters()]
        opt.step()
        after = [p.data for p in model.parameters()]
        # ensure at least one parameter changed
        self.assertTrue(any(not np.allclose(b, a) for b, a in zip(before, after)))

    def test_optimizer_with_momentum_updates_and_buffers(self):
        model = Sequential([Dense(3) @ 'relu', Dense(1)])
        # initialize params
        _ = model(Tensor(np.random.randn(1, 3).astype(np.float32)))
        params = model.parameters()
        opt = VectorizedOptimizer(params, lr=0.05, momentum=0.9)
        x = Tensor(np.random.randn(4, 3).astype(np.float32))
        y = model(x)
        loss = y.sum()
        opt.zero_grad()
        loss.backward()
        before = [p.data.copy() for p in params]
        opt.step()
        after = [p.data for p in params]
        # parameters should change
        self.assertTrue(any(not np.allclose(b, a) for b, a in zip(before, after)))
        # momentum buffers should exist and be non-zero for params that had grads
        self.assertIsNotNone(opt.momentum_buffers)
        self.assertEqual(len(opt.momentum_buffers), len(params))
        self.assertTrue(any(np.any(buf != 0) for buf in opt.momentum_buffers))

    def test_dense_with_explicit_in_features(self):
        dense = Dense(2, in_features=4)
        x = Tensor(np.random.randn(3, 4).astype(np.float32))
        y = dense(x)
        self.assertEqual(y.shape, (3, 2))
        W, b = dense.parameters()
        self.assertEqual(W.shape, (4, 2))
        self.assertEqual(b.shape, (2,))


class TestFlatten(TestTensorShapeOperations):
    """Test cases for flatten() method."""
    
    def test_basic_flatten(self):
        """Test basic flatten functionality."""
        # 2D to 1D
        flattened = self.tensor_2d.flatten()
        self.assertEqual(flattened.shape, (12,))
        self.assertEqual(flattened.size, 12)
        
        # 3D to 1D
        flattened = self.tensor_3d.flatten()
        self.assertEqual(flattened.shape, (24,))
        self.assertEqual(flattened.size, 24)
        
        # 1D remains 1D
        flattened = self.tensor_1d.flatten()
        self.assertEqual(flattened.shape, (6,))
    
    def test_flatten_data_preservation(self):
        """Test that flatten preserves data order."""
        original_data = self.tensor_2d.data.copy()
        flattened = self.tensor_2d.flatten()
        
        # Should be same as reshape(-1)
        expected = self.tensor_2d.reshape(-1)
        np.testing.assert_array_equal(flattened.data, expected.data)
    
    def test_flatten_gradient_flow(self):
        """Test gradient flow through flatten."""
        x = Tensor(np.random.randn(2, 3), requires_grad=True)
        y = x.flatten()
        z = y.sum()
        z.backward()
        
        self.assertEqual(x.grad.shape, x.shape)
        np.testing.assert_array_equal(x.grad, np.ones_like(x.data))
    
    def test_flatten_empty_and_single(self):
        """Test flatten with edge case tensors."""
        # Empty tensor
        flattened = self.empty_tensor.flatten()
        self.assertEqual(flattened.shape, (0,))
        
        # Single element
        flattened = self.single_tensor.flatten()
        self.assertEqual(flattened.shape, (1,))


class TestContiguous(TestTensorShapeOperations):
    """Test cases for contiguous() method."""
    
    def test_already_contiguous(self):
        """Test contiguous() with already contiguous tensors."""
        # Should return self for contiguous tensors
        result = self.tensor_1d.contiguous()
        self.assertIs(result, self.tensor_1d)
        
        result = self.tensor_2d.contiguous()
        self.assertIs(result, self.tensor_2d)
    
    def test_make_contiguous(self):
        """Test making non-contiguous tensor contiguous."""
        # Create non-contiguous tensor
        noncontiguous = Tensor.__new__(Tensor)
        base_data = np.arange(12, dtype=np.float32).reshape(3, 4)
        noncontiguous.data = base_data.T  # Non-contiguous
        noncontiguous.grad = np.zeros_like(noncontiguous.data)
        noncontiguous.requires_grad = True
        noncontiguous.shape = noncontiguous.data.shape
        noncontiguous.size = noncontiguous.data.size
        noncontiguous._children = set()
        noncontiguous._op = ''
        noncontiguous._backward = lambda: None
        
        # Check it's non-contiguous
        self.assertFalse(noncontiguous.data.flags['C_CONTIGUOUS'])
        
        # Make contiguous
        contiguous = noncontiguous.contiguous()
        self.assertTrue(contiguous.data.flags['C_CONTIGUOUS'])
        self.assertIsNot(contiguous, noncontiguous)  # Should be new tensor
        
        # Data should be the same
        np.testing.assert_array_equal(contiguous.data, noncontiguous.data)
    
    def test_contiguous_gradient_flow(self):
        """Test gradient flow through contiguous operation."""
        # Create non-contiguous tensor
        noncontiguous = Tensor.__new__(Tensor)
        noncontiguous.data = np.arange(6, dtype=np.float32).reshape(2, 3).T
        noncontiguous.grad = np.zeros_like(noncontiguous.data)
        noncontiguous.requires_grad = True
        noncontiguous.shape = noncontiguous.data.shape
        noncontiguous.size = noncontiguous.data.size
        noncontiguous._children = set()
        noncontiguous._op = ''
        noncontiguous._backward = lambda: None
        
        # Make contiguous and test gradient flow
        contiguous = noncontiguous.contiguous()
        result = contiguous.sum()
        result.backward()
        
        # Check gradients
        self.assertEqual(noncontiguous.grad.shape, noncontiguous.shape)
        np.testing.assert_array_equal(noncontiguous.grad, np.ones_like(noncontiguous.data))


class TestGradientNumerical(TestTensorShapeOperations):
    """Numerical gradient checking for shape operations."""
    
    def test_reshape_simple_gradient(self):
        """Test simple reshape gradient flow."""
        x = Tensor(np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]), requires_grad=True)
        y = x.reshape(2, 3)
        z = y.sum()
        z.backward()
        
        # For sum(), gradient should be all ones
        expected = np.ones_like(x.data)
        np.testing.assert_array_equal(x.grad, expected)
    
    def test_view_simple_gradient(self):
        """Test simple view gradient flow."""
        x = Tensor(np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]), requires_grad=True)
        y = x.view(2, 3)
        z = y.sum()
        z.backward()
        
        # For sum(), gradient should be all ones
        expected = np.ones_like(x.data)
        np.testing.assert_array_equal(x.grad, expected)
    
    def test_complex_gradient_flow(self):
        """Test gradient flow through complex operations."""
        x = Tensor(np.random.randn(12), requires_grad=True)
        
        # Complex chain: reshape -> view -> flatten -> reshape
        y1 = x.reshape(3, 4)
        y2 = y1.view(12)
        y3 = y2.reshape(4, 3)
        y4 = y3.flatten()
        result = y4.sum()
        
        result.backward()
        
        # Gradient should be all ones (since we're just summing)
        expected = np.ones_like(x.data)
        np.testing.assert_array_equal(x.grad, expected)

class TestTranspose(TestTensorShapeOperations):
    """Test cases for transpose() method."""
    
    def test_basic_transpose(self):
        """Test basic transpose functionality."""
        # 2D transpose: swap dimensions (3,4) -> (4,3)
        transposed = self.tensor_2d.transpose(1, 0)
        self.assertEqual(transposed.shape, (4, 3))
        expected_data = self.tensor_2d.data.T
        np.testing.assert_array_equal(transposed.data, expected_data)
        
        # 2D default transpose should be same as (1, 0)
        default_transposed = self.tensor_2d.transpose()
        self.assertEqual(default_transposed.shape, (4, 3))
        np.testing.assert_array_equal(default_transposed.data, expected_data)
        
        # 3D transpose: (2,3,4) -> (2,4,3)
        transposed_3d = self.tensor_3d.transpose(0, 2, 1)
        self.assertEqual(transposed_3d.shape, (2, 4, 3))
        expected_data_3d = self.tensor_3d.data.transpose(0, 2, 1)
        np.testing.assert_array_equal(transposed_3d.data, expected_data_3d)
    
    def test_transpose_gradient_flow(self):
        """Test gradient flow through transpose operations."""
        x = Tensor(np.random.randn(2, 3), requires_grad=True)
        y = x.transpose(1, 0)
        z = y.sum()
        z.backward()
        
        self.assertEqual(x.grad.shape, x.shape)
        np.testing.assert_array_equal(x.grad, y.grad.transpose(1, 0))

class TestSqueezeUnsqueeze(TestTensorShapeOperations):
    """Test cases for squeeze() and unsqueeze() methods."""
    
    def test_basic_squeeze(self):
        """Test basic squeeze functionality."""
        # Create tensor with size-1 dimensions
        tensor = Tensor(np.random.randn(1, 3, 1, 4, 1))
        
        # Squeeze all size-1 dimensions
        squeezed = tensor.squeeze()
        self.assertEqual(squeezed.shape, (3, 4))
        
        # Squeeze specific dimension
        tensor2 = Tensor(np.random.randn(2, 1, 4))
        squeezed_dim = tensor2.squeeze(1)
        self.assertEqual(squeezed_dim.shape, (2, 4))
        
        # Squeeze dimension that is not size-1 should raise error
        with self.assertRaises(ValueError):
            tensor2.squeeze(0)  # dim 0 has size 2
    
    def test_basic_unsqueeze(self):
        """Test basic unsqueeze functionality."""
        # Unsqueeze to add size-1 dimensions
        unsqueezed = self.tensor_2d.unsqueeze(0)  # Add dim at front
        self.assertEqual(unsqueezed.shape, (1, 3, 4))
        
        unsqueezed = self.tensor_2d.unsqueeze(1)  # Add dim in middle
        self.assertEqual(unsqueezed.shape, (3, 1, 4))
        
        unsqueezed = self.tensor_2d.unsqueeze(-1)  # Add dim at end
        self.assertEqual(unsqueezed.shape, (3, 4, 1))
    
    def test_squeeze_gradient_flow(self):
        """Test gradient flow through squeeze operation."""
        x = Tensor(np.random.randn(1, 3, 1), requires_grad=True)
        y = x.squeeze()
        z = y.sum()
        z.backward()
        
        self.assertEqual(x.grad.shape, x.shape)
        np.testing.assert_array_equal(x.grad, np.ones_like(x.data))
    
    def test_unsqueeze_gradient_flow(self):
        """Test gradient flow through unsqueeze operation."""
        x = Tensor(np.random.randn(3, 4), requires_grad=True)
        y = x.unsqueeze(0)
        z = y.sum()
        z.backward()
        
        self.assertEqual(x.grad.shape, x.shape)
        np.testing.assert_array_equal(x.grad, np.ones_like(x.data))


class TestMatrixOperations(TestTensorShapeOperations):
    """Test cases for matrix multiplication operations."""
    
    def test_basic_matmul(self):
        """Test basic matrix multiplication functionality."""
        # Test 2D @ 2D
        a = Tensor(np.array([[1, 2], [3, 4]], dtype=np.float32))
        b = Tensor(np.array([[5, 6], [7, 8]], dtype=np.float32))
        
        result = a @ b
        expected = np.array([[19, 22], [43, 50]], dtype=np.float32)
        
        np.testing.assert_array_equal(result.data, expected)
        self.assertEqual(result.shape, (2, 2))
    
    def test_matmul_shapes(self):
        """Test matrix multiplication with different valid shapes."""
        # Matrix @ Vector
        matrix = Tensor(np.random.randn(3, 4).astype(np.float32))
        vector = Tensor(np.random.randn(4, 1).astype(np.float32))
        result = matrix @ vector
        self.assertEqual(result.shape, (3, 1))
        
        # Vector @ Matrix  
        vector2 = Tensor(np.random.randn(1, 3).astype(np.float32))
        result2 = vector2 @ matrix
        self.assertEqual(result2.shape, (1, 4))
        
        # Batch matrix multiplication
        batch_a = Tensor(np.random.randn(2, 3, 4).astype(np.float32))
        batch_b = Tensor(np.random.randn(2, 4, 5).astype(np.float32))
        result3 = batch_a @ batch_b
        self.assertEqual(result3.shape, (2, 3, 5))
    
    def test_matmul_with_scalars(self):
        """Test matrix multiplication with tensor-scalar conversion."""
        matrix = Tensor(np.array([[1, 2], [3, 4]], dtype=np.float32))
        
        # Test with numpy array
        numpy_matrix = np.array([[2, 0], [0, 2]], dtype=np.float32)
        result = matrix @ numpy_matrix
        expected = np.array([[2, 4], [6, 8]], dtype=np.float32)
        np.testing.assert_array_equal(result.data, expected)
    
    def test_matmul_gradient_flow(self):
        """Test gradient flow through matrix multiplication."""
        a = Tensor(np.array([[1, 2], [3, 4]], dtype=np.float32), requires_grad=True)
        b = Tensor(np.array([[5, 6], [7, 8]], dtype=np.float32), requires_grad=True)
        
        result = a @ b
        loss = result.sum()
        loss.backward()
        
        # Check gradients exist and have correct shapes
        self.assertEqual(a.grad.shape, a.shape)
        self.assertEqual(b.grad.shape, b.shape)
        
        # For matrix multiplication: if C = A @ B and loss = sum(C)
        # dL/dA = ones(C.shape) @ B.T = [[1,1],[1,1]] @ [[5,7],[6,8]] = [[11,15],[11,15]]
        # dL/dB = A.T @ ones(C.shape) = [[1,3],[2,4]] @ [[1,1],[1,1]] = [[4,4],[6,6]]
        expected_a_grad = np.array([[11, 15], [11, 15]], dtype=np.float32)
        expected_b_grad = np.array([[4, 4], [6, 6]], dtype=np.float32)
        
        np.testing.assert_array_equal(a.grad, expected_a_grad)
        np.testing.assert_array_equal(b.grad, expected_b_grad)
    
    def test_matmul_chain_rule(self):
        """Test matrix multiplication in a computation chain."""
        a = Tensor(np.array([[1, 2]], dtype=np.float32), requires_grad=True)
        b = Tensor(np.array([[3], [4]], dtype=np.float32), requires_grad=True)
        
        # Forward: a @ b -> relu -> sum
        result1 = a @ b  # Shape: (1, 1)
        result2 = result1.relu()
        result3 = result2.sum()
        
        result3.backward()
        
        # Check gradients propagate correctly
        self.assertIsNotNone(a.grad)
        self.assertIsNotNone(b.grad)
        self.assertEqual(a.grad.shape, (1, 2))
        self.assertEqual(b.grad.shape, (2, 1))
    
    def test_matmul_broadcasting(self):
        """Test matrix multiplication with broadcasting behavior."""
        # Test batch @ single matrix
        batch = Tensor(np.random.randn(3, 2, 4).astype(np.float32))
        single = Tensor(np.random.randn(4, 5).astype(np.float32))
        
        result = batch @ single
        self.assertEqual(result.shape, (3, 2, 5))
        
        # Verify each batch element computed correctly
        for i in range(3):
            expected = batch.data[i] @ single.data
            np.testing.assert_array_almost_equal(result.data[i], expected, decimal=5)
    
    def test_matmul_error_cases(self):
        """Test matrix multiplication error handling."""
        a = Tensor(np.random.randn(2, 3).astype(np.float32))
        b = Tensor(np.random.randn(4, 5).astype(np.float32))
        
        # Should raise error for incompatible shapes
        with self.assertRaises(ValueError):
            result = a @ b
    
    def test_matmul_numerical_stability(self):
        """Test matrix multiplication with edge cases."""
        # Test with zeros
        zeros_a = Tensor(np.zeros((2, 3), dtype=np.float32))
        regular_b = Tensor(np.random.randn(3, 4).astype(np.float32))
        result = zeros_a @ regular_b
        np.testing.assert_array_equal(result.data, np.zeros((2, 4)))
        
        # Test with ones
        ones_a = Tensor(np.ones((2, 3), dtype=np.float32))
        result2 = ones_a @ regular_b
        expected = np.sum(regular_b.data, axis=0, keepdims=True)
        expected = np.repeat(expected, 2, axis=0)
        np.testing.assert_array_almost_equal(result2.data, expected, decimal=5)
    
    def test_matmul_memory_efficiency(self):
        """Test matrix multiplication memory usage."""
        # Test that intermediate computations don't explode memory
        large_a = Tensor(np.random.randn(100, 50).astype(np.float32))
        large_b = Tensor(np.random.randn(50, 75).astype(np.float32))
        
        result = large_a @ large_b
        self.assertEqual(result.shape, (100, 75))
        
        # Verify computation is correct by spot-checking
        expected_element = np.dot(large_a.data[0], large_b.data[:, 0])
        self.assertAlmostEqual(result.data[0, 0], expected_element, places=5)

class TestDotProduct(TestTensorShapeOperations):
    """Test cases for dot() method."""
    
    def test_basic_dot(self):
        """Test basic dot product functionality."""
        a = Tensor(np.array([1, 2, 3], dtype=np.float32))
        b = Tensor(np.array([4, 5, 6], dtype=np.float32))
        
        result = a.dot(b)
        expected = np.dot(a.data, b.data)
        
        self.assertEqual(result.shape, ())
        self.assertEqual(result.data, expected)
    
    def test_dot_gradient_flow(self):
        """Test gradient flow through dot product."""
        a = Tensor(np.array([1.0, 2.0, 3.0], dtype=np.float32), requires_grad=True)
        b = Tensor(np.array([4.0, 5.0, 6.0], dtype=np.float32), requires_grad=True)
        
        result = a.dot(b)
        result.backward()
        
        # Gradients should be equal to the other vector
        np.testing.assert_array_equal(a.grad, b.data)
        np.testing.assert_array_equal(b.grad, a.data)
    
    def test_dot_error_cases(self):
        """Test dot product error handling."""
        a = Tensor(np.array([1, 2], dtype=np.float32))
        b = Tensor(np.array([3, 4, 5], dtype=np.float32))
        
        # Should raise error for different sizes
        with self.assertRaises(ValueError):
            result = a.dot(b)
        
class TestGELU(TestTensorShapeOperations):
    """Test cases for GELU activation function."""
    
    def test_gelu_basic(self):
        """Test basic GELU functionality."""
        x = Tensor(np.array([-1.0, 0.0, 1.0], dtype=np.float32))
        y = x.gelu()
        
        # Expected values computed using the GELU formula
        expected = 0.5 * x.data * (1 + np.tanh(np.sqrt(2 / np.pi) * (x.data + 0.044715 * np.power(x.data, 3))))
        np.testing.assert_array_almost_equal(y.data, expected, decimal=5)
    
    def test_gelu_gradient_flow(self):
        """Test gradient flow through GELU."""
        x = Tensor(np.random.randn(5).astype(np.float32), requires_grad=True)
        y = x.gelu()
        z = y.sum()
        z.backward()
        
        self.assertEqual(x.grad.shape, x.shape)
        self.assertIsNotNone(x.grad)
    
    def test_gelu_edge_cases(self):
        """Test GELU with edge case inputs."""
        # Very large positive
        large_pos = Tensor(np.array([1e6], dtype=np.float32))
        gelu_large_pos = large_pos.gelu()
        np.testing.assert_array_almost_equal(gelu_large_pos.data, large_pos.data, decimal=5)
        
        # Very large negative
        large_neg = Tensor(np.array([-1e6], dtype=np.float32))
        gelu_large_neg = large_neg.gelu()
        np.testing.assert_array_almost_equal(gelu_large_neg.data, np.array([0.0], dtype=np.float32), decimal=5)
        
        # Zero
        zero_tensor = Tensor(np.array([0.0], dtype=np.float32))
        gelu_zero = zero_tensor.gelu()
        np.testing.assert_array_almost_equal(gelu_zero.data, np.array([0.0], dtype=np.float32), decimal=5)

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

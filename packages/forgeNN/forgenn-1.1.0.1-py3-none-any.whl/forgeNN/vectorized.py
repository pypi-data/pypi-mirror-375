"""
forgeNN Vectorized Neural Network Module
========================================

High-performance neural network implementations using vectorized operations.
These classes provide significant speedups over the scalar implementations
while maintaining API compatibility.

Classes:
    VectorizedLayer: Efficient layer implementation using matrix operations
    VectorizedMLP: Fast multi-layer perceptron for batch training
    VectorizedOptimizer: SGD optimizer with momentum support
"""

import numpy as np
from .tensor import Tensor
from typing import List, Optional, Union, Callable
from .functions.activation import RELU, LRELU, TANH, SIGMOID, SWISH

# Activation function mapping for unified activation system
ACTIVATION_FUNCTIONS = {
    # String-based activations
    'relu': lambda x: x.relu(),
    'sigmoid': lambda x: x.sigmoid(), 
    'tanh': lambda x: x.tanh(),
    'linear': lambda x: x,
    'lrelu': lambda x: x.leaky_relu(),
    'swish': lambda x: x.swish(),
    
    # Class-based activations (new integration)
    RELU: lambda x: x.relu(),
    LRELU: lambda x: x.leaky_relu(),
    TANH: lambda x: x.tanh(),
    SIGMOID: lambda x: x.sigmoid(),
    SWISH: lambda x: x.swish(),
    
    # Direct callable support
    'function': lambda x, fn: fn(x)
}

class VectorizedLayer:
    """
    Vectorized implementation of a fully-connected neural network layer.
    
    This layer implementation uses matrix operations to process entire batches
    of data simultaneously, providing significant performance improvements
    over the sample-by-sample approach.
    
    Mathematical Operation:
        output = activation(input @ weights + bias)
        
    Where:
        - input: (batch_size, input_features)
        - weights: (input_features, output_features)  
        - bias: (output_features,)
        - output: (batch_size, output_features)
    
    Args:
        input_size (int): Number of input features
        output_size (int): Number of output neurons
        activation (str or class or callable): Activation function. Supports:
            - Strings: 'relu', 'sigmoid', 'tanh', 'linear', 'lrelu', 'swish'
            - Classes: RELU, LRELU, TANH, SIGMOID, SWISH from forgeNN.functions.activation
            - Callable: Any function that takes a Tensor and returns a Tensor
        
    Attributes:
        weights (Tensor): Weight matrix (input_size, output_size)
        bias (Tensor): Bias vector (output_size,)
        activation: Activation function or string identifier
        
    Example:
        >>> # String-based activation names
        >>> layer1 = VectorizedLayer(784, 128, 'relu')
        >>> 
        >>> # Activation class instances
        >>> layer2 = VectorizedLayer(128, 64, LRELU)
        >>> 
        >>> # Custom function
        >>> layer3 = VectorizedLayer(64, 10, lambda x: x.sigmoid())
    """
    
    def __init__(self, input_size: int, output_size: int, 
                 activation: Union[str, type, Callable] = 'linear'):
        """Initialize layer with Xavier/Glorot weight initialization."""
        # Xavier initialization for better training dynamics
        fan_in = input_size
        fan_out = output_size
        limit = np.sqrt(6.0 / (fan_in + fan_out))
        
        self.weights = Tensor(
            np.random.uniform(-limit, limit, (input_size, output_size)),
            requires_grad=True
        )
        self.bias = Tensor(
            np.zeros(output_size),
            requires_grad=True
        )
        self.activation = activation
    
    def __call__(self, x: Tensor) -> Tensor:
        """Forward pass through the layer."""
        # Linear transformation: x @ W + b
        output = x @ self.weights + self.bias
        
        # Apply activation function using unified system
        return self._apply_activation(output)
    
    def _apply_activation(self, x: Tensor) -> Tensor:
        """Apply activation function in a unified way."""
        if callable(self.activation) and not isinstance(self.activation, type):
            # Direct callable (lambda, function) or activation class instance
            if hasattr(self.activation, 'forward'):
                # Activation class instance (e.g., RELU(), SWISH())
                return self.activation.forward(x)
            else:
                # Regular callable (lambda, function)
                return self.activation(x)
        elif self.activation in ACTIVATION_FUNCTIONS:
            # String or class-based activation
            return ACTIVATION_FUNCTIONS[self.activation](x)
        elif type(self.activation) in ACTIVATION_FUNCTIONS:
            # Instance of activation class - get the class and apply
            return ACTIVATION_FUNCTIONS[type(self.activation)](x)
        elif hasattr(x, str(self.activation)):
            # Method name on tensor (e.g., 'relu', 'sigmoid')
            return getattr(x, str(self.activation))()
        else:
            raise ValueError(f"Unknown activation: {self.activation}. "
                           f"Supported: {list(ACTIVATION_FUNCTIONS.keys())}")
    
    def parameters(self) -> List[Tensor]:
        """Return all trainable parameters."""
        return [self.weights, self.bias]

class VectorizedMLP:
    """
    Vectorized Multi-Layer Perceptron for efficient batch training.
    
    This implementation processes entire batches of data simultaneously,
    providing dramatic speedups over sample-by-sample training while
    maintaining the same mathematical operations.
    
    Key Performance Features:
    - Matrix operations instead of loops
    - Efficient memory usage with in-place operations
    - Vectorized activation functions
    - Batch gradient computation
    
    Args:
        input_size (int): Input feature dimensionality
        hidden_sizes (List[int]): List of hidden layer sizes
        output_size (int): Output dimensionality
        activations (List[str or class or callable], optional): Activation per layer. 
            
            **Recommended: Use string names for simplicity and consistency**
            - Strings: 'relu', 'sigmoid', 'tanh', 'linear', 'leaky_relu', 'swish'
            - Classes: RELU(), LRELU(), TANH(), SIGMOID(), SWISH() (advanced control)
            - Callables: Custom functions (maximum flexibility)
            - Mixed: Can combine different types, but strings are preferred
        
    Example:
        >>> # String-based activation names (recommended)
        >>> model = VectorizedMLP(784, [128, 64], 10, ['relu', 'swish', 'linear'])
        >>> 
        >>> # Activation class instances (advanced control)
        >>> model = VectorizedMLP(784, [128, 64], 10, [RELU(), SWISH(), None])
        >>> 
        >>> # Custom functions (maximum flexibility)
        >>> model = VectorizedMLP(784, [128, 64], 10, ['relu', lambda x: x.swish(beta=2.0), 'sigmoid'])
        >>> 
        >>> # Batch forward pass
        >>> batch_x = Tensor(np.random.randn(32, 784))  # 32 samples
        >>> logits = model(batch_x)  # Shape: (32, 10)
        >>> 
        >>> # Compute loss and gradients
        >>> loss = logits.cross_entropy_loss(batch_targets)
        >>> loss.backward()
    """
    
    def __init__(self, input_size: int, hidden_sizes: List[int], output_size: int,
                 activations: Optional[List[Union[str, type, Callable]]] = None):
        """Initialize vectorized MLP with specified architecture."""
        layer_sizes = [input_size] + hidden_sizes + [output_size]
        
        # Default activations: ReLU for hidden, linear for output
        if activations is None:
            activations = ['relu'] * len(hidden_sizes) + ['linear']
        
        assert len(activations) == len(hidden_sizes) + 1, \
            f"Need {len(hidden_sizes) + 1} activations, got {len(activations)}"
        
        # Create layers
        self.layers = []
        for i in range(len(layer_sizes) - 1):
            layer = VectorizedLayer(
                layer_sizes[i], 
                layer_sizes[i + 1], 
                activations[i]
            )
            self.layers.append(layer)
    
    def __call__(self, x: Tensor) -> Tensor:
        """Forward pass through the entire network."""
        output = x
        for layer in self.layers:
            output = layer(output)
        return output
    
    def parameters(self) -> List[Tensor]:
        """Return all trainable parameters from all layers."""
        params = []
        for layer in self.layers:
            params.extend(layer.parameters())
        return params
    
    def zero_grad(self):
        """Reset gradients for all parameters."""
        for param in self.parameters():
            param.zero_grad()

class VectorizedOptimizer:
    """
    Simple SGD optimizer for vectorized training.
    
    Implements stochastic gradient descent with optional momentum
    for efficient parameter updates on vectorized models.
    
    Args:
        parameters (List[Tensor]): Model parameters to optimize
        lr (float): Learning rate. Defaults to 0.01
        momentum (float): Momentum factor. Defaults to 0.0
        
    Example:
        >>> model = VectorizedMLP(784, [128], 10)
        >>> optimizer = VectorizedOptimizer(model.parameters(), lr=0.01)
        >>> 
        >>> # Training step
        >>> loss = compute_loss(model, batch_x, batch_y)
        >>> loss.backward()
        >>> optimizer.step()
        >>> optimizer.zero_grad()
    """
    
    def __init__(self, parameters: List[Tensor], lr: float = 0.01, momentum: float = 0.0):
        """Initialize optimizer with parameters and hyperparameters."""
        self.parameters = parameters
        self.lr = lr
        self.momentum = momentum
        
        # Initialize momentum buffers
        if momentum > 0:
            self.momentum_buffers = [np.zeros_like(p.data) for p in parameters]
        else:
            self.momentum_buffers = None
    
    def step(self):
        """Perform one optimization step."""
        for i, param in enumerate(self.parameters):
            if param.grad is None:
                continue
            
            if self.momentum > 0:
                # Apply momentum
                self.momentum_buffers[i] = (
                    self.momentum * self.momentum_buffers[i] + param.grad
                )
                update = self.momentum_buffers[i]
            else:
                update = param.grad
            
            # Update parameters
            param.data -= self.lr * update
    
    def zero_grad(self):
        """Reset gradients for all parameters."""
        for param in self.parameters:
            param.zero_grad()

def cross_entropy_loss(logits: Tensor, targets: np.ndarray) -> Tensor:
    """
    Compute cross-entropy loss for classification with numerical stability.
    
    Args:
        logits (Tensor): Raw model outputs (batch_size, num_classes)
        targets (np.ndarray): Class indices (batch_size,)
        
    Returns:
        Tensor: Scalar loss value
    """
    batch_size = logits.data.shape[0]
    
    # Numerical stability: subtract max before softmax
    max_logits = logits.max(axis=1, keepdims=True)
    shifted_logits = logits - max_logits
    
    # Compute log-softmax
    exp_logits = shifted_logits.exp()
    sum_exp = exp_logits.sum(axis=1, keepdims=True)
    log_sum_exp = sum_exp.log()
    log_probs = shifted_logits - log_sum_exp
    
    # Select probabilities for correct classes and compute loss directly
    batch_indices = np.arange(batch_size)
    selected_log_probs_data = log_probs.data[batch_indices, targets]
    loss_data = -np.mean(selected_log_probs_data)
    
    # Create loss tensor with proper computation graph
    loss = Tensor(loss_data, requires_grad=logits.requires_grad,
                  _children=(logits,), _op='cross_entropy')
    
    # Proper backward pass that connects to the computation graph
    if logits.requires_grad:
        def _backward():
            # Softmax gradient
            probs = (shifted_logits - log_sum_exp).exp().data
            grad = probs.copy()
            grad[batch_indices, targets] -= 1
            grad /= batch_size
            logits.grad += grad * loss.grad
        
        loss._backward = _backward
    
    return loss

def accuracy(logits: Tensor, targets: np.ndarray) -> float:
    """
    Compute classification accuracy.
    
    Args:
        logits (Tensor): Model predictions (batch_size, num_classes)
        targets (np.ndarray): True class indices (batch_size,)
        
    Returns:
        float: Accuracy as fraction between 0 and 1
    """
    predictions = np.argmax(logits.data, axis=1)
    return np.mean(predictions == targets)

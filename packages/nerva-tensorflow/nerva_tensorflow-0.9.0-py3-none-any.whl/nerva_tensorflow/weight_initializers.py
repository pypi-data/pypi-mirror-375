# Copyright 2023 Wieger Wesselink.
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE or http://www.boost.org/LICENSE_1_0.txt)

"""Weight and bias initialization helpers for linear layers."""

import math
import tensorflow as tf
from nerva_tensorflow.matrix_operations import Matrix
from nerva_tensorflow.utilities import parse_function_call


def set_bias_zero(b: Matrix):
    """Set all bias values to zero."""
    b.assign(tf.zeros_like(b))


def set_bias_uniform(b: Matrix, a: float = 0.0, b_: float = 1.0):
    """Uniform initialization within [a, b)."""
    b.assign(tf.random.uniform(b.shape, minval=a, maxval=b_, dtype=b.dtype))


def set_bias_normal(b: Matrix, mean: float = 0.0, std: float = 1.0):
    """Normal (Gaussian) initialization with given mean and std."""
    b.assign(tf.random.normal(b.shape, mean=mean, stddev=std, dtype=b.dtype))


def set_weights_uniform(W: Matrix, a: float = 0.0, b: float = 1.0):
    """Uniform initialization within [a, b)."""
    W.assign(tf.random.uniform(W.shape, minval=a, maxval=b, dtype=W.dtype))


def set_weights_normal(W: Matrix, mean: float = 0.0, std: float = 1.0):
    """Normal (Gaussian) initialization with given mean and std."""
    W.assign(tf.random.normal(W.shape, mean=mean, stddev=std, dtype=W.dtype))


def set_weights_xavier_uniform(W: Matrix):
    """Xavier / Glorot uniform initialization."""
    K, D = W.shape
    limit = math.sqrt(6.0 / (D + K))
    W.assign(tf.random.uniform(W.shape, minval=-limit, maxval=limit, dtype=W.dtype))


def set_weights_xavier_normal(W: Matrix):
    """Xavier / Glorot normal initialization."""
    K, D = W.shape
    std = math.sqrt(2.0 / (D + K))
    W.assign(tf.random.normal(W.shape, mean=0.0, stddev=std, dtype=W.dtype))


def set_weights_he_normal(W: Matrix):
    """He / Kaiming normal initialization (for ReLU)."""
    K, D = W.shape
    std = math.sqrt(2.0 / D)
    W.assign(tf.random.normal(W.shape, mean=0.0, stddev=std, dtype=W.dtype))


def set_weights_he_uniform(W: Matrix):
    """He / Kaiming uniform initialization (for ReLU)."""
    K, D = W.shape
    limit = math.sqrt(6.0 / D)
    W.assign(tf.random.uniform(W.shape, minval=-limit, maxval=limit, dtype=W.dtype))


def set_weights_zero(W: Matrix):
    """Initialize weights to zero."""
    W.assign(tf.zeros_like(W))


def set_layer_weights(layer, text: str):
    """Initialize a layer's parameters according to a named scheme."""
    func = parse_function_call(text)
    if func.name == 'Uniform':
        a = func.as_scalar('a', 0)
        b = func.as_scalar('b', 1)
        set_weights_uniform(layer.W, a, b)
        set_bias_zero(layer.b)
    elif func.name == 'Normal':
        a = func.as_scalar('a', 0)
        b = func.as_scalar('b', 1)
        set_weights_normal(layer.W, a, b)
        set_bias_zero(layer.b)
    elif func.name == 'XavierUniform':
        set_weights_xavier_uniform(layer.W)
        set_bias_zero(layer.b)
    elif func.name == 'XavierNormal':
        set_weights_xavier_normal(layer.W)
        set_bias_zero(layer.b)
    elif func.name == 'HeUniform':
        set_weights_he_uniform(layer.W)
        set_bias_zero(layer.b)
    elif func.name == 'HeNormal':
        set_weights_he_normal(layer.W)
        set_bias_zero(layer.b)
    elif func.name == 'Zero':
        set_weights_zero(layer.W)
        set_bias_zero(layer.b)
    else:
        raise RuntimeError(f'Could not parse weight initializer "{text}"')

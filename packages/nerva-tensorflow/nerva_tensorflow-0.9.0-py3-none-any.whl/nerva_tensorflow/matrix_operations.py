# Copyright 2023 Wieger Wesselink.
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE or http://www.boost.org/LICENSE_1_0.txt)

"""Matrix operations built on top of TensorFlow to support the math in the library.

The functions here intentionally mirror the names in the accompanying docs.
They operate on 1D/2D tensors and keep broadcasting explicit for clarity.
"""

import tensorflow as tf

Matrix = tf.Tensor


# A constant used by inv_sqrt to avoid division by zero
epsilon = 1e-7


def is_vector(x: Matrix) -> bool:
    """Check if x is a 1D tensor."""
    return len(x.shape) == 1


def is_column_vector(x: Matrix) -> bool:
    """Check if x can be treated as a column vector."""
    return is_vector(x) or x.shape[1] == 1


def is_row_vector(x: Matrix) -> bool:
    """Check if x can be treated as a row vector."""
    return is_vector(x) or x.shape[0] == 1


def vector_size(x: Matrix) -> int:
    """Get size along first dimension."""
    return x.shape[0]


def is_square(X: Matrix) -> bool:
    """Check if X is a square matrix."""
    m, n = X.shape
    return m == n


def dot(x, y):
    """Dot product of vectors x and y."""
    return tf.tensordot(tf.squeeze(x), tf.squeeze(y), axes=1)


def zeros(m: int, n=None, dtype=tf.float32) -> Matrix:
    """
    Returns an mxn matrix with all elements equal to 0.
    """
    return tf.zeros([m, n], dtype=dtype) if n else tf.zeros([m], dtype=dtype)


def ones(m: int, n=None, dtype=tf.float32) -> Matrix:
    """
    Returns an mxn matrix with all elements equal to 1.
    """
    return tf.ones([m, n], dtype=dtype) if n else tf.ones([m], dtype=dtype)


def identity(n: int, dtype=tf.float32) -> Matrix:
    """
    Returns the nxn identity matrix.
    """
    return tf.eye(n, dtype=dtype)


def product(X: Matrix, Y: Matrix) -> Matrix:
    """Matrix multiplication X @ Y."""
    return X @ Y


def hadamard(X: Matrix, Y: Matrix) -> Matrix:
    """Element-wise product X ⊙ Y."""
    return X * Y


def diag(X: Matrix) -> Matrix:
    """Extract diagonal of X as a vector."""
    return tf.linalg.diag_part(X)


def Diag(x: Matrix) -> Matrix:
    """Create diagonal matrix with x as diagonal."""
    return tf.linalg.diag(tf.reshape(x,[-1]))


def elements_sum(X: Matrix):
    """
    Returns the sum of the elements of X.
    """
    return tf.reduce_sum(X)


def column_repeat(x: Matrix, n: int) -> Matrix:
    """Repeat column vector x horizontally n times."""
    assert is_column_vector(x)
    if len(tf.shape(x)) == 1:
        x = tf.expand_dims(x, axis=1)  # Add a dimension to make it (m, 1)
    return tf.tile(x, [1, n])


def row_repeat(x: Matrix, m: int) -> Matrix:
    """Repeat row vector x vertically m times."""
    assert is_row_vector(x)
    if len(tf.shape(x)) == 1:
        x = tf.expand_dims(x, axis=0)  # Add a dimension to make it (1, n)
    return tf.tile(x, [m, 1])


def columns_sum(X: Matrix) -> Matrix:
    """Sum over columns (returns row vector)."""
    return tf.reduce_sum(X, axis=0)


def rows_sum(X: Matrix) -> Matrix:
    """Sum over rows (returns column vector)."""
    return tf.reduce_sum(X, axis=1)


def columns_max(X: Matrix) -> Matrix:
    """
    Returns a column vector with the maximum values of each row in X.
    """
    return tf.reduce_max(X, axis=0)


def rows_max(X: Matrix) -> Matrix:
    """
    Returns a row vector with the maximum values of each column in X.
    """
    return tf.reduce_max(X, axis=1)


def columns_mean(X: Matrix) -> Matrix:
    """
    Returns a column vector with the mean values of each row in X.
    """
    return tf.reduce_mean(X, axis=0)


def rows_mean(X: Matrix) -> Matrix:
    """
    Returns a row vector with the mean values of each column in X.
    """
    return tf.reduce_mean(X, axis=1)


def apply(f, X: Matrix) -> Matrix:
    """Element-wise application of function f to X."""
    return f(X)


def exp(X: Matrix) -> Matrix:
    """Element-wise exponential exp(X)."""
    return tf.exp(X)


def log(X: Matrix) -> Matrix:
    """Element-wise natural logarithm log(X)."""
    return tf.math.log(X)


def reciprocal(X: Matrix) -> Matrix:
    """Element-wise reciprocal 1/X."""
    return tf.math.reciprocal(X)


def square(X: Matrix) -> Matrix:
    """Element-wise square X²."""
    return tf.math.square(X)


def sqrt(X: Matrix) -> Matrix:
    """Element-wise square root √X."""
    return tf.math.sqrt(X)


def inv_sqrt(X: Matrix) -> Matrix:
    """Element-wise inverse square root X^(-1/2) with epsilon for stability."""
    return 1 / tf.sqrt(X + epsilon)  # The epsilon is needed for numerical stability


def log_sigmoid(X: Matrix) -> Matrix:
    """Element-wise log(sigmoid(X)) computed stably."""
    return -tf.nn.softplus(-X)

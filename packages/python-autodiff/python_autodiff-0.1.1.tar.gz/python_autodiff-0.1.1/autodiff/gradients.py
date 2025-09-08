import numpy as np 
from autodiff.Tensor import Tensor


def absolute_grad(a, dout):
	return np.multiply(dout, (a / np.abs(a)))

def add_grad(a, b, dout):
	return dout

def arccos_grad(a, dout):
	return np.multiply(dout, -(1 / (np.sqrt(1 - (a ** 2)))))

def arccosh_grad(a, dout):	
	return np.multiply(dout, (1 / (np.sqrt((a ** 2) - 1))))

def arcsin_grad(a, dout):
	return np.multiply(dout, (1 / (np.sqrt(1 - (a ** 2)))))

def arcsinh_grad(a, dout):
	return np.multiply(dout, (1 / (np.sqrt((a ** 2) + 1))))

def arctan_grad(a, dout):
	return np.multiply(dout, (1 / ((a ** 2) + 1)))

def arctanh_grad(a, dout):
	return np.multiply(dout, (1 / (1 - (a ** 2))))

def cbrt_grad(a, dout):
	return np.multiply(dout, (1 / ((3 * a) ** (2 / 3))))

def cos_grad(a, dout):
	return np.multiply(dout, -np.sin(a))

def cosh_grad(a, dout):
	return np.multiply(dout, np.sinh(a))

def divide_grad_left(a, b, dout):
	return np.divide(dout, b)

def divide_grad_right(a, b, dout):
	return -np.multiply(dout, (a / (b ** 2)))

def exp2_grad(a, dout):
	return np.multiply(dout, (np.log(2) * (2 ** a)))

def exp_grad(a, dout):
	return np.multiply(dout, np.exp(a))

def log10_grad(a, dout):
	return np.multiply(dout, (1 / (np.log(10) * a)))

def log1p_grad(a, dout):
	return np.multiply(dout, (1 / (a + 1)))

def log2_grad(a, dout):
	return np.multiply(dout, (1 / np.log(2) * a))

def log_grad(a, dout):
	return np.multiply(dout, (1 / a))

def matmul_grad_left(a, b, dout):
	return np.matmul(dout, b.T)

def matmul_grad_right(a, b, dout):
	return np.matmul(a.T, dout)

def multiply_grad_left(a, b, dout):
	return np.multiply(dout, b)

def multiply_grad_right(a, b, dout):
	return np.multiply(dout, a)

def negative_grad(a, dout):
	return np.negative(dout)

def power_grad_left(a, b, dout):
	return np.multiply(dout, (b * (a ** (b - 1))))

def power_grad_right(a, b, dout):
	return np.nan_to_num(np.multiply(dout, (a ** b) * (np.log(np.abs(a)))), nan=0, neginf=0, posinf=0)

def reciprocal_grad(a, dout):
	return np.multiply(dout, -np.reciprocal(a ** 2))

def sin_grad(a, dout):
	return np.multiply(dout, np.cos(a))

def sinh_grad(a, dout):
	return np.multiply(dout, np.cosh(a))

def sqrt_grad(a, dout):
	return np.multiply(dout, 1 / (2 * np.sqrt(a)))

def subtract_grad_left(a, b, dout):
	return dout

def subtract_grad_right(a, b, dout):
	return -dout

def tan_grad(a, dout): 
	return np.multiply(dout, 1 + (np.tan(a) ** 2))

def tanh_grad(a, dout):
	return np.multiply(dout, 1 - (np.tanh(a) ** 2))


def transpose_grad(a, dout, **kwargs): return dout.T

def nan_to_num(x, copy=True, nan=0, posinf=None, neginf=None):
	return Tensor(np.nan_to_num(x._i, copy, nan, posinf, neginf), dtype=x.dtype, source=x._source)

def sum_grad(a, dout, **kwargs):
	return np.ones(shape=a.shape) * dout


GRADS = {
	np.abs.__name__: [absolute_grad],
	np.absolute.__name__: [absolute_grad],
	np.add.__name__: [add_grad, add_grad],
	np.arccos.__name__: [arccos_grad],
	np.arccosh.__name__: [arccosh_grad],
	np.arcsin.__name__: [arcsin_grad],
	np.arcsinh.__name__: [arcsinh_grad],
	np.arctan.__name__: [arctan_grad],
	np.arctanh.__name__: [arctanh_grad],
	np.cbrt.__name__: [cbrt_grad],
	np.cos.__name__: [cos_grad],
	np.cosh.__name__: [cosh_grad],
	np.divide.__name__: [divide_grad_left, divide_grad_right],
	np.exp2.__name__: [exp2_grad],
	np.exp.__name__: [exp_grad],
	np.log10.__name__: [log10_grad],
	np.log1p.__name__: [log1p_grad],
	np.log2.__name__: [log2_grad],
	np.log.__name__: [log_grad],
	np.matmul.__name__: [matmul_grad_left, matmul_grad_right],
	np.multiply.__name__: [multiply_grad_left, multiply_grad_right],
	np.negative.__name__: [negative_grad],
	np.power.__name__: [power_grad_left, power_grad_right],
	np.reciprocal.__name__: [reciprocal_grad],
	np.sin.__name__: [sin_grad],
	np.sinh.__name__: [sinh_grad],
	np.sum.__name__: [sum_grad],
	np.sqrt.__name__: [sqrt_grad],
	np.subtract.__name__: [subtract_grad_left, subtract_grad_right],
	np.tan.__name__: [tan_grad],
	np.tanh.__name__: [tanh_grad],
	np.transpose.__name__: [transpose_grad]
}

import numpy as np
from numbers import Number
from autodiff.nodes import Operator, Var, Const


def nan_to_num(x, **kwargs):
	return Tensor(np.nan_to_num(x._i, **kwargs), dtype=x.dtype, source=x._source)

def transpose(a, **kwargs):
	val = np.transpose(a._i, **kwargs)
	op = Operator([a._source], value=val, name=None, optype=np.transpose.__name__)
	return Tensor(val, dtype=a.dtype, source=op)

def sum(a, **kwargs):
	val = np.sum(a._i, **kwargs)
	op = Operator([a._source], value=val, name=None, optype=np.sum.__name__)
	return Tensor(val, dtype=a.dtype, source=op)


HANDLED_FUNCTIONS = {
	np.nan_to_num: nan_to_num,
	np.transpose: transpose,
	np.sum: sum,
}


class Tensor(np.lib.mixins.NDArrayOperatorsMixin):
	def __init__(self, _i, dtype="float32", constant=False, *args, **kwargs):
		"""
		The Tensor object is a custom numpy container which produces a computation
		tree whenever numpy ufuncs are performed on it.

		Parameters 
		----------
		_i: `np.ndarray`, `list`
			The value of the array.
		dtype: `str` 
			The data type of the tensor.
		constant: `bool`
			Setting this as true will treat this Tensor as a constant. Its gradient
			will be zero. By default it is set to *True* which will mean that the
			tensor will be treated as a variable.
		"""
		self._i = np.array(_i).astype(dtype)
		self.shape = self._i.shape

		if constant:
			self._source = kwargs.get("source") or Const(self._i, kwargs.get("name"))
		else: 
			self._source = kwargs.get("source") or Var(self._i, kwargs.get("name"))

	@property
	def dtype(self):
		"""
		Returns the data type of the tensor
		"""
		return self._i.dtype

	@property
	def T(self):
		"""
		Returns the transposed version of the tensor.
		"""
		return np.transpose(self)

	def __repr__(self):
		return f"<Tensor value={self._i} dtype={self.dtype}>"
	
	def __getitem__(self, key):
		return self.__class__(self._i[key], dtype=self.dtype, source=self._source)
	def __setitem__(self, key, value):
		self._i[key] = value

	def __iter__(self):
		self._idx = 0
		return self
	
	def __next__(self):
		if self._idx < len(self._i):
			x = self._i[self._idx]
			self._idx += 1
			return self.__class__(x, dtype=self.dtype, source=Var(x, name=self._source.name))
		raise StopIteration
	
	def __array__(self, dtype=None, copy=None):
		if copy is False:
			raise ValueError(
				"`copy=False` isn't supported. A copy is always created."
			)
		return np.array(self._i).astype(dtype)
	
	def __array_ufunc__(self, ufunc, method, *args, **kwargs):
		if method == '__call__':
			scalars, sources = self.__set_source_scalar(args)
			val = ufunc(*scalars, **kwargs)
			op = Operator(sources, value=val, name=None, optype=ufunc.__name__)
			return self.__class__(val, dtype=self.dtype, source=op)
		else:
			return NotImplemented
		
	def __array_function__(self, func, types, args, kwargs):
		if func not in HANDLED_FUNCTIONS:
			return NotImplemented

		if not all(issubclass(t, self.__class__) for t in types):
			return NotImplemented
			
		return HANDLED_FUNCTIONS[func](*args, **kwargs)

	def __set_source_scalar(self, inps):
		scalars = []
		sources = []

		for inp in inps:
			val = inp
			
			if issubclass(type(inp), Number) or issubclass(type(inp), np.ndarray) or isinstance(inp, list):
				try: val = self.__class__(inp, source=Const(inp))
				except:
					raise ValueError(f"Cannot convert {inp} into type {self.__class__.__name__}")
			
			scalars.append(val._i)
			sources.append(val._source)

		return scalars, sources
	
	def copy(self):
		"""
		Returns a shallow copy of the array.
		
		[NOTE] Any built up computation graphs from the original array will be discarded.
		"""
		return self.__class__(self._i, dtype=self.dtype)
	
	def assign(self, a):
		"""
		Adds and assigns the result to the tensor.

		Parameters
		----------
		value: `np.ndarray` 
			Value to be assigned to the tensor
		"""
		self._i = a

	def assign_add(self, value): 
		"""
		Adds and assigns the result to the tensor.

		Parameters
		----------
		value: `np.ndarray`
			Value to be added to the current value of the tensor
		"""
		return self.assign(self._i + value)
	
	def assign_sub(self, value): 
		"""
		Subtracts and assigns the result to the tensor.

		Parameters
		----------
		value: `np.ndarray`
			Value to be subtracted from the current value of the tensor
		"""
		return self.assign(self._i - value)

	def astype(self, dtype):
		"""
		Changes the data type of the tensor.

		Parameters
		----------
		dtype: `str` 
			The data type to switch to
		"""
		self._i = self._i.astype(dtype)

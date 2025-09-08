from autodiff.nodes.Node import Node
import numpy as np


class Const(Node):
	count = 0

	def __init__(self, value, name=None):
		self.name = name or self.set_name(Const, name)
		Const.count += 1
		super().__init__(value, self.name)

	def __repr__(self):
		return f"Const name={self.name} value={self.value}"
	
	def string(self):
		return f"np.array({self.value.tolist()})" if type(self.value) == np.ndarray else f"{self.value}"
	
	@staticmethod
	def reset_count():
		Const.count = 0
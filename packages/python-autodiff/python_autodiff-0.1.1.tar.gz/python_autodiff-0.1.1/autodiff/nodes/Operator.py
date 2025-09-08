from autodiff.nodes import Node


class Operator(Node):
	count = 0

	def __init__(self, inputs, value=None, name=None, optype=None, *args, **kwargs):
		self.name = name or self.set_name(Operator, name)
		Operator.count += 1
		self.inputs = inputs
		self.inputs_strs = list(map(lambda x: x.string(), self.inputs))
		self.scalars = list(map(lambda x: x.value, self.inputs))
		self.optype = optype

		super().__init__(value, self.name)

	def __repr__(self):
		return f"<{Operator.__name__} name={self.name} type={self.optype}>"

	def string(self):
		return f"np.{self.optype}({','.join(self.inputs_strs)})"
	
	@staticmethod
	def reset_count():
		Operator.count = 0
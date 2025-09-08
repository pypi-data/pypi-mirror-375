from autodiff.nodes import Node


class Var(Node):
	count = 0

	def __init__(self, value, name=None):
		self.name = name or self.set_name(Var, name) 
		Var.count += 1
		super().__init__(value, self.name)
	
	def __repr__(self) -> str:
		return f"<Var name={self.name} value={self.value}>"
	
	def string(self):
		return self.name
	
	@staticmethod
	def reset_count():
		Var.count = 0
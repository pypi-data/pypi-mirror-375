class Node(object):
	def __init__(self, value, name):
		self.value = value
		self._gradient = 0
		self.name = name

	def set_name(self, cls, name=None): return f"{name or cls.__name__[0]}{cls.count}"

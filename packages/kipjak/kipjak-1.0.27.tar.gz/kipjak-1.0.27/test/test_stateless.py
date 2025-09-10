# test_main_args.py
import uuid
import kipjak as kj

from test_person import *

__all__ = [
	'Main',
	'Main_Start',
	'Main_int',
	'Main_list_int',
	'Main_Person',
	'Main_dict_UUID_Person',
	'Main_Stop',
]

class Main(kj.Point, kj.Stateless):
	def __init__(self, height: int=8, width: int=8, value: float=0.125):
		super().__init__()
		self.height = height
		self.width = width
		self.value = value

def Main_Start(self, message):
	self.console(height=self.height, width=self.width, value=self.value)

def Main_int(self, message):
	self.console(message=message)

def Main_list_int(self, message):
	self.console(message=message)

def Main_Person(self, message):
	self.console(message=message)

def Main_dict_UUID_Person(self, message):
	self.console(message=message)

def Main_Stop(self, message):
	table = [[self.value] * self.height] * self.width
	self.complete(table)

kj.bind(Main,
	(kj.Start, int, list[int], Person, dict[uuid.UUID, Person], kj.Stop),
	return_type=kj.VectorOf(kj.VectorOf(float)))

if __name__ == '__main__':
	kj.create(Main)

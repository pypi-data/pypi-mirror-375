# Author: Scott Woods <scott.suzuki@gmail.com>
# MIT License
#
# Copyright (c) 2025 Scott Woods
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Machines send messages and dispatch received machines to functions.

Purest async objects. Capable of sharing a thread.
"""
__docformat__ = 'restructuredtext'

import re

from .virtual_memory import *
from .message_memory import *
from .convert_signature import *
from .convert_type import *
from .virtual_runtime import *
from .point_runtime import *
from .virtual_point import *

__all__ = [
	'Stateless',
	'StateMachine',
	'DEFAULT',
]

class DEFAULT: pass

# Find the state and message embedded within a function name.
state_message = re.compile('(?P<state>[A-Z][A-Z0-9]*(_[A-Z0-9]+)*)_(?P<message>[A-Z][A-Za-z0-9]*)')

unknown = portable_to_signature(UserDefined(Unknown))

class Stateless(Machine):
	"""Base for simple machines that maintain no formal state.

	Messages are received by an assigned thread and dispatched to
	handlers according to the type of the received message.
	"""
	def __init__(self):
		Machine.__init__(self)

	def transition(self, message):
		art = self.__art__
		shift, messaging = art.value
		m, p, a = un_cast(message)
		s = portable_to_signature(p)
		f = shift.get(s, None)			# Explicit match.
		if f:
			return m, p, a, f

		if a:
			for c, f in messaging.items():
				if isinstance(m, c):		# Base-derived match.
					return m, p, a, f

		f = shift.get(unknown, None)	# Catch-all.
		return m, p, a, f

	def received(self, queue, message, return_address):
		"""Dispatch message to the appropriate handler.

		:parm queue: instance of a Queue-based async object
		:type queue: a Queue-based async class
		:parm message: the received massage
		:type message: instance of a registered class
		:parm return_address: origin of the message
		:type return_address: object address
		:rtype: none
		"""
		art = self.__art__
		m, p, a, f = self.transition(message)
		r = return_address[-1]
		if f is None:
			if art.message_trail and (not a or a.message_trail):
				t = portable_to_tag(p)
				if isinstance(m, Faulted):
					e = str(m)
					self.log(USER_TAG.RECEIVED, f'Dropped {t} from <{r:08x}>, {e}')
				else:
					self.log(USER_TAG.RECEIVED, f'Dropped {t} from <{r:08x}>')
			return

		if art.message_trail and (not a or a.message_trail):
			t = portable_to_tag(p)
			if isinstance(m, Faulted):
				e = str(m)
				self.log(USER_TAG.RECEIVED, f'Received {t} from <{r:08x}> {e}')
			else:
				self.log(USER_TAG.RECEIVED, f'Received {t} from <{r:08x}>')

		self.received_type = p
		f(self, m)

class StateMachine(Machine):
	"""Base for machines that maintain a formal state.

	Messages are received by an assigned thread and dispatched to
	handlers according to the current state and the type of the
	received message.

	Every handler must return the next state. In those cases where
	the state remains unchanged, return ``self.current_state``. Termination
	of a machine is by a call to :meth:`~.Point.complete`.

	:param initial: Start state for all instances of derived class
	:type initial: class
	"""
	def __init__(self, initial):
		Machine.__init__(self)
		self.current_state = initial

	def transition(self, state, message):
		art = self.__art__
		shift, messaging = art.value
		m, p, a = un_cast(message)
		s = portable_to_signature(p)
		shifted = shift.get(state, None)
		if shifted is None:
			raise ValueError(f'machine "{art.path}" shifted to nowhere')

		f = shifted.get(s, None)				# Explicit match.
		if f:
			return m, p, a, f

		if a:
			messaged = messaging.get(state, None)
			if messaged:
				for c, f in messaged.items():
					if isinstance(m, c):			# Base-derived match.
						return m, p, a, f

		f = shifted.get(unknown, None)			# Catch-all.
		return m, p, a, f

	def received(self, queue, message, return_address):
		"""Dispatch message to the appropriate handler.

		:parm queue: instance of a Queue-based async object
		:type queue: a Queue-based async class
		:parm message: the received massage
		:type message: instance of a registered class
		:parm return_address: origin of the message
		:type return_address: object address
		:rtype: none
		"""
		art = self.__art__
		m, p, a, f = self.transition(self.current_state, message)
		r = return_address[-1]
		if f is None:
			if art.message_trail and (not a or a.message_trail):
				t = portable_to_tag(p)
				if isinstance(message, Faulted):
					e = str(message)
					self.log(USER_TAG.RECEIVED, f'Dropped {t} from <{r:08x}>, {e}')
				else:
					self.log(USER_TAG.RECEIVED, f'Dropped {t} from <{r:08x}>')
			return

		if art.message_trail and (not a or a.message_trail):
			t = portable_to_tag(p)
			if isinstance(message, Faulted):
				e = str(message)
				self.log(USER_TAG.RECEIVED, f'Received {t} from <{r:08x}> {e}')
			else:
				self.log(USER_TAG.RECEIVED, f'Received {t} from <{r:08x}>')

		self.received_type = p
		self.current_state = f(self, m)

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

"""Engine room of the type system, the confluence of Python, Portable and
Python hints.

Type information is gathered from class/func declarations in the form of
hints. There is also an opportunity to declare type info at the point of
registration (kipjak.bind). This is all combined/unified into a single
instance of Portable, stored in the SIGNATURE_TABLE using the generated
signature as the key. THe core idea is that only one instance of any given
type (i.e. a construction of Portables) is used within the async app.
"""

import typing
import types

__all__ = [
	'convert_hint',
	'install_hint',
	'lookup_hint',
	'convert_portable',
	'install_portable',
	'lookup_portable',
	'lookup_signature',
	'install_type',
	'lookup_type',
	'install_hints',
	'def_type',
	'cast_to',
	'un_cast',
	'cast_back',
	'bool_type',
	'int_type',
	'float_type',
	'str_type',
	'bytes_type',
	'bytearray_type',
	'datetime_type',
	'timedelta_type',
	'uuid_type',
	'message_to_tag',
]

from .virtual_memory import *
from .virtual_runtime import *
from .convert_signature import *
from collections import deque
from datetime import datetime, timedelta
import uuid
from enum import Enum

# Map of signature-to-type, ensuring the single type
# instance is in use at runtime.
SIGNATURE_TABLE = {
	'boolean': Boolean(),		# Pre-loaded with the basic types.
	'integer8': Integer8(),
	'float8': Float8(),
	'byte': Byte(),
	'block': Block(),
	'character': Character(),
	'string': String(),
	'rune': Rune(),
	'unicode': Unicode(),
	'clock': ClockTime(),
	'span': TimeSpan(),
	'world': WorldTime(),
	'delta': TimeDelta(),
	'uuid': UUID(),
	'type': Type(),
	'word': Word(),
	'address': Address(),
	'target': TargetAddress(),
	'any': Any(),
}

# Direct mapping from Python hint to
# library type.
SIMPLE_TYPE = {
	bool: Boolean(),
	int: Integer8(),
	float: Float8(),
	str: Unicode(),
	bytes: String(),
	bytearray: Block(),
	datetime: WorldTime(),
	timedelta: TimeDelta(),
	uuid.UUID: UUID(),

	Boolean: Boolean(),
	Integer8: Integer8(),
	Float8: Float8(),
	Unicode: Unicode(),
	String: String(),
	Block: Block(),
	UUID: UUID(),
	WorldTime: WorldTime(),
	TimeDelta: TimeDelta(),
	ClockTime: ClockTime(),
	TimeSpan: TimeSpan(),
	Address: Address(),
	TargetAddress: TargetAddress(),
	Type: Type(),
	Word: Word(),
	Any: Any(),
}

from typing import Union, Optional, get_origin, get_args

def convert_hint(hint, then):
	"""Accept a portable, message, basic type, Python hint or None."""

	t = SIMPLE_TYPE.get(hint, None)
	if t is not None:
		return t

	try:
		if hasattr(hint, '__art__'):
			return UserDefined(hint)
		elif issubclass(hint, Enum):
			return Enumeration(hint)
	except TypeError:
		pass

	if isinstance(hint, types.GenericAlias):
		c = hint.__origin__
		a = hint.__args__
		if c == list:
			if len(a) != 1:
				raise PointConstructionError(f'expected an argument for type "{c.__name__}"')
			a0 = convert_hint(a[0], then)
			then(a0)
			return VectorOf(a0)
		elif c == dict:
			if len(a) != 2:
				raise PointConstructionError(f'expected key and value arguments for type "{c.__name__}"')
			a0 = convert_hint(a[0], then)
			a1 = convert_hint(a[1], then)
			then(a0)
			then(a1)
			return MapOf(a0, a1)
		elif c == set:
			if len(a) != 1:
				raise PointConstructionError(f'expected an argument for type "{c.__name__}"')
			a0 = convert_hint(a[0], then)
			then(a0)
			return SetOf(a0)
		elif c == deque:
			if len(a) != 1:
				raise PointConstructionError(f'expected an argument for type "{c.__name__}"')
			a0 = convert_hint(a[0], then)
			then(a0)
			return DequeOf(a0)
	elif hint == typing.Any:
		return None
	elif hint == types.NoneType:
		return None

	try:
		origin = get_origin(hint)
		if origin:
			if origin is Union:
				args = [a for a in get_args(hint)]
				return convert_hint(args[0], then)
		return None
	except (TypeError, ValueError):
		pass

	raise PointConstructionError(f'cannot convert hint "{hint}"')

def lookup(p):
	s = portable_to_signature(p)
	f = SIGNATURE_TABLE.get(s, None)
	if f is not None:
		return f

	raise PointConstructionError(f'portable "{s}" was not loaded')

def lookup_hint(t):
	"""Search the internal table for properly installed types. Return the identity type."""
	p = convert_hint(t, lookup)
	return lookup(p)

def install(p):
	s = portable_to_signature(p)
	f = SIGNATURE_TABLE.get(s, None)
	if f is None:
		SIGNATURE_TABLE[s] = p
		return p
	return f

def install_hint(t):
	"""Search the internal table for properly installed types."""
	p = convert_hint(t, install)
	return install(p)

CONVERT_PYTHON = {
	bool: Boolean(),
	int: Integer8(),
	float: Float8(),
	str: Unicode(),
	bytes: String(),
	bytearray: Block(),
	datetime: WorldTime(),
	timedelta: TimeDelta(),
	uuid.UUID: UUID(),
}

def convert_portable(p, then, bread=None):
	"""Walk the potential hierarchy of a type, patching as necessary. Return a clean Portable."""
	if bread is None:
		bread = {}

	if is_portable(p):
		if not is_container(p):
			return p	# No change.
		# Fall thru for structured processing.
	elif is_portable_class(p):
		if not is_container_class(p):
			return p()  # Promotion of simple type.
		raise ValueError(f'portable class "{p.__name__}" used in type information, instance required')
	elif hasattr(p, '__art__'):
		if issubclass(p, Enum):
			return Enumeration(p)
		return UserDefined(p)
	else:
		# Is it one of the mapped Python classes.
		try:
			e = CONVERT_PYTHON[p]
			return e
		except KeyError:
			pass
		except TypeError:   # Unhashable - list.
			pass
		raise ValueError(f'not a portable type ({p})')

	# We have an instance of structuring.
	name = p.__class__.__name__
	if isinstance(p, ArrayOf):
		p.element = convert_portable(p.element, then, bread)
		then(p.element)
	elif isinstance(p, VectorOf):
		p.element = convert_portable(p.element, then, bread)
		then(p.element)
	elif isinstance(p, SetOf):
		p.element = convert_portable(p.element, then, bread)
		then(p.element)
	elif isinstance(p, MapOf):
		p.key = convert_portable(p.key, then, bread)
		p.value = convert_portable(p.value, then, bread)
		then(p.key)
		then(p.value)
	elif isinstance(p, DequeOf):
		p.element = convert_portable(p.element, then, bread)
		then(p.element)
	elif isinstance(p, UserDefined):
		if p.element is None or not hasattr(p.element, '__art__'):
			raise ValueError(f'"{name}" is not an installed message')
	elif isinstance(p, Enumeration):
		if not issubclass(p.element, Enum):
			raise ValueError(f'"{name}" is not an enum class')
	elif isinstance(p, PointerTo):
		try:
			e = bread[id(p)]
		except KeyError:
			e = convert_portable(p.element, then, bread)
			bread[id(p)] = e
		p.element = e
		then(p.element)
	else:
		raise ValueError('unexpected container type')
	return p

def lookup_portable(t):
	"""Search the internal table for properly installed types. Return the identity type."""
	p = convert_portable(t, lookup)
	return lookup(p)

def install_portable(t):
	"""Search the internal table for properly installed types."""
	p = convert_portable(t, install)
	return install(p)

def lookup_signature(s):
	f = SIGNATURE_TABLE.get(s, None)
	return f

def install_hints(hints):
	'''Convert standard Python hints into a managed set of Portable objects. Return a 2-tuple of dict and Portable.'''
	named_type = {}
	return_type = None
	for k, v in hints.items():
		m = install_hint(v)
		if m is None:
			continue
		if k == 'return':
			return_type = m
			continue
		named_type[k] = m
	return named_type, return_type

def lookup_type(t):
	"""Search the internal table for properly installed types. Return the identity type."""
	if isinstance(t, Portable):
		return lookup_portable(t)
	return lookup_hint(t)

def install_type(t):
	"""Search the internal table for properly installed types."""
	if isinstance(t, Portable):
		return install_portable(t)
	return install_hint(t)

def def_type(hint_or_portable):
	"""
	Register an application type. Return :class:`~.Portable`.

	Register a type for use within an application. Where necessary, convert Python
	hints into :class:`~.Portable` equivalents.

	:param hint_or_portable: a type description
	:type hint_or_portable: :ref:`tip<type-reference>`
	"""
	p = install_type(hint_or_portable)
	return p

def cast_to(value, p: Portable):
	"""
	Accept Python value and type. Return a :ref:`message<kj-message>`.

	For registered messages, this is a no-op. For constructed types it's
	required for encoding/decoding to function properly.

	:param value: the application value
	:param p: portable representation of type
	"""
	if isinstance(p, UserDefined):
		return value
	return (value, p)

def un_cast(message: Any):
	"""
	Accept the results of a :func:`~.cast_to` or network receive. Returns a 3-tuple.

	Splits the :ref:`message<kj-message>` into an application value, portable
	representation and the technical details registered at runtime.

	:param message: the portable data
	"""
	if message is None:
		return None, Any(), None
	art = getattr(message, '__art__', None)
	if art:
		value = message
		p = lookup_signature(art.path)
	elif isinstance(message, tuple) and len(message) == 2 and isinstance(message[1], Portable):
		value = message[0]
		p = message[1]
	else:
		raise ValueError(f'cannot unroll {message}')
	return value, p, art

def cast_back(message: Any):
	"""
	Accept the results of a :func:`~.cast_to` or network receive. Returns a 2-tuple.

	Splits the :ref:`message<kj-message>` into an application value and a portable type.

	:param message: class instance or constructed
	"""
	if message is None:
		return None, Any()
	art = getattr(message, '__art__', None)
	if art:
		value = message
		p = lookup_signature(art.path)
	elif isinstance(message, tuple) and len(message) == 2 and isinstance(message[1], Portable):
		value = message[0]
		p = message[1]
	else:
		raise ValueError(f'cannot unroll {message}')
	return value, p

bool_type = def_type(Boolean())
int_type = def_type(Integer8())
float_type = def_type(Float8())
str_type = def_type(Unicode())
bytes_type = def_type(String())
bytearray_type = def_type(Block())
datetime_type = def_type(WorldTime())
timedelta_type = def_type(TimeDelta())
uuid_type = def_type(UUID())

def message_to_tag(message):
	if message is None:
		return '<none>'

	art = getattr(message, '__art__', None)
	if art:
		t = art.path
	elif isinstance(message, tuple) and len(message) == 2 and isinstance(message[1], Portable):
		t = portable_to_tag(message[1])
	else:
		t = '<not-an-any>'

	return t

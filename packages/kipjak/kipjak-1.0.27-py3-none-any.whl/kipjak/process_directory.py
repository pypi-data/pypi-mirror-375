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
"""The directory built in to every process. Default is inactive.

.
"""
__docformat__ = 'restructuredtext'

from enum import Enum
from collections import deque

from .general_purpose import *
from .ip_networking import *
from .command_line import *
from .point_runtime import *
from .virtual_point import *
from .object_runtime import *
from .object_directory import *

__all__ = [
	'PD',
	'publish',
	'subscribe',
	'clear_published',
	'clear_subscribed',
]

PD = Gas(directory=None)

'''
ifs = netifaces.interfaces()
for i in ifs:
	a = netifaces.ifaddresses(i)
	if netifaces.AF_INET not in a:
		continue
	print(a[netifaces.AF_INET][0]['addr'])

'''

# Managed creation of the builtin directory.
def create_directory(root):
	directory_scope = CL.directory_scope or ScopeOfDirectory.PROCESS
	connect_to_directory = CL.connect_to_directory or HostPort()
	accept_directories_at = CL.accept_directories_at or HostPort()
	PD.directory = root.create(ObjectDirectory, directory_scope=directory_scope,
		connect_to_directory=connect_to_directory,
		accept_directories_at=accept_directories_at)

def stop_directory(root):
	root.send(Stop(), PD.directory)
	root.select(Returned)

AddOn(create_directory, stop_directory)

#
def publish(self: Point, name: str, scope: ScopeOfDirectory=ScopeOfDirectory.HOST, encrypted: bool=False):
	"""
	Establish a service presence under the specified name.

	:param self: asynchronous identity
	:param name: name to be used as alias for the given object
	:param scope: scope in which the name is available
	:param encrypted: enable encryption of subscriber sessions
	"""
	p = PublishAs(name=name, scope=scope, publisher_address=self.object_address, encrypted=encrypted)
	self.send(p, PD.directory)

def subscribe(self: Point, search: str, scope: ScopeOfDirectory=ScopeOfDirectory.HOST):
	"""
	Establish a lookup for services matching the specified pattern.

	:param self: asynchronous identity
	:param search: pattern to be used for matching with services
	:param scope: scope in which to search
	"""
	p = SubscribeTo(search=search, scope=scope, subscriber_address=self.object_address)
	self.send(p, PD.directory)

def clear_published(self: Point, published: Published, note: str=None):
	"""
	Remove all trace of the previously published service.

	:param self: asynchronous identity
	:param published: message confirming a :func:`~.publish`
	:param note: short description added to logs
	"""
	p = ClearPublished(name=published.name, scope=published.scope, published_id=published.published_id, note=note)
	self.send(p, PD.directory)

def clear_subscribed(self: Point, subscribed: Subscribed, note: str=None):
	"""
	Remove all trace of the previously registered search.

	:param self: asynchronous identity
	:param published: message confirming a :func:`~.subscribe`
	:param note: short description added to logs
	"""
	s = ClearSubscribed(search=subscribed.search, scope=subscribed.scope, subscribed_id=subscribed.subscribed_id, note=note)
	self.send(s, PD.directory)

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
"""A hierarchical directory of named addresses, expressions of interest and matches.

.
"""
__docformat__ = 'restructuredtext'

import os
import sys
from datetime import datetime
import uuid
import re
from .get_local_ip import get_local_ip

from .general_purpose import *
from .command_line import *
from .ip_networking import *
from .virtual_memory import *
from .convert_memory import *
from .message_memory import *
from .convert_type import *
from .virtual_runtime import *
from .point_runtime import *
from .virtual_point import *
from .point_machine import *
from .bind_type import *
from .listen_connect import *
from .get_response import *

__all__ = [
	'scope_type',
	'DIRECTORY_PORT',
	'DIRECTORY_AT_HOST',
	'DIRECTORY_AT_LAN',
	'directory_at_lan',
	'ConnectTo',
	'AcceptAt',
	'PublishAs',
	'SubscribeTo',
	'Published',
	'Subscribed',
	'ClearPublished',
	'ClearSubscribed',
	'PublishedCleared',
	'SubscribedCleared',
	'NotPublished',
	'NotSubscribed',
	'ObjectDirectory',
	'Available',
	'Delivered',
	'Dropped',
]

#
scope_type = def_type(ScopeOfDirectory)

# Time required for request/response sequence across peer connection.
COMPLETE_A_LOOP = 3.0

# Activate/update the directory-to-directory connections. See
# also ObjectDirectory_READY_Enquiry (support for library processes).
class ConnectTo(object):
	def __init__(self, ipp: HostPort=None):
		self.ipp = ipp or HostPort()

class AcceptAt(object):
	def __init__(self, ipp: HostPort=None):
		self.ipp = ipp or HostPort()

bind(ConnectTo)
bind(AcceptAt)

# Declare publish/subscribe within the host process.
# Sent by the application objects.
class PublishAs(object):
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, publisher_address: Address=None, encrypted: bool=None):
		self.name = name
		self.scope = scope
		self.publisher_address = publisher_address
		self.encrypted = encrypted

class SubscribeTo(object):
	def __init__(self, search: str=None, scope: ScopeOfDirectory=None, subscriber_address: Address=None):
		self.search = search
		self.scope = scope
		self.subscriber_address = subscriber_address

bind(PublishAs)
bind(SubscribeTo)

# Internal record of pub/subs held within each directory in the tree.
# Also sent to subscribers/publishers as confirmation of sub/pub and
# expected as the arg to clear_published, et al.
# Propagated up the hierarchy.
class Published(object):
	"""
	Successful completion of :func:`~.publish`.

	:param name: name the service is known by
	:param scope: scope in which to search
	:param published_id: unique identity assigned to registration
	:param listening_ipp: IP and port assigned to this service
	:param home_address: address of the publishing process
	"""
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, encrypted: bool=False,
			published_id: UUID=None, listening_ipp: HostPort=None,
			home_address: Address=None):
		self.name = name
		self.scope = scope
		self.encrypted = encrypted
		self.published_id = published_id
		self.listening_ipp = listening_ipp or HostPort()
		self.home_address = home_address

class Subscribed(object):
	"""
	Successful completion of :func:`~.subscribe`.

	:param search: pattern to match with services
	:param scope: scope in which to search
	:param subscribed_id: unique identity assigned to registration
	:param home_address: address of the subscribing process
	"""
	def __init__(self, search: str=None, scope: ScopeOfDirectory=None,
			subscribed_id: UUID=None, home_address: Address=None):
		self.search = search
		self.scope = scope
		self.subscribed_id = subscribed_id
		self.home_address = home_address

bind(Published)
bind(Subscribed)

class Advisory(object):
	"""A warning to the receiving directory, that there is a collision at a higher level."""
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, published_id: UUID=None):
		self.name = name
		self.scope = scope
		self.published_id = published_id

bind(Advisory)

# Instructions and confirmations from the application to retract
# the specified pub/sub.
class ClearPublished(object):
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, published_id: UUID=None, note: str=None):
		self.name = name
		self.scope = scope
		self.published_id = published_id
		self.note = note

class ClearSubscribed(object):
	def __init__(self, search: str=None, scope: ScopeOfDirectory=None, subscribed_id: UUID=None, note: str=None):
		self.search = search
		self.scope = scope
		self.subscribed_id = subscribed_id
		self.note = note

class PublishedCleared(object):
	"""
	Successful completion of :func:`~.clear_published`.

	:param name: name the service is known by
	:param scope: scope in which to search
	:param published_id: unique identity assigned to registration
	:param note: short description appearing in logs
	"""
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, published_id: UUID=None, note: str=None):
		self.name = name
		self.scope = scope
		self.published_id = published_id
		self.note = note

class SubscribedCleared(object):
	"""
	Successful completion of :func:`~.clear_subscribed`.

	:param name: name the service is known by
	:param scope: scope in which to search
	:param subscribed_id: unique identity assigned to registration
	:param note: short description appearing in logs
	"""
	def __init__(self, search: str=None, scope: ScopeOfDirectory=None, subscribed_id: UUID=None, note: str=None):
		self.search = search
		self.scope = scope
		self.subscribed_id = subscribed_id
		self.note = note

bind(ClearPublished)
bind(ClearSubscribed)
bind(PublishedCleared)
bind(SubscribedCleared)

# When pub/sub fails.
class NotPublished(Faulted):
	"""
	Unsuccessful completion of :func:`~.publish`.

	Derived from :class:`~.Faulted`

	:param name: name the service would be known by
	:param scope: scope in which service would be available
	:param note: short description added to logs
	"""
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, note: str=None):
		self.name = name
		self.scope = scope
		self.note = note
		Faulted.__init__(self,f'cannot publish as "{name}"', note)

class NotSubscribed(Faulted):
	"""
	Unsuccessful completion of :func:`~.subscribe`.

	Derived from :class:`~.Faulted`

	:param name: pattern for matching services
	:param scope: scope in which to search
	:param note: short description added to logs
	"""
	def __init__(self, search: str=None, scope: ScopeOfDirectory=None, note: str=None):
		self.search = search
		self.scope = scope
		self.note = note
		Faulted.__init__(self,f'cannot subscribe to "{search}"', note)

bind(NotPublished, explanation=str, error_code=int, exit_status=int)
bind(NotSubscribed, explanation=str, error_code=int, exit_status=int)

# Bulk transfer of listings between directories, e.g. on
# reconnect to parent.
class PublishedDirectory(object):
	def __init__(self, published: list[Published]=None, subscribed: list[Subscribed]=None):
		self.published = published or []
		self.subscribed = subscribed or []

bind(PublishedDirectory)

# When an accepted directory is lost, all the pub/sub listings
# originating from that connection are cleared out of the hierarchy.
class ClearListings(object):
	def __init__(self, subscribers: set[UUID]=None, publishers: set[UUID]=None):
		self.subscribers = subscribers or set()
		self.publishers = publishers or set()

bind(ClearListings)

# Custom message from route to loadable library process.
class OpenLibrary(object):
	def __init__(self, published_id: UUID=None, subscribed_id: UUID=None):
		self.published_id = published_id
		self.subscribed_id = subscribed_id

bind(OpenLibrary)

# Messages from route to pub/sub home processes to inform the
# receivers of another routing option.
# Base class for all.
class SubscriberRoute(object):
	def __init__(self, route_id: UUID=None, scope: ScopeOfDirectory=None,
			subscribed_id: UUID=None, published_id: UUID=None,
			name: str=None):
		self.route_id = route_id
		self.scope = scope
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.name = name

# Derived class for RouteOverConnect.
class RouteOverLoop(SubscriberRoute):
	def __init__(self, route_id: UUID=None, scope: ScopeOfDirectory=None, encrypted: bool=False,
			subscribed_id: UUID=None, published_id: UUID=None,
			ipp: HostPort=None, name: str=None):
		# Base members.
		self.route_id = route_id
		self.scope = scope
		self.encrypted = encrypted
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.name = name
		# Specialized members.
		self.ipp = ipp

# Derived class for RouteInProcess.
class RouteToAddress(SubscriberRoute):
	def __init__(self, route_id: UUID=None, scope: ScopeOfDirectory=None,
			subscribed_id: UUID=None, published_id: UUID=None,
			subscriber_address: Address=None, publisher_address: Address=None,
			name: str=None, opened_at: datetime=None):
		# Base members.
		self.route_id = route_id
		self.scope = scope
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.subscriber_address = subscriber_address
		self.publisher_address = publisher_address
		self.name = name
		self.opened_at = opened_at

# Messages from route to pub/sub home processes, to delete the given route.
class ClearSubscriberRoute(object):
	def __init__(self, subscribed_id: UUID=None, name: str=None, route_id: UUID=None):
		self.subscribed_id = subscribed_id
		self.name = name
		self.route_id = route_id

class ClearPublisherRoute(object):
	def __init__(self, published_id: UUID=None, name: str=None, route_id: UUID=None):
		self.published_id = published_id
		self.name = name
		self.route_id = route_id

bind(SubscriberRoute)
bind(RouteOverLoop)
bind(RouteToAddress)
bind(ClearSubscriberRoute)
bind(ClearPublisherRoute)

# From directory to connector. Pass the baton for establishing
# communications.
class RequestLoop(object):
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, route_id: UUID=None,
			subscribed_id: UUID=None, published_id: UUID=None,
			subscriber_address: Address=None):
		self.name = name
		self.scope = scope
		self.route_id = route_id
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.subscriber_address = subscriber_address

# From ConnectToPeer to ListenForPeer. Establish
# a virtual circuit.
class OpenLoop(object):
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, route_id: UUID=None, subscribed_id: UUID=None, published_id: UUID=None, subscriber_address: Address=None):
		self.name = name
		self.scope = scope
		self.route_id = route_id
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.subscriber_address = subscriber_address

# Response to OpenLoop.
class LoopOpened(object):
	def __init__(self, publisher_address: Address=None):
		self.publisher_address = publisher_address

# From ConnectToPeer to ListenForPeer. Clear the
# virtual cicuit.
class CloseLoop(object):
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, route_id: UUID=None, subscribed_id: UUID=None, published_id: UUID=None, subscriber_address: Address=None):
		self.name = name
		self.scope = scope
		self.route_id = route_id
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.subscriber_address = subscriber_address

# Response to CloseLoop.
class LoopClosed(object):
	def __init__(self, publisher_address: Address=None):
		self.publisher_address = publisher_address

# From directory to connector. Subscriber is rerouting,
# e.g. upgrading.
class DropLoop(object):
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, route_id: UUID=None, subscribed_id: UUID=None, published_id: UUID=None, subscriber_address: Address=None):
		self.name = name
		self.scope = scope
		self.route_id = route_id
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.subscriber_address = subscriber_address

# Response to DropLoop and also when remote object
# clears a pub/sub.
class LoopDropped(object):
	def __init__(self, subscribed_id: UUID=None, name: str=None, route_id: UUID=None):
		self.subscribed_id = subscribed_id
		self.name = name
		self.route_id = route_id

bind(RequestLoop)
bind(OpenLoop)
bind(LoopOpened)
bind(CloseLoop)
bind(LoopClosed)
bind(DropLoop)
bind(LoopDropped)

# Notifications from directory to pub/sub regarding presence of virtual circuit.
# A publisher is available at self.return_address.
class Available(object):
	"""Session notification, peer transport to service established.

	:param name: name of the matched service
	:param scope: scope at which name was matched
	:param route_id: unique identity assigned to match
	:param subscribed_id: unique identity assigned to subscription
	:param published_id: unique identity assigned to publication
	:param publisher_address: address of the publishing process
	:param opened_at: moment the match occurred
	"""
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, route_id: UUID=None,
			subscribed_id: UUID=None, published_id: UUID=None,
			publisher_address: Address=None, opened_at: datetime=None):
		self.name = name
		self.scope = scope
		self.route_id = route_id
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.publisher_address = publisher_address
		self.opened_at = opened_at

# A subscriber is at self.return_address.
class Delivered(object):
	"""Session notification, peer transport to subscriber established.

	:param name: name of the matched service
	:param scope: scope at which name was matched
	:param route_id: unique identity assigned to match
	:param subscribed_id: unique identity assigned to subscription
	:param published_id: unique identity assigned to publication
	:param subscriber_address: address of the subscribing process
	:param opened_at: moment the match occurred
	"""
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, route_id: UUID=None,
			subscribed_id: UUID=None, published_id: UUID=None,
			subscriber_address: Address=None, opened_at: datetime=None):
		self.name = name
		self.scope = scope
		self.route_id = route_id
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.subscriber_address = subscriber_address
		self.opened_at = opened_at

# An existing circuit has been cleared.
class Dropped(object):
	"""Session notification, peer transport to published/subscriber lost.

	:param name: name of the matched service
	:param scope: scope at which name was matched
	:param route_id: unique identity assigned to match
	:param subscribed_id: unique identity assigned to subscription
	:param published_id: unique identity assigned to publication
	:param remote_address: address of the subscriber/publisher
	:param opened_at: moment the match occurred
	"""
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, route_id: UUID=None,
			subscribed_id: UUID=None, published_id: UUID=None,
			remote_address: Address=None, opened_at: datetime=None):
		self.name = name
		self.scope = scope
		self.route_id = route_id
		self.subscribed_id = subscribed_id
		self.published_id = published_id
		self.remote_address = remote_address
		self.opened_at = opened_at

bind(Available)
bind(Delivered)
bind(Dropped)

#
#
class OpenDirectory(object):
	def __init__(self, scope: ScopeOfDirectory=None):
		self.scope = scope or ScopeOfDirectory.HOST

class ListDirectory(object): pass
class GetDirectory(object): pass
class DirectoryOpened(object): pass

class DirectoryRoute(object):
	"""A [scope][name] route from subscribed id to published id.

	.
	"""
	def __init__(self, name: str=None,
			subscribed_id: UUID=None, published_id: UUID=None):
		self.name = name
		self.subscribed_id = subscribed_id
		self.published_id = published_id

class PeerSession(object):
	def __init__(self, name: str=None, route: Any=None, status: Any=None):
		self.name = name
		self.route = route
		self.status = status

class DirectoryPeer(object):
	def __init__(self, subscribed_id: UUID=None, search: str=None, session: list[PeerSession]=None):
		self.subscribed_id = subscribed_id
		self.search = search
		self.session = session or []

class DirectoryListing(object):
	"""Network administration, contents.

	.
	"""
	def __init__(self, unique_id: UUID=None, executable: str=None,
			directory_address: Address=None, scope: ScopeOfDirectory=None,
			primary_ip: str=None,
			connect_to_directory: HostPort=None, accept_directories_at: HostPort=None,
			published: list[Published]=None, subscribed: list[Subscribed]=None,
			routed: list[DirectoryRoute]=None,
			peer: dict[UUID, DirectoryPeer]=None,
			sub_directory: dict[HostPort, Address]=None):
		self.unique_id = unique_id
		self.executable = executable
		self.directory_address = directory_address
		self.scope = scope
		self.primary_ip = primary_ip or '(not detected)'
		self.connect_to_directory = connect_to_directory
		self.accept_directories_at = accept_directories_at
		self.published = published or []
		self.subscribed = subscribed or []
		self.routed = routed or []
		self.peer = peer or {}
		self.sub_directory = sub_directory or {}

bind(OpenDirectory)
bind(DirectoryOpened)
bind(ListDirectory)
bind(GetDirectory)
bind(DirectoryRoute)
bind(PeerSession)
bind(DirectoryPeer)
bind(DirectoryListing)

#
class INITIAL: pass
class PENDING: pass
class READY: pass
class OPENING: pass

DIRECTORY_PORT			= 54195
DIRECTORY_AT_EPHEMERAL	= HostPort('127.0.0.1', 0)
DIRECTORY_AT_HOST		= HostPort('127.0.0.1', DIRECTORY_PORT)
DIRECTORY_AT_LAN		= HostPort('192.168.0.195', DIRECTORY_PORT)

# A managed listen. One required for every publish beyond
# the process scope.
class ListeningForPeer(Point, StateMachine):
	def __init__(self, name: str=None, scope: ScopeOfDirectory=None, address: Address=None, encrypted: bool=False):
		Point.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.name = name
		self.scope = scope
		self.address = address
		self.encrypted = encrypted
		self.listening = None
		self.accepted = {}

def ListeningForPeer_INITIAL_Start(self, message):
	# Tune the listen address according to the scope of the publish. Host
	# portion is overruled where the publish is listed in higher scopes,
	# e.g. LAN. All use ephemeral ports.
	if self.scope.value < ScopeOfDirectory.HOST.value:
		ipp = HostPort('0.0.0.0', 0)

	elif self.scope.value < ScopeOfDirectory.PROCESS.value:
		ipp = HostPort('127.0.0.1', 0)

	else:
		self.complete(Faulted(f'Cannot peer for scope [{self.scope}]'))

	listen(self, ipp, encrypted=self.encrypted)
	return PENDING

def ListeningForPeer_PENDING_Listening(self, message):
	self.listening = message
	self.send(message.listening_ipp, self.parent_address)
	return READY

def ListeningForPeer_PENDING_NotListening(self, message):
	self.complete(message)

def ListeningForPeer_READY_Accepted(self, message):
	# Tracking of open loops.
	self.accepted[self.return_address[-1]] = {}
	return READY

def ListeningForPeer_READY_Closed(self, message):
	p = self.accepted.pop(self.return_address[-1], None)
	# Going down. Send out the end-of-session notifications
	# to those that received the start-of-session.
	if p is not None:
		for k, v in p.items():
			a, opened_at = v
			d = Dropped(name=a.name, scope=a.scope, route_id=a.route_id,
				subscribed_id=a.subscribed_id, published_id=a.published_id,
				remote_address=k, opened_at=opened_at)
			self.forward(d, self.address, k)
	return READY

def ListeningForPeer_READY_OpenLoop(self, message):
	opened_at = world_now()
	self.accepted[self.return_address[-1]][message.subscriber_address] = [message, opened_at]

	self.reply(LoopOpened(publisher_address=self.address))

	d = Delivered(name=message.name, scope=message.scope, route_id=message.route_id,
		subscribed_id=message.subscribed_id, published_id=message.published_id,
		subscriber_address=message.subscriber_address, opened_at=opened_at)

	self.forward(d, self.address, message.subscriber_address)
	return READY

def ListeningForPeer_READY_CloseLoop(self, message):
	p, opened_at = self.accepted[self.return_address[-1]].pop(message.subscriber_address, None)

	self.reply(LoopClosed(publisher_address=self.address))

	d = Dropped(name=message.name, scope=message.scope, route_id=message.route_id,
		subscribed_id=message.subscribed_id, published_id=message.published_id,
		remote_address=message.subscriber_address, opened_at=opened_at)

	self.forward(d, self.address, message.subscriber_address)
	return READY

def ListeningForPeer_READY_Stop(self, message):
	self.complete(Aborted())

def ListeningForPeer_READY_NotListening(self, message):
	self.complete(Aborted())

LISTENING_FOR_PEER_DISPATCH = {
	INITIAL: (
		(Start,),
		()
	),
	PENDING: (
		(Listening, NotListening),
		()
	),
	READY: (
		(Accepted, Closed,
		OpenLoop, CloseLoop,
		Stop,
		NotListening),
		()
	),
}

bind(ListeningForPeer, LISTENING_FOR_PEER_DISPATCH)

# A managed connect. One required for every outbound route
# on a unique ip+port.
class ConnectToPeer(Point, StateMachine):
	def __init__(self, ipp: HostPort=None, encrypted: bool=False):
		Point.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.ipp = ipp
		self.encrypted = encrypted
		self.request = []		# All the RequestLoops.
		self.available = []		# Requests answered by LoopOpened.

	def delete_request(self, route_id):
		d = None
		for i, ra in enumerate(self.request):
			r, a = ra
			if r.route_id == route_id:
				d = i
				break
		if d is not None:
			r = self.request.pop(d)
			return r
		return None

	def delete_available(self, route_id):
		d = None
		for i, a in enumerate(self.available):
			if a[0].route_id == route_id:
				d = i
				break
		if d is not None:
			a = self.available.pop(d)
			return a
		return None

	def not_available(self):
		for a, s, p in self.available:
			d = LoopDropped(subscribed_id=a.subscribed_id, name=a.name, route_id=a.route_id)
			self.send(d, self.parent_address)

			d = Dropped(name=a.name, scope=a.scope, route_id=a.route_id,
				subscribed_id=a.subscribed_id, published_id=a.published_id,
				remote_address=a.publisher_address, opened_at=a.opened_at)

			self.forward(d, s, p)

def ConnectToPeer_INITIAL_Start(self, message):
	localhost = self.ipp.host.startswith('127.')
	keep_alive = not localhost
	connect(self, self.ipp, keep_alive=keep_alive, encrypted=self.encrypted)
	return PENDING

def ConnectToPeer_PENDING_Connected(self, message):
	self.connected = message

	def opened(self, loop, args):
		request = args.request
		client_address = args.client_address
		if not isinstance(loop, LoopOpened):
			self.warning(f'Closing peer connection (unexpected looping response {loop})')
			self.send(Close(), self.connected.proxy_address)
			self.send(loop, client_address)
			return

		a = Available(name=request.name, scope=request.scope, route_id=request.route_id,
			published_id=request.published_id, subscribed_id=request.subscribed_id,
			publisher_address=loop.publisher_address, opened_at=world_now())

		self.forward(a, request.subscriber_address, loop.publisher_address)
		self.available.append((a, request.subscriber_address, loop.publisher_address))
		self.send(self.connected, client_address)

	# Send OpenLoop on behalf of each client.
	for ra in self.request:
		r, a = ra
		address = r.subscriber_address
		open = OpenLoop(name=r.name, scope=r.scope, route_id=r.route_id,
			subscribed_id=r.subscribed_id, published_id=r.published_id,
			subscriber_address=address)
		g = self.create(GetResponse, open, self.connected.proxy_address, seconds=COMPLETE_A_LOOP)
		self.on_return(g, opened, request=r, client_address=a)
	return READY

def ConnectToPeer_PENDING_NotConnected(self, message):
	self.complete()

def ConnectToPeer_PENDING_RequestLoop(self, message):
	request_and_address = (message, self.return_address)
	self.request.append(request_and_address)
	return PENDING

def ConnectToPeer_PENDING_DropLoop(self, message):
	if self.delete_request(message.route_id):
		d = LoopDropped(subscribed_id=message.subscribed_id, name=message.name, route_id=message.route_id)
		self.reply(d)
	return PENDING

def ConnectToPeer_READY_RequestLoop(self, message):
	request_and_address = (message, self.return_address)
	self.request.append(request_and_address)

	def opened(self, loop, args):
		request = args.request
		client_address = args.client_address
		if not isinstance(loop, LoopOpened):
			self.warning(f'Closing peer connection (unexpected looping response {loop})')
			self.send(Close(), self.connected.proxy_address)
			self.send(loop, self.client_address)
			return

		a = Available(name=request.name, scope=request.scope, route_id=request.route_id,
			published_id=request.published_id, subscribed_id=request.subscribed_id,
			publisher_address=loop.publisher_address, opened_at=world_now())

		self.forward(a, request.subscriber_address, loop.publisher_address)
		self.available.append((a, request.subscriber_address, loop.publisher_address))
		self.send(self.connected, client_address)

	open = OpenLoop(name=message.name, scope=message.scope, route_id=message.route_id,
		subscribed_id=message.subscribed_id, published_id=message.published_id,
		subscriber_address=message.subscriber_address)

	a = self.create(GetResponse, open, self.connected.proxy_address, seconds=COMPLETE_A_LOOP)
	self.on_return(a, opened, request=message, client_address=self.return_address)
	return READY

def ConnectToPeer_READY_DropLoop(self, message):
	dr = self.delete_request(message.route_id)
	da = self.delete_available(message.route_id)
	if dr is None or da is None:
		self.warning(f'Request to drop unknown/incomplete loop')
		d = LoopDropped(subscribed_id=message.subscribed_id, name=message.name, route_id=message.route_id)
		self.reply(d)
		return READY

	def closed(self, loop, args):
		request, available, return_address = args.request, args.available, args.return_address
		client_address = args.client_address

		if isinstance(loop, LoopClosed):
			d = Dropped(name=request.name, scope=request.scope, route_id=request.route_id,
				subscribed_id=request.subscribed_id, published_id=request.published_id,
				remote_address=available[2], opened_at=available[0].opened_at)
			self.forward(d, available[1], available[2])

			d = LoopDropped(subscribed_id=request.subscribed_id, name=request.name, route_id=request.route_id)
			self.send(d, return_address)

			if len(self.request) == 0:
				self.start(T1, GRACE_BEFORE_CLEARANCE)
			return

		if isinstance(self.connected, Connected):
			self.send(Close(), self.connected.proxy_address)
		self.complete()

	address = message.subscriber_address
	close = CloseLoop(name=message.name, scope=message.scope, route_id=message.route_id,
		subscribed_id=message.subscribed_id, published_id=message.published_id,
		subscriber_address=address)

	a = self.create(GetResponse, close, self.connected.proxy_address, seconds=COMPLETE_A_LOOP)
	self.on_return(a, closed, request=dr[0], client_address=dr[1], available=da, return_address=self.return_address)
	return READY

def ConnectToPeer_READY_T1(self, message):
	if len(self.request) == 0:
		self.send(Close(), self.connected.proxy_address)
	return READY

def ConnectToPeer_READY_Returned(self, message):
	d = self.debrief()
	if isinstance(d, OnReturned):
		d(self, message)
	return READY

def ConnectToPeer_READY_Closed(self, message):
	self.not_available()
	self.complete()

def ConnectToPeer_READY_Stop(self, message):
	self.complete()

CONNECT_TO_PEER_DISPATCH = {
	INITIAL: (
		(Start,),
		()
	),
	PENDING: (
		(Connected, NotConnected,
		RequestLoop, DropLoop),
		()
	),
	READY: (
		(RequestLoop, DropLoop,
		T1,
		Returned,
		Closed,
		Stop),
		()
	),
}

bind(ConnectToPeer, CONNECT_TO_PEER_DISPATCH)

# A route is available that would require a peer connection
# from subscriber to publisher.
class RouteOverConnect(Point, StateMachine):
	def __init__(self, route_id: UUID=None, scope: ScopeOfDirectory=None, encrypted: bool=False, subscriber: Subscribed=None, publisher: Published=None):
		Point.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.route_id = route_id
		self.scope = scope
		self.encrypted = encrypted
		self.subscriber = subscriber
		self.publisher = publisher

def RouteOverConnect_INITIAL_Start(self, message):
	r = RouteOverLoop(route_id=self.route_id, scope=self.scope, encrypted=self.encrypted,
		subscribed_id=self.subscriber.subscribed_id, published_id=self.publisher.published_id,
		name=self.publisher.name, ipp=self.publisher.listening_ipp)

	self.send(r, self.subscriber.home_address)
	return READY

def RouteOverConnect_READY_Stop(self, message):
	s = self.subscriber
	p = self.publisher
	self.send(ClearSubscriberRoute(subscribed_id=s.subscribed_id, name=p.name, route_id=self.route_id), s.home_address)
	self.send(ClearPublisherRoute(published_id=p.published_id, name=p.name, route_id=self.route_id), p.home_address)
	self.complete(Aborted())

ROUTE_OVER_PEER_DISPATCH = {
	INITIAL: (
		(Start,),
		()
	),
	READY: (
		(Stop,),
		()
	),
}

bind(RouteOverConnect, ROUTE_OVER_PEER_DISPATCH)

# A match has been found between two objects within a process.
# This also covers the process-to-library scenario.
class RouteInProcess(Point, StateMachine):
	def __init__(self, route_id: UUID=None, subscriber: Subscribed=None, publisher: Published=None, subscribe_to: SubscribeTo=None, publish_as: PublishAs=None):
		Point.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.route_id = route_id
		self.subscriber = subscriber
		self.publisher = publisher
		self.subscribe_to = subscribe_to
		self.publish_as = publish_as

	def send_route(self):
		opened_at = world_now()
		r = RouteToAddress(route_id=self.route_id, scope=ScopeOfDirectory.PROCESS,
			subscribed_id=self.subscriber.subscribed_id, published_id=self.publisher.published_id,
			subscriber_address=self.subscribe_to.subscriber_address, publisher_address=self.publish_as.publisher_address,
			name=self.publisher.name, opened_at=opened_at)

		self.send(r, self.subscriber.home_address)

def RouteInProcess_INITIAL_Start(self, message):
	pa = self.publish_as
	st = self.subscribe_to
	if pa is None and st is None:
		self.complete(Faulted('inter-library routing not supported'))

	if pa is None:
		self.send(OpenLibrary(published_id=self.publisher.published_id), self.publisher.home_address)
		return OPENING

	elif st is None:
		self.send(OpenLibrary(subscribed_id=self.subscriber.subscribed_id), self.subscriber.home_address)
		return OPENING

	self.send_route()
	return READY

def RouteInProcess_OPENING_SubscribeTo(self, message):
	self.subscribe_to = message
	self.send_route()
	return READY

def RouteInProcess_OPENING_PublishAs(self, message):
	self.publish_as = message
	self.send_route()
	return READY

def RouteInProcess_OPENING_Stop(self, message):
	self.complete(Aborted())

def RouteInProcess_READY_Stop(self, message):
	#if self.publish_as is None:
	#	self.forward(OpenLibrary(self.publisher.name), self.publisher.home_address, self.subscriber_address)
	#	return READY

	s = self.subscriber
	p = self.publisher
	self.send(ClearSubscriberRoute(subscribed_id=s.subscribed_id, name=p.name, route_id=self.route_id), s.home_address)
	self.send(ClearPublisherRoute(published_id=p.published_id, name=p.name, route_id=self.route_id), p.home_address)
	self.complete(Aborted())

ROUTE_IN_PROCESS_DISPATCH = {
	INITIAL: (
		(Start,),
		()
	),
	OPENING: (
		(SubscribeTo, PublishAs, Stop),
		()
	),
	READY: (
		(Stop,),
		()
	),
}

bind(RouteInProcess, ROUTE_IN_PROCESS_DISPATCH)

#
def find_route(route, routing):
	for r in routing:
		if r.scope == route.scope or r.route_id == route.route_id:
			return True
	return False

def scope_route(route, routing):
	for i, r in enumerate(routing):
		if r.scope == route.scope:
			return i
	return None

def shortest_route(routing, excluding=None):
	best = None
	for r in routing:
		if r.route_id == excluding:
			continue
		if best is None or r.scope.value > best.scope.value:
			best = r
	return best

def add_route(route, routing):
	routing.append(route)
	shortest = shortest_route(routing)
	return shortest

def delete_route(route_id, routing):
	d = None
	for i, r in enumerate(routing):
		if r.route_id == route_id:
			d = i
	if d is not None:
		r = routing.pop(d)
		return r
	return None

four_octets = re.compile(r'([0-9]+)\.([0-9]+)\.([0-9]+)\.([0-9]+)')

def directory_at_lan():
	d = get_local_ip()
	if not d:
		return None

	m = four_octets.fullmatch(d)
	if not m:
		return None

	if d.startswith('192.168.'):
		leading_octets = '192.168.0'
	elif d.startswith('172.'):
		octet_2 = int(m[2])
		if octet_2 < 16 or octet_2 > 31:
			return None
		leading_octets = '172.16.0'
	elif d.startswith('10.'):
		leading_octets = '10.0.0'
	else:
		return None

	a = f'{leading_octets}.195'
	return HostPort(a, DIRECTORY_PORT)

RECONNECT_DELAY = [1.0, 8.0, 32.0, 120.0]	# 1-based indexing from enum, i.e. [0] is not used.
GRACE_BEFORE_CLEARANCE = 8.0

class ObjectDirectory(Threaded, StateMachine):
	def __init__(self, directory_scope: ScopeOfDirectory=None,
			connect_to_directory: HostPort=None, accept_directories_at: HostPort=None,
			encrypted: bool=None):
		Threaded.__init__(self)
		StateMachine.__init__(self, INITIAL)
		self.directory_scope = directory_scope or ScopeOfDirectory.PROCESS
		self.connect_to_directory = connect_to_directory or HostPort()
		self.accept_directories_at = accept_directories_at or HostPort()
		self.encrypted = encrypted

		self.unique_id = uuid.uuid4()
		self.reconnect_delay = None

		# Links to the upper and lower parts of the hierarchy.
		self.connected = None
		self.listening = None
		self.accepted = {}				# Remember who connects from below and what they provide.
		self.pending_enquiry = set()

		# Keep the db clean.
		self.unique_publish = {}
		self.unique_subscribe = {}

		# For quick lookup and distribution.
		self.listed_publisher = {}
		self.listed_subscriber = {}

		# For quick matching.
		self.published_name = {}
		self.subscribed_search = {}

		# Routed listings.
		self.routed_publish = {}
		self.routed_subscribe = {}

		# Routing tables for active loops.
		self.subscriber_routing = {}

		# Connections across group, host and lan domains.
		self.peer_connect = {}

		self.directory_opened = None

	def calculate_reconnect(self, host):
		if host is None:
			return
		s = local_private_other(host)
		seconds = RECONNECT_DELAY[s.value]
		self.reconnect_delay = spread_out(seconds, 10)
		self.trace(f'Update parameter', reconnect_delay=self.reconnect_delay)

	def keep_alive(self):
		host = self.connect_to_directory.host
		localhost = host.startswith('127.')
		return not localhost

	def encrypted_directory(self):
		if self.encrypted is None:
			return CL.encrypted_process
		return self.encrypted

	def auto_connect(self, message):
		# If certain conditions are met, auto-assign a parent directory address
		# and start connecting.
		connecting_to_host = self.connect_to_directory.host is not None
		to_be_pushed = message.scope.value < self.directory_scope.value
		if connecting_to_host or not to_be_pushed:
			return

		if self.directory_scope in (ScopeOfDirectory.PROCESS, ScopeOfDirectory.GROUP):
			self.connect_to_directory = DIRECTORY_AT_HOST
		elif self.directory_scope  == ScopeOfDirectory.HOST:
			a = directory_at_lan()
			if a is None:
				return
			self.connect_to_directory = a
		else:
			return

		connect(self, self.connect_to_directory,
			keep_alive=self.keep_alive(),
			encrypted=self.encrypted_directory())
		self.calculate_reconnect(self.connect_to_directory.host)

	def add_publisher(self, listing: Published, origin: Address, publish: PublishAs):
		name = listing.name
		scope = listing.scope
		encrypted = listing.encrypted

		# Existence - by id.
		lp = self.listed_publisher.get(listing.published_id, None)
		if lp is not None:
			if lp[0].home_address == listing.home_address:
				self.trace(f'Publish ignored "{name}" (refresh)')
			else:
				self.warning(f'Publish ignored "{name}" (same id, multiple addresses)')
			return False

		# And search name.
		lp = self.published_name.get(name, None)
		if lp is not None:
			self.warning(f'Cannot publish "{name}" (multiple ids, same name)')
			return False

		if publish:
			# Publishing object is in this process. Is an
			# access point required.
			if scope.value < ScopeOfDirectory.PROCESS.value:
				a = self.create(ListeningForPeer,
					name=name, scope=scope,
					address=publish.publisher_address, encrypted=encrypted)
				self.assign(a, (listing, publish))
				return False

		elif self.directory_scope == ScopeOfDirectory.LAN:
			# This directory overlooks a LAN. Overwrite the given
			# listening ip (0.0.0.0) with the ip provided by sockets.
			a, sub, pub = self.accepted.get(self.return_address[-1])
			listing.listening_ipp = HostPort(a.opened_ipp.host, listing.listening_ipp.port)

		elif self.directory_scope in (ScopeOfDirectory.HOST, ScopeOfDirectory.GROUP):
			# This directory overlooks a HOST or GROUP. Overwrite whatever
			# was provided with the loopback address.
			listing.listening_ipp = HostPort('127.0.0.1', listing.listening_ipp.port)
		elif self.directory_scope in (ScopeOfDirectory.PROCESS, ScopeOfDirectory.LIBRARY):
			pass
		else:
			self.warning(f'Scope [{self.directory_scope}] not implemented')
			return False

		self.console(f'Published "{name}"[{self.directory_scope}] ({listing.listening_ipp})')

		lp = (listing, publish)
		self.published_name[name] = lp
		self.listed_publisher[listing.published_id] = lp

		if origin is not None:
			origin.add(listing.published_id)
		return True

	def add_subscriber(self, listing: Subscribed, origin: Address, subscribe: SubscribeTo):
		search = listing.search
		scope = listing.scope
		subscribed_id = listing.subscribed_id

		# Existence - by id.
		ls = self.listed_subscriber.get(listing.subscribed_id, None)
		if ls is not None:
			if ls[0].home_address == listing.home_address:
				self.trace(f'Subscribe ignored "{search}" (refresh)')
			else:
				self.warning(f'Subscribe ignored "{search}" (same id, multiple addresses)')
			return False

		# and search. Build out required structure.
		sr = self.subscribed_search.get(search, None)
		if sr is None:
			try:
				# Keep a single pre-compiled search machine.
				r = re.compile(listing.search)
			except re.error as e:
				t = str(e)
				self.warning(f'Cannot subscribe to "{search}" ({t})')
				return False
			s = {}
			sr = [s, r]
			self.subscribed_search[search] = sr
		else:
			s = sr[0]

		# Existence of subscriber.
		if subscribed_id in s:
			self.warning(f'Subscribe ignored "{search}" (id already registered)')
			return False

		self.console(f'Subscribed "{search}"[{self.directory_scope}]')

		ls = (listing, subscribe)
		s[subscribed_id] = ls
		self.listed_subscriber[subscribed_id] = ls

		if origin is not None:
			origin.add(listing.subscribed_id)
		return True

	def find_subscribers(self, published: Published):
		# Turn a search into a flat list of matching subscribers.
		for k, v in self.subscribed_search.items():
			m = v[1].fullmatch(published.name)
			if m:
				for s in v[0].values():
					yield s[0]

	def find_publishers(self, subscribed: Subscribed):
		# Turn a search into a flat list of matching publishers.
		sr = self.subscribed_search.get(subscribed.search, None)
		if sr is None:
			return
		machine = sr[1]
		for k, lp in self.published_name.items():
			m = machine.fullmatch(k)
			if m:
				yield lp[0]

	def create_route(self, subscriber: Subscribed, publisher: Published):
		self.console(f'Route', name=publisher.name, scope=self.directory_scope, encrypted=publisher.encrypted)
		# There is a match at this scope between given sub and pub.
		# Create the appropriate route object and record its existence.
		# Communication with relevant directories is up to the route.

		route_id = uuid.uuid4()
		if self.directory_scope in (ScopeOfDirectory.LAN, ScopeOfDirectory.HOST, ScopeOfDirectory.GROUP):
			r = self.create(RouteOverConnect,
				route_id=route_id, scope=self.directory_scope, encrypted=publisher.encrypted,
				subscriber=subscriber, publisher=publisher)

		elif self.directory_scope == ScopeOfDirectory.PROCESS:
			s = self.listed_subscriber[subscriber.subscribed_id][1]
			p = self.listed_publisher[publisher.published_id][1]

			r = self.create(RouteInProcess, route_id=route_id,
				subscriber=subscriber, publisher=publisher,
				subscribe_to=s, publish_as=p)

		else:
			self.warning(f'Cannot route "{publisher.name}" at [{self.directory_scope}]')
			return

		# When this publisher is cleared, nudge this route.
		pr = self.routed_publish.get(publisher.published_id, None)
		if pr is None:
			pr = [publisher, set()]
			self.routed_publish[publisher.published_id] = pr
		pr[1].add(r)

		# When this subscriber is cleared, nudge this route.
		sr = self.routed_subscribe.get(subscriber.subscribed_id, None)
		if sr is None:
			sr = [subscriber, set()]
			self.routed_subscribe[subscriber.subscribed_id] = sr
		sr[1].add(r)

		# When the route terminates, clear out the links.
		def clear(self, value, args):
			pr = self.routed_publish.get(args.published_id)
			if pr is not None:
				self.console(f'Cleared route "{pr[0].name}"[{self.directory_scope}] ({args.published_id})')

				pr[1].discard(args.route)
				if len(pr[1]) == 0:
					self.routed_publish.pop(args.published_id, None)
			else:
				self.console(f'Route not cleared "{args.published_id}" [{self.directory_scope}]')

			sr = self.routed_subscribe.get(args.subscribed_id)
			if sr is not None:
				sr[1].discard(args.route)
				if len(sr[1]) == 0:
					self.routed_subscribe.pop(args.subscribed_id, None)

		self.on_return(r, clear, subscribed_id=subscriber.subscribed_id, published_id=publisher.published_id, route=r)

	def clear_listings(self, subscribers, publishers):
		stop = Stop()
		# Remove the listed subscriber ids from this directory.
		# Routing, listings and searching maps need to be popped.
		for s in subscribers:
			# Terminate all routes involving this subscriber.
			routed_subscribe = self.routed_subscribe.get(s, None)
			if routed_subscribe:
				for a in routed_subscribe[1]:
					# Entry cleared by termination of route.
					self.send(stop, a)

			# Remove from the listings.
			listed_subscribe = self.listed_subscriber.pop(s, None)
			if listed_subscribe is None:
				continue
			search = listed_subscribe[0].search

			# Remove from the matching machinery.
			subscribed = self.subscribed_search.get(search, None)
			if subscribed is None:
				continue
			a, m = subscribed
			a.pop(s, None)

			self.console(f'Cleared subscribed "{search}"[{self.directory_scope}]')

			# If this is the home directory, remove from uniqueness check.
			if listed_subscribe[1] is not None:
				unique_subscribe = (listed_subscribe[1].search, listed_subscribe[1].subscriber_address)
				self.unique_subscribe.pop(unique_subscribe, None)

		# Remove the listed publisher ids from this directory.
		for p in publishers:
			# Terminate all routes involving this publisher.
			routed_publish = self.routed_publish.get(p, None)
			if routed_publish:
				for a in routed_publish[1]:
					# Entry cleared by termination of route.
					self.send(stop, a)

			# Remove from the listings.
			listed_publish = self.listed_publisher.pop(p, None)
			if listed_publish is None:
				continue
			name = listed_publish[0].name

			# Remove from the matching machinery.
			self.published_name.pop(name, None)

			self.console(f'Cleared published "{name}"[{self.directory_scope}]')

			# If this is the home directory, remove from uniqueness check.
			if listed_publish[1] is not None:
				unique_publish = listed_publish[1].name
				self.unique_publish.pop(unique_publish, None)

	def open_route(self, route):
		# Callback on loss of ConnectToPeer.
		def clear_ipp(self, value, args):
			self.console(f'Clearing peer connection {args.ipp}')
			self.peer_connect.pop(args.ipp, None)

		def response_to_request(self, value, args):
			r = args.request
			sr = self.subscriber_routing.get(r.subscribed_id, None)
			if sr is None:
				return
			if isinstance(value, Faulted):
				self.console(f'Cannot establish session for {r.subscribed_id} ({value})')
				return
			arc = sr.get(r.name, None)
			if arc is None:
				return
			arc[2] = value

		# Initiate the given route. This is on a per-type basis.
		# Should be a virtual method.
		self.trace(f'Opening route "{route.name}"[{route.scope}]')

		if isinstance(route, RouteOverLoop):
			# Comms is over a standard message connection between this process
			# and the process at the given network address.
			ls = self.listed_subscriber.get(route.subscribed_id, None)
			c = self.peer_connect.get(route.ipp, None)
			if c is None:
				c = self.create(ConnectToPeer, route.ipp, route.encrypted)
				self.on_return(c, clear_ipp, ipp=route.ipp)
				self.peer_connect[route.ipp] = c
			address = ls[1].subscriber_address

			# Initiate loop over this connection for subscriber/name relation.
			r = RequestLoop(name=route.name, scope=route.scope, route_id=route.route_id,
				subscribed_id=route.subscribed_id, subscriber_address=address,
				published_id=route.published_id,
			)
			a = self.create(GetResponse, r, c)
			self.on_return(a, response_to_request, request=r)

		elif isinstance(route, RouteToAddress):
			# Comms is between objects within this process, or this process and a library.
			a = Available(name=route.name, scope=route.scope, route_id=route.route_id,
				subscribed_id=route.subscribed_id, published_id=route.published_id,
				publisher_address=route.publisher_address, opened_at=route.opened_at)

			d = Delivered(name=route.name, scope=route.scope, route_id=route.route_id,
				subscribed_id=route.subscribed_id, published_id=route.published_id,
				subscriber_address=route.subscriber_address, opened_at=route.opened_at)

			self.forward(a, route.subscriber_address, route.publisher_address)
			self.forward(d, route.publisher_address, route.subscriber_address)
		else:
			self.warning(f'Routing by {type(route)} not implemented')

	def drop_route(self, ls, route):
		self.trace(f'Dropping route "{route.name}"[{route.scope}]')

		if isinstance(route, RouteOverLoop):
			# Comms is over actual transport.
			c = self.peer_connect.get(route.ipp, None)
			if c is None:
				return

			def dropped(self, value, args):
				if not isinstance(value, LoopDropped):
					self.warning(f'Unexpected response to drop of loop ({value})')
				route = args.route
				try:
					routing = self.subscriber_routing[route.subscribed_id][route.name]
				except (KeyError, IndexError):
					return READY

				if routing[0] is None:
					pass
				elif routing[0].route_id == route.route_id:
					pass
				else:
					return READY		# Routed by some other means.

				shortest = shortest_route(routing[1])	# Get the best.
				if shortest is None:					# Nothing there.
					return READY
				routing[0] = shortest
				self.open_route(shortest)

			d = DropLoop(name=route.name, scope=route.scope, route_id=route.route_id,
				subscribed_id=route.subscribed_id, published_id=route.published_id,
				subscriber_address=ls[1].subscriber_address)

			a = self.create(GetResponse, d, c, seconds=COMPLETE_A_LOOP)
			self.on_return(a, dropped, route=route)

		elif isinstance(route, RouteToAddress):
			s = Dropped(name=route.name, scope=route.scope, route_id=route.route_id,
				subscribed_id=route.subscribed_id, published_id=route.published_id,
				remote_address=route.publisher_address, opened_at=route.opened_at)

			p = Dropped(name=route.name, scope=route.scope, route_id=route.route_id,
				subscribed_id=route.subscribed_id, published_id=route.published_id,
				remote_address=route.subscriber_address, opened_at=route.opened_at)

			self.forward(s, route.subscriber_address, route.publisher_address)
			self.forward(p, route.publisher_address, route.subscriber_address)

	def clear_route(self, ls, route):
		self.trace(f'Clearing route "{route.name}"[{route.scope}]')

		if isinstance(route, RouteOverLoop):
			# Transport-based pub-sub is not cleared on loss of the
			# control channel.
			return False

		elif isinstance(route, RouteToAddress):
			s = Dropped(name=route.name, scope=route.scope, route_id=route.route_id,
				subscribed_id=route.subscribed_id, published_id=route.published_id,
				remote_address=route.publisher_address, opened_at=route.opened_at)

			p = Dropped(name=route.name, scope=route.scope, route_id=route.route_id,
				subscribed_id=route.subscribed_id, published_id=route.published_id,
				remote_address=route.subscriber_address, opened_at=route.opened_at)

			self.forward(s, route.subscriber_address, route.publisher_address)
			self.forward(p, route.publisher_address, route.subscriber_address)

			return True
		return False

	def send_up(self, listing):
		if isinstance(self.connected, Connected):
			if listing.scope.value < self.directory_scope.value:
				self.send(listing, self.connected.proxy_address)

	def push_up(self):
		published = [v[0] for k, v in self.published_name.items() if v[0].scope.value < self.directory_scope.value]
		subscribed = []
		for k, v in self.subscribed_search.items():
			for t in v[0].values():
				if t[0].scope.value < self.directory_scope.value:
					subscribed.append(t[0])
		if published or subscribed:
			self.send(PublishedDirectory(published, subscribed), self.connected.proxy_address)

	def get_directory(self, client_address):
		argv = sys.argv
		if argv[0].rfind('python') == -1:
			name = argv[0]
		else:
			name = argv[1]
		executable = os.path.basename(name)

		published = [v[0] for k, v in self.listed_publisher.items()]
		subscribed = [v[0] for k, v in self.listed_subscriber.items()]

		directory_route = {}
		for k, v in self.routed_publish.items():
			pub, routed = v
			for r in routed:
				directory_route[r] = DirectoryRoute(name=pub.name, published_id=pub.published_id)

		for k, v in self.routed_subscribe.items():
			sub, routed = v
			for r in routed:
				dr = directory_route.get(r, None)
				if dr is None:
					continue
				dr.subscribed_id = sub.subscribed_id

		routed = [v for k, v in directory_route.items() if v.subscribed_id and v.published_id]

		peer = {}
		for subscribed_id, v in self.subscriber_routing.items():
			ls = self.listed_subscriber.get(subscribed_id, None)
			if ls is None:
				continue
			s = [PeerSession(name=name, route=t3[0], status=t3[2]) for name, t3 in v.items()]
			c = DirectoryPeer(subscribed_id=subscribed_id, search=ls[0].search, session=s)
			peer[subscribed_id] = c

		primary_ip = get_local_ip()

		sub_directory = {}
		if isinstance(self.listening, Listening):
			accept_directories_at = self.listening.listening_ipp
			for k, v in self.accepted.items():
				ta, sub, pub = v
				sub_directory[ta.opened_ipp] = ta.proxy_address
		else:
			accept_directories_at = self.accept_directories_at

		directory = DirectoryListing(unique_id=self.unique_id, executable=executable,
			directory_address=self.object_address, scope=self.directory_scope,
			primary_ip=primary_ip,
			connect_to_directory=self.connect_to_directory, accept_directories_at=accept_directories_at,
			published=published, subscribed=subscribed,
			routed=routed, peer=peer, sub_directory=sub_directory)

		self.send(directory, client_address)

#
#
def ObjectDirectory_INITIAL_Start(self, message):
	self.calculate_reconnect(self.connect_to_directory.host)
	if self.connect_to_directory.host is not None:
		connect(self, self.connect_to_directory,
			keep_alive=self.keep_alive(),
			encrypted=self.encrypted_directory())
	if self.accept_directories_at.host is not None:
		listen(self, self.accept_directories_at,
			encrypted=self.encrypted_directory())
	return READY

#
def ObjectDirectory_READY_Listening(self, message):
	self.listening = message
	for p in self.pending_enquiry:
		self.send(message.listening_ipp, p)
	self.pending_enquiry = set()
	return READY

def ObjectDirectory_READY_NotListening(self, message):
	self.listening = message
	# Schedule a retry.
	return READY

def ObjectDirectory_READY_Connected(self, message):
	self.connected = message
	self.push_up()
	if self.directory_opened:
		self.send(DirectoryOpened(), self.directory_opened)
		self.directory_opened = None
	return READY

def ObjectDirectory_READY_NotConnected(self, message):
	if self.connect_to_directory.host:
		self.connected = message
		self.start(T1, self.reconnect_delay)
		if self.directory_opened:
			self.send(DirectoryOpened(), self.directory_opened)
			self.directory_opened = None
	return READY

def ObjectDirectory_READY_T1(self, message):
	if self.connect_to_directory.host is not None:
		connect(self, self.connect_to_directory,
			keep_alive=self.keep_alive(),
			encrypted=self.encrypted_directory())
	return READY

def ObjectDirectory_READY_Accepted(self, message):
	self.accepted[self.return_address[-1]] = [message, set(), set()]	# Accepted, subs, pubs.
	return READY

def ObjectDirectory_READY_Closed(self, message):
	if isinstance(self.connected, Connected):
		if self.return_address == self.connected.proxy_address:
			self.connected = message
			self.start(T1, self.reconnect_delay)
			return READY

	p = self.accepted.pop(self.return_address[-1], None)
	if p is None:
		return READY
	self.clear_listings(p[1], p[2])
	if isinstance(self.connected, Connected) and (p[1] or p[2]):
		self.send(ClearListings(p[1], p[2]), self.connected.proxy_address)
	return READY

def ObjectDirectory_READY_Enquiry(self, message):
	if self.accept_directories_at.host is None:
		self.accept_directories_at = DIRECTORY_AT_EPHEMERAL
		listen(self, self.accept_directories_at,
			encrypted=self.encrypted_directory())
		self.pending_enquiry.add(self.return_address)
		return READY

	if not isinstance(self.listening, Listening):
		self.pending_enquiry.add(self.return_address)
	else:
		self.reply(self.listening.listening_ipp)

	return READY

def ObjectDirectory_READY_PublishAs(self, message):
	name = message.name
	scope = message.scope
	encrypted = message.encrypted

	unique_publish = name
	r = self.unique_publish.get(unique_publish, None)
	if r is not None:
		self.reply(NotPublished(name=name, scope=scope, note=f'already published'))
		return READY

	self.auto_connect(message)

	published_id = uuid.uuid4()
	listing = Published(name=name, scope=scope, encrypted=encrypted,
		published_id=published_id, home_address=self.object_address)

	if not self.add_publisher(listing, None, message):
		return READY
	self.unique_publish[unique_publish] = published_id
	if self.directory_scope.value < ScopeOfDirectory.LIBRARY.value:
		self.send(listing, message.publisher_address)

	for s in self.find_subscribers(listing):
		self.create_route(s, listing)
	self.send_up(listing)

	return READY

def ObjectDirectory_READY_HostPort(self, message):
	d = self.progress()
	if d is None:
		self.warning(f'cannot complete ListenForPeer (no message record)')
		return READY
	listing, publish = d
	listing.listening_ipp = message		# Update with live network address.

	self.console(f'Published[{self.directory_scope}]', name=listing.name, listening=message)

	self.published_name[listing.name] = (listing, publish)
	self.listed_publisher[listing.published_id] = (listing, publish)

	unique_publish = publish.name
	self.unique_publish[unique_publish] = listing.published_id
	self.send(listing, publish.publisher_address)

	for s in self.find_subscribers(listing):
		self.create_route(s, listing)
	self.send_up(listing)

	return READY

def ObjectDirectory_READY_SubscribeTo(self, message):
	search = message.search
	scope = message.scope

	unique_subscribe = (search, self.return_address)
	r = self.unique_subscribe.get(unique_subscribe, None)
	if r is not None:
		self.reply(NotSubscribed(search=search, scope=scope, note=f'already subscribed'))
		return READY

	self.auto_connect(message)

	subscribed_id = uuid.uuid4()
	listing = Subscribed(search=search, scope=scope, subscribed_id=subscribed_id, home_address=self.object_address)
	if not self.add_subscriber(listing, None, message):
		self.reply(NotSubscribed(search=search, scope=scope, note=f'duplicates/search expression'))
		return READY
	self.unique_subscribe[unique_subscribe] = subscribed_id
	self.send(listing, message.subscriber_address)

	for p in self.find_publishers(listing):
		self.create_route(listing, p)
	self.send_up(listing)

	return READY

def ObjectDirectory_READY_Published(self, message):
	if message.scope.value > self.directory_scope.value:
		return READY

	a, sub, pub = self.accepted[self.return_address[-1]]
	if not self.add_publisher(message, pub, None):
		self.send(Advisory(name=message.name, scope=self.directory_scope, published_id=message.published_id), message.home_address)
		return READY
	self.auto_connect(message)

	for s in self.find_subscribers(message):
		self.create_route(s, message)
	self.send_up(message)

	return READY

def ObjectDirectory_READY_Advisory(self, message):
	self.warning(f'Cannot publish "{message.name}" at [{message.scope}]')
	return READY

def ObjectDirectory_READY_Subscribed(self, message):
	if message.scope.value > self.directory_scope.value:
		return READY

	a, sub, pub = self.accepted[self.return_address[-1]]
	if not self.add_subscriber(message, sub, None):
		return READY
	self.auto_connect(message)

	for p in self.find_publishers(message):
		self.create_route(message, p)
	self.send_up(message)
	return READY

def ObjectDirectory_READY_PublishedDirectory(self, message):
	a, sub, pub = self.accepted[self.return_address[-1]]
	highest = None
	for p in message.published:
		if p.scope.value > self.directory_scope.value:
			continue
		if not self.add_publisher(p, pub, None):
			continue
		if highest is None or p.scope.value < highest.scope.value:
			highest = p
		for s in self.find_subscribers(p):
			self.create_route(s, p)

	highest is not None and self.auto_connect(highest)

	for s in message.subscribed:
		if s.scope.value > self.directory_scope.value:
			continue
		if not self.add_subscriber(s, sub, None):
			continue
		if highest is None or s.scope.value < highest.scope.value:
			highest = s
		for p in self.find_publishers(s):
			self.create_route(s, p)

	highest is not None and self.auto_connect(highest)

	if isinstance(self.connected, Connected):
		self.push_up()
	return READY

def ObjectDirectory_READY_ClearListings(self, message):
	self.clear_listings(message.subscribers, message.publishers)
	if isinstance(self.connected, Connected):
		self.send(message, self.connected.proxy_address)
	return READY

def ObjectDirectory_READY_ClearPublished(self, message):
	subscribers = set()
	publishers = set([message.published_id])
	self.clear_listings(subscribers, publishers)
	self.reply(PublishedCleared(name=message.name, scope=message.scope, published_id=message.published_id, note=message.note))
	if isinstance(self.connected, Connected):
		self.send(ClearListings(subscribers, publishers), self.connected.proxy_address)
	return READY

def ObjectDirectory_READY_ClearSubscribed(self, message):
	subscribers = set([message.subscribed_id])
	publishers = set()
	self.clear_listings(subscribers, publishers)
	self.reply(SubscribedCleared(search=message.search, scope=message.scope, subscribed_id=message.subscribed_id, note=message.note))
	if isinstance(self.connected, Connected):
		self.send(ClearListings(subscribers, publishers), self.connected.proxy_address)
	return READY

def ObjectDirectory_READY_ClearSubscriberRoute(self, message):
	subscribed_id = message.subscribed_id
	listing = self.listed_subscriber.get(subscribed_id, None)
	if listing is None:
		self.warning('No such subscription')
		return READY

	# Find the routing table.
	subscriber = self.subscriber_routing.get(subscribed_id, None)
	if subscriber is None:
		return READY

	routing = subscriber.get(message.name, None)
	if routing is None:
		return READY

	# Delete the route from the available routes.
	d = delete_route(message.route_id, routing[1])
	if not d:
		self.warning('Unknown route')
		return READY

	if routing[0] and routing[0].route_id == message.route_id:
		if self.clear_route(listing, routing[0]):
			routing[0] = None

	# Clear out empty vessels.
	if len(routing[1]) == 0:
		subscriber.pop(message.name, None)

	if len(subscriber) == 0:
		self.subscriber_routing.pop(subscribed_id, None)
	return READY

def ObjectDirectory_READY_ClearPublisherRoute(self, message):
	p = self.listed_publisher.get(message.published_id, None)
	if p is None:
		return READY
	# So far there is no action required on the
	# publisher side.
	return READY

def ObjectDirectory_READY_OpenLibrary(self, message):
	if message.published_id:
		p = self.listed_publisher.get(message.published_id, None)
		if p[1]:
			self.reply(p[1])
	elif message.subscribed_id:
		s = self.listed_subscriber.get(message.subscribed_id, None)
		if s[1]:
			self.reply(s[1])
	return READY

def ObjectDirectory_READY_SubscriberRoute(self, message):
	subscribed_id = message.subscribed_id

	# Add the route to the routing[subscriber][name] table.
	# Evaluate the (changed) routing options.
	# If no current loop, initiate the best option.
	ls = self.listed_subscriber.get(subscribed_id, None)
	if ls is None or ls[1] is None:
		self.warning('No such subscription or not the home directory')
		return READY

	# Routing per listing
	subscriber = self.subscriber_routing.get(subscribed_id, None)
	if subscriber is None:
		subscriber = {}
		self.subscriber_routing[subscribed_id] = subscriber

	# Per matched name
	routing = subscriber.get(message.name, None)
	if routing is None:
		routing = [None, [], ToBeConfirmed('no active route or loop not closed')]
		subscriber[message.name] = routing

	# Final checks.
	i = scope_route(message, routing[1])
	if i is not None:
		if isinstance(message, RouteOverLoop):
			if equal_ipp(message.ipp, routing[1][i].ipp):
				self.trace(f'Replacement route at [{message.scope}]')
				routing[1][i] = message
				# Cant do this - would invalidate session notifications.
				#if routing[0].scope == message.scope:
				#	routing[0] = message
				return READY
		self.trace(f'Duplicate route at [{message.scope}]')
		return READY

	# Evaluate what affect the addition of this route will
	# have on this subscriber-to-name connection effort.
	shortest = add_route(message, routing[1])

	if routing[0] is not None:	# Route is active.
		if shortest.scope.value > routing[0].scope.value:
			self.trace(f'Upgrading "{routing[0].name}"[{routing[0].scope}] to inner [{shortest.scope}]')
			self.drop_route(ls, routing[0])
		else:
			self.trace(f'Added outer route "{message.name}"[{message.scope}]')
		return READY

	routing[0] = shortest
	self.open_route(shortest)
	return READY

def ObjectDirectory_READY_LoopDropped(self, message):
	try:
		routing = self.subscriber_routing[message.subscribed_id][message.name]
	except (KeyError, IndexError):
		return READY

	if routing[0] and routing[0].route_id == message.route_id:
		routing[0] = None
		shortest = shortest_route(routing[1], excluding=message.route_id)
		if shortest is None:
			return READY
		routing[0] = shortest
		self.open_route(shortest)
	return READY

def ObjectDirectory_READY_Returned(self, message):
	d = self.debrief()
	if isinstance(d, OnReturned):
		d(self, message)
	return READY

def ObjectDirectory_READY_Stop(self, message):
	self.complete()

import json
def ObjectDirectory_READY_Incognito(self, message):
	s = json.dumps(message.decoded_word)
	self.console(type_name=message.type_name, word=s)
	return READY

def ObjectDirectory_READY_OpenDirectory(self, message):
	self.directory_opened = self.return_address

	if self.connected:
		self.reply(DirectoryOpened())
		return READY

	if self.connect_to_directory.host is None:
		pa = PublishAs(name='open-directory', scope=message.scope)
		self.auto_connect(pa)

	return READY

def ObjectDirectory_READY_ListDirectory(self, message):
	if isinstance(self.connected, Connected):
		self.forward(message, self.connected.proxy_address, self.return_address)
		return READY

	self.get_directory(self.return_address)
	return READY

def ObjectDirectory_READY_GetDirectory(self, message):
	self.get_directory(self.return_address)
	return READY

def ObjectDirectory_READY_Ping(self, message):
	self.reply(message)
	return READY

OBJECT_DIRECTORY_DISPATCH = {
	INITIAL: (
		(Start,),
		()
	),
	READY: (
		(Listening, NotListening,
		Connected, NotConnected,
		T1,
		Accepted, Closed,
		Enquiry,
		PublishAs, SubscribeTo, HostPort,
		Published, Subscribed,
		Advisory,
		PublishedDirectory,
		ClearListings,
		ClearPublished, ClearSubscribed,
		ClearSubscriberRoute, ClearPublisherRoute,
		LoopDropped,
		OpenLibrary,
		SubscriberRoute,
		Returned,
		Stop,
		Incognito,
		OpenDirectory, ListDirectory, GetDirectory,
		Ping,),
		()
	),
}

bind(ObjectDirectory, OBJECT_DIRECTORY_DISPATCH)

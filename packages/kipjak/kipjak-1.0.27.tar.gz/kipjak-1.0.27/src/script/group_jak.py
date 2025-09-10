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

"""Directory at the GROUP scope.

Starts and monitors a collection of processes, according to the materials
it finds in a folder (i.e. home_path) and optional search criteria.

An empty list of patterns implies "all roles". A non-empty list of
patterns that fails to match anything is considered an error.

Termination is by intervention (i.e. control-c) or termination of the
child processes. There are several variations on this general theme;

* termination of all processes, retries optional (the default),
* termination of a specified process, retries optional (see main_role).
"""
__docformat__ = 'restructuredtext'

import re
import kipjak as kj

#
#
DEFAULT_GROUP = 'group'

class INITIAL: pass
class ENQUIRING: pass
class RUNNING: pass
class RETURNING: pass
class GROUP_RETURNING: pass

dict_type = kj.def_type(dict[str,kj.Any])

class Group(kj.Threaded, kj.StateMachine):
	def __init__(self, *search,
			directory_at_host: kj.HostPort=None, directory_at_lan: kj.HostPort=None,
			encrypted_directory: bool=None,
			retry: kj.RetryIntervals=None, main_role: str=None) -> kj.Any:
		kj.Threaded.__init__(self)
		kj.StateMachine.__init__(self, INITIAL)
		self.search = search			# List or re's.
		self.directory_at_host = directory_at_host
		self.directory_at_lan = directory_at_lan
		self.encrypted_directory = encrypted_directory
		self.retry = retry
		self.main_role = main_role

		self.home_path = kj.CL.home_path or kj.DEFAULT_HOME
		self.role_name = kj.CL.role_name or DEFAULT_GROUP

		self.machine = []				# Compiled re's.
		self.home = {}					# Roles matched by patterns.
		self.ephemeral = None			# The connect_to_directory value for child processes.
		self.interval = {}				# Interval iterators for each role.
		self.group_returned = {}		# Values returned by self-terminating processes

def Group_INITIAL_Start(self, message):
	if self.search:
		s = ', '.join(self.search)
		self.trace(f'Search "{s}"')

	if self.directory_at_host:
		connect_to_directory = self.directory_at_host
	elif self.directory_at_lan:
		connect_to_directory = self.directory_at_lan
	else:
		connect_to_directory = None

	accept_directories_at = kj.HostPort('127.0.0.1', 0)

	self.directory = self.create(kj.ObjectDirectory, directory_scope=kj.ScopeOfDirectory.GROUP,
		connect_to_directory=connect_to_directory,
		accept_directories_at=accept_directories_at,
		encrypted=self.encrypted_directory)
	self.assign(self.directory, 0)

	self.send(kj.Enquiry(), self.directory)
	return ENQUIRING

def Group_ENQUIRING_HostPort(self, message):
	self.ephemeral = message					# This is accept_directories_at.

	# Load all the roles.
	home = kj.open_home(self.home_path)
	if home is None:
		self.complete(kj.Faulted(f'cannot open path "{self.home_path}"'))

	# Compile all the patterns.
	for s in self.search:
		try:
			m = re.compile(s)
		except re.error as e:
			self.complete(kj.Faulted(f'cannot compile search "{s}"', str(e)))
		self.machine.append(m)

	# Scan for roles matching a pattern.
	if self.machine:
		def match(name):
			for m in self.machine:
				b = m.match(name)
				if b:
					return True
			return False

		home = {k: v for k, v in home.items() if match(k)}
		if not home:
			s = ', '.join(self.search)
			self.complete(kj.Faulted(f'No roles matching "{s}"'))

	elif not home:
		self.complete(kj.Faulted(f'No roles at location "{self.home_path}"'))

	# Start the roles in this non-empty list.
	encrypted_process = self.encrypted_directory == True
	for k, v in home.items():
		a = self.create(kj.ProcessObject, v,
			home_path=self.home_path, role_name=k, top_role=True,
			directory_scope=kj.ScopeOfDirectory.PROCESS,
			connect_to_directory=self.ephemeral,
			encrypted_process=encrypted_process)
		self.assign(a, k)

	# Remember for restarts.
	self.home = home
	return RUNNING

def Group_ENQUIRING_Faulted(self, message):
	self.complete(message)

def Group_ENQUIRING_Stop(self, message):
	self.complete(kj.Aborted())

def Group_RUNNING_Returned(self, message):
	d = self.debrief()
	if isinstance(d, kj.OnReturned):			# Restart callbacks.
		d(self, message)
		return RUNNING

	if d == self.main_role:						# Declared "main" - no retries.
		if not self.working():					# Includes ProcessObjects and restart callbacks.
			self.complete(message.message)

		self.abort(message.message)
		return RETURNING

	#
	self.group_returned[d] = message.message

	if self.retry is None:						# Not configured for restarts.
		if not self.working():					# As above.
			message = kj.cast_to(self.group_returned, dict_type)
			self.complete(message)

		if self.main_role is None:
			self.abort()
			return GROUP_RETURNING

		return RUNNING

	i = self.interval.get(d, None)
	if i is None:
		i = kj.smart_intervals(self.retry)
		self.interval[d] = i

	try:
		seconds = next(i)
		self.trace(f'Restart "{d}" ({seconds} seconds)')
	except StopIteration:
		if not self.working():					# As above.
			message = kj.cast_to(self.group_returned, dict_type)
			self.complete(message)

		if self.main_role is None:
			self.abort()
			return GROUP_RETURNING

		return RUNNING

	def restart(self, value, args):
		a = self.create(kj.ProcessObject, self.home[args.role],
			home_path=self.home_path, role_name=args.role, top_role=True,
			directory_scope=kj.ScopeOfDirectory.PROCESS, connect_to_directory=self.ephemeral)
		self.assign(a, args.role)

	# Run a no-op with the desired timeout.
	a = self.create(kj.Delay, seconds=seconds)
	self.on_return(a, restart, role=d)
	return RUNNING

def Group_RUNNING_Faulted(self, message):
	if not self.working():
		self.complete(message)

	self.abort(message.message)
	return RETURNING

def Group_RUNNING_Stop(self, message):
	if not self.working():
		self.complete(kj.Aborted())

	self.abort(kj.Aborted())
	return RETURNING

def Group_RETURNING_Returned(self, message):
	d = self.debrief()
	if isinstance(d, kj.OnReturned):		# Restart callbacks.
		pass

	if not self.working():					# Includes ProcessObjects and restart callbacks.
		self.complete(self.aborted_message)

	return RETURNING

def Group_GROUP_RETURNING_Returned(self, message):
	d = self.debrief()
	if isinstance(d, kj.OnReturned):		# Restart callbacks.
		pass
	else:
		self.group_returned[d] = message.message

	if not self.working():					# Includes ProcessObjects and restart callbacks.
		message = kj.cast_to(self.group_returned, dict_type)
		self.complete(message)

	return GROUP_RETURNING


GROUP_DISPATCH = {
	INITIAL: (
		(kj.Start,),
		()
	),
	ENQUIRING: (
		(kj.HostPort, kj.Faulted, kj.Stop),
		()
	),
	RUNNING: (
		(kj.Returned, kj.Faulted, kj.Stop),
		()
	),
	RETURNING: (
		(kj.Returned,),
		()
	),
	GROUP_RETURNING: (
		(kj.Returned,),
		()
	),
}

kj.bind(Group, GROUP_DISPATCH)

def main():
	# See send(kj.Enquiry()) and Group_ENQUIRING_HostPort for how
	# this process acquires the right listening configuration.
	# Unless there is an explicit argument this will open a listen
	# port at 127.0.0.1:0 (i.e. ephemeral). If the directory
	# is presented with pub-subs for higher levels and no connect
	# address has been specified, it will auto-connect to
	# DIRECTORY_AT_HOST (e.g. 127.0.0.1:DIRECTORY_PORT)
	kj.create(Group)

if __name__ == '__main__':
	main()

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

"""kipjak, command line utility.

CRUD for creation/management of a set of process definitions.
Process orchestration for running images of defintiions.
Access to records of execution.
"""
__docformat__ = 'restructuredtext'

import os
import stat
import signal
import re
import datetime
import uuid
import kipjak as kj
import kipjak.rolling_log as rl
import kipjak.process_directory as pd
import kipjak.object_directory as od

from enum import Enum
import calendar

#
GROUP_ROLE = 'group'
GROUP_EXECUTABLE = 'group-jak'

#
def cli(self, *word):
	# At [0] is the tuple created by command_sub_arguments() based on the
	# presence of a valid sub-command name, or its None.
	if not word:
		# A non-sub execution of the utility.
		return kj.Faulted('no sub-command')
	sub = word[0]
	word = word[1:]

	sub_command, jump, sub_args, remainder = sub

	# Catch uncurated args that are not going anywhere.
	if jump not in (create, add, update) and (remainder[0] or remainder[1]):
		a = [k for k in remainder[0].keys()]
		b = [k for k in remainder[1].keys()]
		a.extend(b)
		a = ','.join(a)
		return kj.Faulted(f'cannot execute "{sub_command}"', f'unknown arg(s) "{a}"')

	# Transfer to sub function. Perhaps could be
	# a self.create.
	return jump(self, word, remainder, **sub_args)

kj.bind(cli)

def create(self, word, remainder):
	'''Create a new area on disk to hold process definitions. Return Faulted/None.'''
	home_path = word_i(word, 0) or kj.CL.home_path or kj.DEFAULT_HOME

	cannot_create = f'cannot create "{home_path}"'
	if os.path.isfile(home_path):
		return kj.Faulted(cannot_create, 'existing file')

	elif os.path.isdir(home_path):
		return kj.Faulted(cannot_create, 'existing folder')

	self.console('create', home_path=home_path)

	try:
		f = kj.Folder(home_path)
		f.folder('script')
		f.folder('resource')
		f.folder('role')
		f.folder('departures')
		f.folder('arrivals')

	except OSError as e:
		return kj.Faulted(cannot_create, str(e))

	# Folder created by execution of group create-role.
	self.create(kj.ProcessObject, GROUP_EXECUTABLE,
		origin=kj.ProcessOrigin.RUN,
		home_path=home_path,
		role_name=GROUP_ROLE, top_role=True,
		create_role=True,
		remainder_args=remainder)

	m = self.input()
	if not isinstance(m, kj.Returned):
		return kj.Faulted(cannot_create, f'unexpected process response {m}')

	if isinstance(m.message, kj.Faulted):
		return m.message

	# Consume the expected response.
	if not isinstance(m.message, kj.CommandResponse):
		t = kj.message_to_tag(m.message)
		return kj.Faulted(cannot_create, f'unexpected command response {t}')

	return None

kj.bind(create)

#
#
def add(self, word, remainder, role_count: int=None, role_start: int=0):
	'''Add process definition(s) to an existing store. Return Faulted/None.'''
	executable = word_i(word, 0)
	role_name = word_i(word, 1) or kj.CL.role_name
	home_path = kj.CL.home_path or kj.DEFAULT_HOME

	if executable is None:
		return kj.Faulted('cannot add role', 'no module specified')
	bp = kj.breakpath(executable)

	role_name = role_name or bp[1]
	if role_name is None:
		return kj.Faulted('cannot add role', 'no role specified')

	cannot_add = f'cannot add "{role_name}"'

	if role_name.startswith(GROUP_ROLE):
		return kj.Faulted(cannot_add, 'reserved name')

	home = kj.open_home(home_path)
	if home is None:
		return kj.Faulted(cannot_add, f'home path "{home_path}" does not exist or contains unexpected/incomplete materials')

	if role_count is None:
		role_call = [role_name]
	elif 1 <= role_count <= 1000:
		role_call = [f'{role_name}-{i}' for i in range(role_start, role_start + role_count)]
	else:
		return kj.Faulted(cannot_add, 'expecting role_count in the range 1...1000')

	c = set(home.keys()) & set(role_call)
	if c:
		s = ','.join(c)
		return kj.Faulted(cannot_add, f'collision of roles "{s}"')

	self.console('add', executable=executable, role_name=role_name, home_path=home_path)

	for r in role_call:
		a = self.create(kj.ProcessObject, executable,
			origin=kj.ProcessOrigin.RUN,
			home_path=home_path,
			role_name=r, top_role=True,
			create_role=True,
			remainder_args=remainder)
		m = self.input()
		if not isinstance(m, kj.Returned):
			return kj.Faulted(cannot_add, f'unexpected process response {m}')

		if isinstance(m.message, kj.Faulted):
			return m.message

		if not isinstance(m.message, kj.CommandResponse):
			t = kj.message_to_tag(m.message)
			return kj.Faulted(cannot_add, f'unexpected command response {t}')

	return None

kj.bind(add)

#
#
def list_(self, search, remainder, long_listing: bool=False, group_role: bool=False, sub_roles: bool=False):
	'''List the process definition(s) in an existing store. Return Faulted/None.'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_list = f'cannot list "{home_path}"'

	home = home_listing(self, home_path, search, grouping=group_role, sub_roles=sub_roles)
	if home is None:
		return kj.Faulted(cannot_list, f'does not exist or contains unexpected/incomplete materials')

	s = ','.join(search)
	self.console('list', search=s, home_path=home_path)

	keys = sorted(home.keys())
	for k in keys:
		v = home[k]
		if long_listing:
			home_role = os.path.join(home_path, 'role', k)
			m, _ = kj.storage_manifest(home_role)
			print(f'{k:24} {v.executable_file()} {m.manifests}/{m.listings}/{m.bytes}')
			continue
		print(k)

	return None

kj.bind(list_)

#
#
def update(self, search, remainder):
	'''Update details of existing process definition(s). Return Faulted/None.'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)
	group_role = True
	sub_roles = True

	cannot_update = f'cannot update "{home_path}"'

	home = home_listing(self, home_path, search, grouping=group_role, sub_roles=sub_roles)
	if home is None:
		return kj.Faulted(cannot_update, f'does not exist or contains unexpected/incomplete materials')

	r = ','.join(home.keys())
	self.console('update', roles=r, home_path=home_path)

	for k, v in home.items():
		a = self.create(kj.ProcessObject, v,
			origin=kj.ProcessOrigin.RUN,
			home_path=home_path,
			role_name=k, top_role=True,
			update_role=True,
			remainder_args=remainder)
		m = self.input()
		if not isinstance(m, kj.Returned):
			return kj.Faulted(cannot_update, f'unexpected process response {m}')

		if isinstance(m.message, kj.Faulted):
			return m.message

		if not isinstance(m.message, kj.CommandResponse):
			t = kj.message_to_tag(m.message)
			return kj.Faulted(cannot_update, f'not a proper command response {t}')

	return None

kj.bind(update)

#
#
def delete(self, search, remainder, all_roles: bool=False):
	'''Delete existing process definition(s). Return Faulted/None.'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_delete = f'cannot delete from "{home_path}"'
	if search:
		home = home_listing(self, home_path, search)
	elif all_roles:
		home = kj.open_home(home_path)
		if home is None:
			return kj.Faulted(cannot_delete, f'does not exist or unexpected/incomplete materials')
	else:
		return kj.Faulted(cannot_delete, f'no roles specified, use --all_roles?')

	self.console('delete', search=search, home_path=home_path)

	try:
		running = home_running(self, home)
		if running:
			r = ','.join(running.keys())
			return kj.Faulted(cannot_delete, f'roles "{r}" are currently running')

	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	try:
		role_path = os.path.join(home_path, 'role')
		for p in os.listdir(role_path):
			if p.startswith('group'):
				continue
			s = p.split('.')
			if s[0] not in home:
				continue
			home_role = os.path.join(role_path, p)
			kj.remove_folder(home_role)
	except FileNotFoundError as e:
		return kj.Faulted(cannot_delete, str(e))

	return None

kj.bind(delete)

#
#
def destroy(self, word, remainder):
	'''Remove all trace of an existing store. Return Faulted/None.'''
	home_path = word_i(word, 0) or kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_destroy = f'cannot destroy "{home_path}"'

	# Most basic checks.
	if os.path.isfile(home_path):
		return kj.Faulted(cannot_destroy, f'existing file')

	elif not os.path.isdir(home_path):
		return kj.Faulted(cannot_destroy, f'not a folder')

	# Need valid contents to be able to check
	# process status.
	home = kj.open_home(home_path)
	if home is None:
		return kj.Faulted(cannot_destroy, f'does not exist or unexpected/incomplete materials')

	self.console('destroy', home_path=home_path)

	try:
		running = home_running(self, home)
		if not running:
			kj.remove_folder(home_path)
	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	if running:
		r = ','.join(running.keys())
		return kj.Faulted(cannot_destroy, f'running roles "{r}"')

	return None

kj.bind(destroy)

#
#
def run(self, search, remainder, main_role: str=None):
	'''Execute a subset/all of the process definition(s), to completion. Return Faulted/None.'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_run = f'cannot run "{home_path}"'
	if search:
		home = home_listing(self, home_path, search)
	else:
		home = kj.open_home(home_path)
		if not home:
			return kj.Faulted(cannot_run, f'does not exist or unexpected/incomplete materials')

	s = ','.join(search)
	self.console('run', search=s, home_path=home_path)

	try:
		kv = {}
		if main_role is not None:
			kv['main_role'] = main_role

		running = home_running(self, home)
		if not running:
			a = self.create(kj.ProcessObject, GROUP_EXECUTABLE, *search,
				home_path=home_path,
				role_name=GROUP_ROLE, top_role=True,
				origin=kj.ProcessOrigin.RUN,
				**kv)
			self.assign(a, 0)
			m = self.input()
			if isinstance(m, kj.Returned):
				self.debrief()
				return m.message
			elif isinstance(m, kj.Faulted):
				return m
			elif isinstance(m, kj.Stop):
				return kj.Aborted()

	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	if running:
		r = ','.join(running.keys())
		return kj.Faulted(cannot_run, f'roles "{r}" are already running')

	return None

kj.bind(run)

#
#
def start(self, search, remainder, main_role: str=None):
	'''Start a subset/all of the process definition(s) as background daemons. Return Faulted/None (immediately).'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_start = f'cannot start "{home_path}"'
	if search:
		home = home_listing(self, home_path, search)
	else:
		home = kj.open_home(home_path)
		if home is None:
			return kj.Faulted(cannot_start, f'does not exist or unexpected/incomplete materials')

	if not home:
		return kj.Faulted(cannot_start, f'empty')

	s = ','.join(search)
	self.console('start', search=s, home_path=home_path)

	try:
		kv = {}
		if main_role is not None:
			kv['main_role'] = main_role

		running = home_running(self, home)
		if not running:
			a = self.create(kj.ProcessObject, GROUP_EXECUTABLE, *search,
				home_path=home_path,
				role_name=GROUP_ROLE, top_role=True,
				origin=kj.ProcessOrigin.START,
				**kv)
			self.assign(a, 0)
			m = self.input()
			if isinstance(m, kj.Returned):
				self.debrief()
				if not isinstance(m.message, kj.CommandResponse):
					return kj.Faulted(cannot_start, f'unexpected response from group')
				return None
			elif isinstance(m, kj.Faulted):
				return m
			elif isinstance(m, kj.Stop):
				return kj.Aborted()

	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	if running:
		r = ','.join(running.keys())
		return kj.Faulted(cannot_start, f'roles "{r}" are already running')

	return None

kj.bind(start)

#
#
def stop(self, search, remainder):
	'''Stop the previously started set of background daemons. Return Faulted/None (immediately).'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_stop = f'cannot stop "{home_path}"'
	home = kj.open_home(home_path)
	if home is None:
		return kj.Faulted(cannot_stop, f'does not exist or unexpected/incomplete materials')

	if not home:
		return kj.Faulted(cannot_stop, f'empty')

	self.console('stop', home_path=home_path)

	try:
		running = home_running(self, home)
		if not running:
			return kj.Faulted(cannot_stop, f'nothing running')
		parent_pid = set()

		for k, v in running.items():
			parent_pid.add(v.parent_pid)

		for p in parent_pid:
			os.kill(p, signal.SIGINT)

	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	return None

kj.bind(stop)

#
#
def status(self, search, remainder, long_listing: bool=False, group_role: bool=False, sub_roles: bool=False):
	'''Query running/not-running status of background daemons. Return Faulted/None.'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_status = f'cannot query status "{home_path}"'

	# Get list of roles at home_path, trimmed down
	# according to the list of search patterns.
	home = home_listing(self, home_path, search, grouping=group_role, sub_roles=sub_roles)
	if home is None:
		return kj.Faulted(cannot_status, f'does not exist or unexpected/incomplete materials')

	if not home:
		return kj.Faulted(cannot_status, f'empty')

	s = ','.join(search)
	self.console('status', search=s, home_path=home_path)

	try:
		# Determine the running/idle status of the
		# selected roles.
		running = home_running(self, home)
		if not running:
			return kj.Faulted(cannot_status, f'nothing running')

	finally:
		# Cleanup the locking from inside home_running().
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	now = datetime.datetime.now(kj.UTC)
	orderly = sorted(running.keys())

	def long_status():
		for k in orderly:
			v = home.get(k, None)
			r = running.get(k, None)

			start_stop = v.start_stop()
			s = start_stop[-1]
			if s.start is not None:
				d = now - s.start
				s = short_delta(d)
			else:
				s = '(never started)'

			def dq(pid):
				if pid is None:
					return '0'
				return f'{pid}'
			kj.output_line('%-24s <%s> %s' % (k, dq(r.pid), s))

	def short_status():
		for k in orderly:
			kj.output_line(k)

	if long_listing:
		long_status()
	else:
		short_status()

	return None

kj.bind(status)

#
#
def history(self, word, remainder, long_listing: bool=False):
	'''List the the start/stop record for the specified role. Return Faulted/None.'''
	role_name = word_i(word, 0) or kj.CL.role_name
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	group_role = True
	sub_roles = True

	if role_name is None:
		return kj.Faulted(f'cannot pull history', f'no role specified')
	cannot_history = f'cannot pull history for "{role_name}"'

	home = kj.open_home(home_path, grouping=group_role, sub_roles=sub_roles)
	if home is None:
		return kj.Faulted(cannot_history, f'home at "{home_path}" does not exist or contains unexpected/incomplete materials')

	role = home.get(role_name, None)
	if role is None:
		return kj.Faulted(cannot_history, f'does not exist')

	self.console('history', role_name=role_name, home_path=home_path)

	def long_history():
		now = datetime.datetime.now(kj.UTC)
		for s in role.start_stop():
			start = kj.world_to_text(s.start)
			if s.stop is None:
				kj.output_line('%s ... ?' % (start,))
				continue
			stop = kj.world_to_text(s.stop)
			d = s.stop - s.start
			span = '%s' % (kj.short_delta(d),)
			if isinstance(s.returned, kj.Incognito):
				kj.output_line('%s ... %s (%s) %s' % (start, stop, span, s.returned.type_name))
			else:
				kj.output_line('%s ... %s (%s) %s' % (start, stop, span, s.returned.__class__.__name__))

	def short_history():
		for i, s in enumerate(role.start_stop()):
			now = datetime.datetime.now(kj.UTC)
			d = now - s.start
			start = '%s ago' % (kj.short_delta(d),)
			if s.stop is None:
				kj.output_line('[%d] %s ... ?' % (i, start))
				continue
			d = s.stop - s.start
			stop = kj.short_delta(d)
			if isinstance(s.returned, kj.Incognito):
				kj.output_line('[%d] %s ... %s (%s)' % (i, start, stop, s.returned.type_name))
			else:
				kj.output_line('[%d] %s ... %s (%s)' % (i, start, stop, s.returned.__class__.__name__))

	if long_listing:
		long_history()
	else:
		short_history()
	return None

kj.bind(history)

#
#
class NoFault(object):
	def __init__(self, fault: kj.Any=None):
		self.fault = fault

kj.bind(NoFault)

def returned(self, word, remainder, start: int=None, timeout: float=None):
	'''Print a specific termination value for the specified role. Return Faulted/None.'''
	role_name = word_i(word, 0) or kj.CL.role_name
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	group_role = True
	sub_roles = True

	if role_name is None and group_role:
		role_name = GROUP_ROLE

	if role_name is None:
		return kj.Faulted(f'cannot pull return', f'no role specified')
	cannot_returned = f'cannot pull return for "{role_name}"'

	home = kj.open_home(home_path, grouping=group_role, sub_roles=sub_roles)
	if home is None:
		return kj.Faulted(cannot_returned, f'home at "{home_path}" does not exist or contains unexpected/incomplete materials')

	role = home.get(role_name, None)
	if role is None:
		return kj.Faulted(cannot_returned, f'does not exist')

	self.console('returned', role_name=role_name, home_path=home_path)

	start_stop = role.start_stop()
	if len(start_stop) < 1:
		return kj.Faulted(cannot_returned, f'no start/stop records')

	ls = len(start_stop) - 1	# Last stop
	if start is None:
		start = ls
	elif start < 0:
		start = ls + 1 + start

	if start < 0 or start > ls:
		return kj.Faulted(cannot_returned, f'start [{start}] out of bounds')

	# Criteria met - valid row in the table.
	selected = start_stop[start]
	anchor = selected.start

	def no_fault(value):
		if isinstance(value, kj.Faulted):
			return NoFault(value)
		return selected.returned

	# This row has already returned.
	if selected.stop is not None:
		return no_fault(selected.returned)

	# Cannot poll for completion of anything other
	# than the last row.
	if start != ls:
		return kj.Faulted(cannot_returned, f'no record of role[{start}] stopping and never will be')

	if timeout is not None:
		self.start(kj.T1, timeout)

	self.start(kj.T2, 1.0)
	while True:
		m, i = self.select(kj.Stop, kj.T1, kj.T2)
		if isinstance(m, kj.Stop):
			break
		elif isinstance(m, kj.T1):
			return kj.TimedOut(m)
		elif isinstance(m, kj.T2):
			r = role.start_stop.resume()
			if len(r) < start:
				return kj.Faulted(cannot_returned, f'lost original start position')
			if r[start].start != anchor:
				return kj.Faulted(cannot_returned, f'lost original start position, datetime anchor')
			if r[start].stop is not None:
				return no_fault(r[start].returned)
			self.start(kj.T2, 1.0)

	return None

kj.bind(returned)

#
#
# Extraction of logs for a role.
#
class TimeFrame(Enum):
	"""
	Enumeration of a general-usage time unit.

	* MONTH - 4 weeks
	* WEEK - 7 days
	* DAY - 24 hours
	* HOUR - 60 minutes
	* MINUTE - 60 seconds
	* HALF - 30 minutes
	* QUARTER - 15 minutes
	* TEN - 10 minutes
	* FIVE - 5 minutes
	"""
	MONTH=0
	WEEK=1
	DAY=2
	HOUR=3
	MINUTE=4
	HALF=5
	QUARTER=6
	TEN=7
	FIVE=8

def log(self, word, remainder, clock: bool=False,
	tail: int=None, from_: str=None, last: TimeFrame=None, start: int=None, back=None,
	to: str=None, span=None, count: int=None, sample: str=None, tags: str=None):
	'''List logging records for the specified process definition. Return Faulted/None.'''
	role_name = word_i(word, 0) or kj.CL.role_name
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	group_role = True
	sub_roles = True

	if role_name is None:
		return kj.Faulted(f'cannot log', f'no role specified')
	cannot_log = f'cannot log "{role_name}"'

	self.console('log', role_name=role_name, home_path=home_path)

	# Need a beginning and an ending.
	f = [
		tail,		# Rewind up to a specified number of lines.
		from_,		# At a specific datetime.
		last,		# Recent timeframe.
		start,		# Entry in the start-stop log.
		back		# Timespan back from now.
	]
	c = len(f) - f.count(None)
	if c == 0:
		tail = os.get_terminal_size().lines - 2
	elif c != 1:
		# one of <tail>, <from>, <last>, <start> or <back> is required
		return kj.Faulted(cannot_log, f'need one of tail, from_, last, start or back')

	# The ending (optional).
	t = [
		to,			# Specific datetime.
		span,		# Timespan from start.
		count		# Number of lines from start.
	]
	c = len(t) - t.count(None)
	if c == 0:
		pass		# Default is query to end-of-log.
	elif c != 1:
		# one of <to>, <span> or <count> is required
		return kj.Faulted(cannot_log, f'optional use of to, span or count')

	# Open the home and role.
	home = kj.open_home(home_path, grouping=group_role, sub_roles=sub_roles)
	if home is None:
		return kj.Faulted(cannot_log, f'home at "{home_path}" does not exist or contains unexpected/incomplete materials')

	role = home.get(role_name, None)
	if role is None:
		return kj.Faulted(cannot_log, f'does not exist')

	# Calculate the start position and then the
	# end position - might be relative to start.
	begin, end = None, None
	if tail is not None:
		if tail < 1:
			return kj.Faulted(cannot_log, f'tail [{tail}] out of range')

	elif from_ is not None:
		begin = world_or_clock(from_, clock)

	elif last is not None:
		begin = from_last(last)
		if begin is None:
			return kj.Faulted(cannot_log, f'last is not a TimeFrame')

	elif start is not None:
		start_stop = role.start_stop()
		if len(start_stop) < 1:
			return kj.Faulted(cannot_log, f'no history available')
		if start < 0:
			y = len(start_stop) + start
		else:
			y = start
		try:
			s = start_stop[y]
		except IndexError:
			return kj.Faulted(cannot_log, f'start [{y} out of range]')
		begin = s.start
		p1 = y + 1
		if p1 < len(start_stop):
			end = start_stop[p1].start
		else:
			end = None
	elif back is not None:
		d = datetime.datetime.now(kj.UTC)
		t = datetime.timedelta(seconds=back)
		begin = d - t

	# Calculate the end.
	if to is not None:
		end = world_or_clock(to, clock)
	elif span is not None:
		#t = datetime.timedelta(seconds=span)
		if begin is None:
			return kj.Faulted(cannot_log, f'span has nowhere to start')
		end = begin + span

	# Now that <begin>(or tail) and <end> have been established, a
	# few more sanity checks.
	if begin is None and tail is None:
		return kj.Faulted(cannot_log, f'<begin> not defined and not inferred')

	if begin is not None and end is not None and end < begin:
		return kj.Faulted(cannot_log, f'<end> comes before <begin>')

	if sample is not None and tags is not None:
		return kj.Faulted(cannot_log, f'sampling is by a specific tag')

	# Boundaries are set. Ready to scan.
	if sample:
		a = self.create(sampler, role, clock, begin, tail, end, count, sample)
	else:
		a = self.create(printer, role, clock, begin, tail, end, count, tags)

	m, i = self.select(kj.Stop, kj.Returned)
	if isinstance(m, kj.Stop):
		kj.halt(a)
		m, i = self.select(kj.Returned)
		return kj.Aborted()

	message = m.message
	if message is None:   # Reached the end.
		pass
	elif isinstance(message, kj.Faulted):	 # kj.Failed to complete stream.
		return message
	else:
		return kj.Faulted(cannot_log, f'unexpected reader response')

	return None

kj.bind(log, span=kj.TimeSpan(), back=kj.TimeSpan())

#
#
def edit(self, word, remainder):
	'''Edit the configuration of the specified process defintion. Return Faulted/None.'''
	role_name = word_i(word, 0) or kj.CL.role_name
	home_path = word_i(word, 1) or kj.CL.home_path or kj.DEFAULT_HOME
	group_role = True
	sub_roles = True

	if role_name is None:
		return kj.Faulted(f'cannot edit "{home_path}"', f'no role specified')

	cannot_edit = f'cannot edit "{role_name}"'

	home = kj.open_home(home_path, grouping=group_role, sub_roles=sub_roles)
	if home is None:
		return kj.Faulted(cannot_edit, f'does not exist or contains unexpected/incomplete materials')

	try:
		running = home_running(self, home)
		if role_name in running:
			return kj.Faulted(cannot_edit, f'role is running')

	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	r = home.get(role_name, None)
	if r is None:
		return kj.Faulted(cannot_edit, f'does not exist')

	self.console('edit', role_name=role_name, home_path=home_path)

	output = kj.HR.edit_role(self, r)
	return output

kj.bind(edit)

#
#
def print_scope(s):
	s = str(s)
	i = s.rfind('.')
	return s[i + 1:]

def print_id(uid, full_identity=False):
	s = str(uid)
	if full_identity:
		return s
	return s[:8]

#
#
def print_network(self, d, ipp, full_identity=False, directory_addresses=False, tab=0,
		list_published=False, list_subscribed=False, list_routed=False, list_connected=False):

	#kj.output_line(f'scope={d.scope}, unique_id={d.unique_id}, subs={len(d.sub_directory)}')
	#for k, v in d.sub_directory.items():
	#	kj.output_line(f'k={k}, v={v}')

	i = print_id(d.unique_id, full_identity=full_identity)
	s = print_scope(d.scope)
	a = str(ipp)

	if directory_addresses:
		kj.output_line(f'[{s}] {d.executable} ({i}) {d.primary_ip} <C>{d.connect_to_directory} <L>{d.accept_directories_at}', tab=tab)
	else:
		kj.output_line(f'[{s}] {d.executable} ({i})', tab=tab)

	if list_published:
		for p in d.published:
			t = print_id(p.published_id, full_identity=full_identity)
			ipp = p.listening_ipp
			if ipp and ipp.host:
				kj.output_line(f'# "{p.name}" ({t}) {p.listening_ipp}', tab=tab+1)
			else:
				kj.output_line(f'# "{p.name}" ({t})', tab=tab+1)

	if list_subscribed:
		for s in d.subscribed:
			t = print_id(s.subscribed_id, full_identity=full_identity)
			kj.output_line(f'? "{s.search}" ({t})', tab=tab+1)

	if list_routed:
		for r in d.routed:
			a = print_id(r.subscribed_id, full_identity=full_identity)
			b = print_id(r.published_id, full_identity=full_identity)
			kj.output_line(f'<>" {r.name}" ({a} -> {b})', tab=tab+1)

	if list_connected:
		for subscribed_id, dc in d.peer.items():
			a = print_id(subscribed_id, full_identity=full_identity)
			kj.output_line(f'? "{dc.search}" ({a})', tab=tab+1)
			for ds in dc.session:
				route = ds.route
				scope = print_scope(route.scope)
				if route is None:
					kj.output_line(f'> "{ds.name}" (no active route)', tab=tab+2)
				elif isinstance(route, od.RouteOverLoop):
					if isinstance(ds.status, kj.Connected):
						requested_ipp = ds.status.request.requested_ipp
						opened_ipp = ds.status.opened_ipp
						kj.output_line(f'> "{ds.name}"[{scope}] ({opened_ipp} -> {requested_ipp})', tab=tab+2)
					elif isinstance(ds.status, kj.Faulted):
						kj.output_line(f'"{ds.name}"[{scope}] {route.ipp} ({ds.status})', tab=tab+2)
					else:
						tag = kj.message_to_tag(ds.status)
						kj.output_line(f'> "{ds.name}"[{scope}] {route.ipp} (unexpected "{tag}")', tab=tab+2)
				elif isinstance(route, od.RouteToAddress):
					pi = print_id(route.published_id, full_identity=full_identity)
					si = print_id(route.subscribed_id, full_identity=full_identity)
					kj.output_line(f'> "{ds.name}"[{scope}] ({si} -> {pi})', tab=tab+2)

	for k, v in d.sub_directory.items():
		self.send(od.GetDirectory(), v)
		m = self.input()
		if isinstance(m, od.DirectoryListing):
			print_network(self, m, k, full_identity=full_identity, directory_addresses=directory_addresses, tab=tab+1,
				list_published=list_published, list_subscribed=list_subscribed, list_routed=list_routed, list_connected=list_connected)
		elif isinstance(m, kj.Faulted):
			return m
		elif isinstance(m, kj.Stop):
			return kj.Aborted()

	return None

def network(self, word, remainder, open_scope: kj.ScopeOfDirectory=None, full_identity: bool=False, directory_addresses: bool=False,
		list_published: bool=False, list_subscribed: bool=False, list_routed: bool=False, list_connected: bool=False):
	'''. Return Faulted/None.'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME

	if home_path is None:
		return kj.Faulted(f'cannot edit "{home_path}"', f'no role specified')
	open_scope = open_scope or kj.ScopeOfDirectory.HOST

	# Check for connected directory.
	self.send(od.OpenDirectory(scope=open_scope), pd.PD.directory)
	self.start(kj.T1, 30.0)
	while True:
		m = self.input()
		if isinstance(m, od.DirectoryOpened):
			break
		elif isinstance(m, kj.Faulted):
			return m
		elif isinstance(m, kj.T1):
			return kj.TimedOut(m)
		elif isinstance(m, kj.Stop):
			return kj.Aborted()

	# Directory is connected to something. Query
	# for the whole tree.
	self.send(od.ListDirectory(), pd.PD.directory)
	self.start(kj.T2, 10.0)

	m = self.input()
	if isinstance(m, od.DirectoryListing):
		output = print_network(self, m, 'root',
			full_identity=full_identity, directory_addresses=directory_addresses,
			list_published=list_published, list_subscribed=list_subscribed,
			list_routed=list_routed, list_connected=list_connected)
	elif isinstance(m, kj.Faulted):
		return m
	elif isinstance(m, kj.T2):
		return kj.TimedOut(m)
	elif isinstance(m, kj.Stop):
		return kj.Aborted()

	return output

kj.bind(network)

#
#
def find_name(self, d, name):
	s = str(d.unique_id)
	if s.startswith(name):
		return d

	for p in d.published:
		t = str(p.published_id)
		if t.startswith(name):
			return p.published_id

	for s in d.subscribed:
		t = str(s.subscribed_id)
		if t.startswith(name):
			return s.subscribed_id

	for k, v in d.sub_directory.items():
		self.send(od.GetDirectory(), v)
		m = self.input()
		if isinstance(m, od.DirectoryListing):
			f = find_name(self, m, name)
			if f:
				return f
		elif isinstance(m, kj.Faulted):
			return m
		elif isinstance(m, kj.Stop):
			return kj.Aborted()

	return None

def ping(self, word, remainder, open_scope: kj.ScopeOfDirectory=None, ping_count: int=4):
	'''. Return Faulted/None.'''
	name = word_i(word, 0)

	if name is None:
		return kj.Faulted(f'cannot ping', f'no identity specified')
	open_scope = open_scope or kj.ScopeOfDirectory.HOST

	# Check for connected directory.
	self.send(od.OpenDirectory(scope=open_scope), pd.PD.directory)
	self.start(kj.T1, 30.0)
	while True:
		m = self.input()
		if isinstance(m, od.DirectoryOpened):
			break
		elif isinstance(m, kj.Faulted):
			return m
		elif isinstance(m, kj.T1):
			return kj.TimedOut(m)
		elif isinstance(m, kj.Stop):
			return kj.Aborted()

	# Directory is connected to something. Query
	# for the whole tree.
	self.send(od.ListDirectory(), pd.PD.directory)
	self.start(kj.T2, 10.0)
	while True:
		m = self.input()
		if isinstance(m, od.DirectoryListing):
			break
		elif isinstance(m, kj.Faulted):
			return m
		elif isinstance(m, kj.T2):
			return kj.TimedOut(m)
		elif isinstance(m, kj.Stop):
			return kj.Aborted()

	d = find_name(self, m, name)
	if d is None:
		return kj.Faulted(f'cannot ping "{name}"', f'not present in directory')
	elif isinstance(d, uuid.UUID):
		return kj.Faulted(f'cannot ping "{name}"', f'not a directory node')
	elif isinstance(d, od.DirectoryListing):
		pass
	else:
		return kj.Faulted(f'cannot ping "{name}"', f'unexpected object')

	for i in range(ping_count):
		if i:
			self.start(kj.T2, 1.0)

			m = self.input()
			if isinstance(m, kj.T2):
				pass
			elif isinstance(m, kj.Stop):
				return kj.Aborted()

		kj.output_line(f'[{i}] ... ', newline=False)

		b = kj.clock_now()
		self.send(kj.Ping(), d.directory_address)
		self.start(kj.T1, 3.0)

		m = self.input()
		if isinstance(m, kj.Ping):
			e = kj.clock_now()
			t = e - b
			t = kj.span_to_text(t)
			kj.output_line(f'{t}')
		elif isinstance(m, kj.T1):
			kj.output_line(f'(timed out)')
		elif isinstance(m, kj.Stop):
			return kj.Aborted()

	output = None
	return output

kj.bind(ping)

#
#
def list_folder(path, recursive_listing):
	for s in os.listdir(path):
		p = os.path.join(path, s)
		if os.path.isdir(p):
			yield p
			if recursive_listing:
				yield from list_folder(p, True)
		elif os.path.isfile(p):
			yield p

def get_printer(target_path, full_path, long_listing):
	if full_path:
		if long_listing:
			def printer(path):
				st = os.stat(path)
				fm = stat.filemode(st.st_mode)
				print(f'{fm} {st.st_uid}/{st.st_gid} {path}')
		else:
			def printer(path):
				print(path)
	else:
		h = len(target_path)
		if long_listing:
			def printer(path):
				st = os.stat(path)
				fm = stat.filemode(st.st_mode)
				hd = path[h + 1:]
				print(f'{fm} {st.st_uid}/{st.st_gid} {hd}')
		else:
			def printer(path):
				hd = path[h + 1:]
				print(hd)
	return printer

def resource(self, word, remainder,
		full_path: bool=False, recursive_listing: bool=False, long_listing: bool=False,
		make_changes: bool=False, clear_all: bool=False):
	'''.'''
	if not word:
		return kj.Faulted(f'cannot resource group', f'no executable specified')

	executable = word[0]
	word = word[1:]
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_resource = f'cannot resource "{executable}"'

	home = kj.open_home(home_path, grouping=True, sub_roles=True)
	if home is None:
		return kj.Faulted(cannot_resource, f'does not exist or contains unexpected/incomplete materials')

	def matching(executable_file):
		s = os.path.split(executable_file)
		return s[1] == executable

	role_matching = {k: v for k, v in home.items() if matching(v.executable_file())}

	try:
		running = home_running(self, role_matching)
		n = len(running)
		if n > 1:
			r = ','.join(running.keys())
			return kj.Faulted(cannot_resource, f'roles "{r}" are running')
		elif n == 1:
			r = next(iter(running.keys()))
			return kj.Faulted(cannot_resource, f'role "{r}" is running')

	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	try:
		resource_path = kj.CL.resource_path
		target_path = os.path.join(home_path, 'resource', executable)
		if not os.path.isdir(target_path):
			return kj.Faulted(cannot_resource, f'folder "{target_path}" does not exist')

		if not word:
			if resource_path:
				source_storage, _ = kj.storage_manifest(resource_path)
				target_storage, _ = kj.storage_manifest(target_path)
			elif clear_all:
				kj.remove_contents(target_path)
				return None
			else:
				printer = get_printer(target_path, full_path, long_listing)
				for r in list_folder(target_path, recursive_listing):
					printer(r)
				return None
		else:
			if resource_path or clear_all or full_path or recursive_listing:
				return kj.Faulted(cannot_resource, 'inappropriate argument(s)')
			source_storage, _ = kj.storage_selection(word, path=os.getcwd())
			target_storage, _ = kj.storage_manifest(target_path)

		storage_delta = [d for d in kj.storage_delta(source_storage, target_storage)]

		if not storage_delta:			# Nothing to see or do.
			return None

		if not make_changes:			# Without explicit command, show what would happen.
			for d in storage_delta:
				print(d)
			return None

		a = self.create(kj.FolderTransfer, storage_delta, target_storage.path)

		m, _ = self.select(kj.Returned, kj.Stop)
		if isinstance(m, kj.Stop):
			self.send(m, a)
			m, _ = self.select(kj.Returned)
			return kj.Aborted()

	except (OSError, ValueError) as e:
		return kj.Faulted(cannot_resource, str(e))

	message = m.message
	if isinstance(message, kj.Faulted):
		return message
	return None

kj.bind(resource)

#
#
def model(self, word, remainder,
		full_path: bool=False, recursive_listing: bool=False, long_listing: bool=False,
		make_changes: bool=False, clear_all: bool=False,
		get_latest: str=None):
	'''.'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_model = f'cannot model "{home_path}"'

	if not word:
		return kj.Faulted(cannot_model, f'no role specified')
	role = word[0]
	word = word[1:]

	cannot_model = f'cannot model "{role}"'

	home = kj.open_home(home_path, grouping=True, sub_roles=True)
	if home is None:
		return kj.Faulted(cannot_model, f'does not exist or contains unexpected/incomplete materials')

	# Can match only 1. Keep consistent code
	# layout for status checks.
	def matching(k):
		return k == role

	role_matching = {k: v for k, v in home.items() if matching(k)}

	if not role_matching:
		return kj.Faulted(cannot_model, f'unknown role')

	model_path = kj.CL.model_path
	try:
		running = home_running(self, role_matching)
		n = len(running)
		if word or model_path or clear_all or make_changes:
			if n > 1:
				r = ','.join(running.keys())
				return kj.Faulted(cannot_model, f'roles "{r}" are running')
			elif n == 1:
				r = next(iter(running.keys()))
				return kj.Faulted(cannot_model, f'role "{r}" is running')

	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	if model_path or clear_all or full_path or recursive_listing:
		return kj.Faulted(cannot_model, 'inappropriate argument(s)')

	try:
		target_path = os.path.join(home_path, 'role', role, 'model')
		if not os.path.isdir(target_path):
			return kj.Faulted(cannot_model, f'role model folder is not usable')

		if not word:
			if model_path:
				# Folder-based asset management.
				model_path = os.path.abspath(model_path)
				if not os.path.isdir(model_path):
					return kj.Faulted(cannot_model, f'path "{model_path}" is not a usable folder')

				source_storage, _ = kj.storage_manifest(model_path)
				target_storage, _ = kj.storage_manifest(target_path)

			elif get_latest:
				# Retrieve assets from the role.
				get_latest = os.path.abspath(get_latest)
				if not os.path.exists(get_latest):
					kj.Folder(get_latest)
				elif not os.path.isdir(get_latest):
					return kj.Faulted(cannot_model, f'path "{get_latest}" is not a usable folder')

				source_storage, _ = kj.storage_manifest(target_path)
				target_storage, _ = kj.storage_manifest(get_latest)

			elif clear_all:
				kj.remove_contents(target_path)
				return None
			else:
				printer = get_printer(target_path, full_path, long_listing)
				for r in list_folder(target_path, recursive_listing):
					printer(r)
				return None
		else:
			if get_latest:
				get_latest = os.path.abspath(get_latest)
				if not os.path.exists(get_latest):
					kj.Folder(get_latest)
				elif not os.path.isdir(get_latest):
					return kj.Faulted(cannot_model, f'path "{get_latest}" is not a usable folder')

				source_storage, _ = kj.storage_manifest(target_path)
				target_storage, _ = kj.storage_selection(word, path=get_latest)
			else:
				source_storage, _ = kj.storage_selection(word)
				target_storage, _ = kj.storage_manifest(target_path)

		storage_delta = [d for d in kj.storage_delta(source_storage, target_storage)]

		if not storage_delta:			# Nothing to see or do.
			return None

		if not make_changes:			# Without explicit command, show what would happen.
			for d in storage_delta:
				print(d)
			return None

		a = self.create(kj.FolderTransfer, storage_delta, target_storage.path)

		m, _ = self.select(kj.Returned, kj.Stop)
		if isinstance(m, kj.Stop):
			self.send(m, a)
			m, _ = self.select(kj.Returned)
			return kj.Aborted()

	except (OSError, ValueError) as e:
		return kj.Faulted(cannot_model, str(e))

	message = m.message
	if isinstance(message, kj.Faulted):
		return message
	return None

kj.bind(model)

#
#
def script(self, word, remainder,
		full_path: bool=False, recursive_listing: bool=False, long_listing: bool=False,
		list_scripts: bool=False, list_executables: bool=False, list_paths: bool=False,
		make_changes: bool=False, clear_all: bool=False):
	'''.'''
	home_path = kj.CL.home_path or kj.DEFAULT_HOME
	home_path = os.path.abspath(home_path)

	cannot_script = f'cannot script "{home_path}"'

	home = kj.open_home(home_path, grouping=True, sub_roles=True)
	if home is None:
		return kj.Faulted(cannot_script, f'does not exist or contains unexpected/incomplete materials')

	try:
		running = home_running(self, home)
		n = len(running)
		if n and (clear_all or make_changes):
			r = ','.join(running.keys())
			return kj.Faulted(cannot_script, f'roles "{r}" are running')

	finally:
		self.abort()
		while self.working():
			m, i = self.select(kj.Returned)
			self.debrief()

	# Get all executable for every role, then refine that to a map of
	# unique paths, i.e. where each python module comes from.
	role_executable = {k: v.executable_file() for k, v in home.items()}
	source_path = {os.path.split(v)[0] for k, v in role_executable.items() if v.endswith('.py')}

	if not source_path:
		return kj.Faulted(cannot_script, f'no scripts in use')

	# Combine the file and folder names from each unique path into
	# a single collection.
	selection = []
	collision = []
	for p in source_path:
		for s in os.listdir(p):
			# Need special handling of "library" module. Allow
			# the first one through. If present at this level its
			# intended that they are all empty.
			if s == '__init__.py':
				if s in selection:
					continue
			elif s.startswith('__') and s.endswith('__'):
				# Skip any other special python materials, e.g. cache.
				continue
			elif s in selection:
				collision.append(s)
				continue
			t = os.path.join(p, s)
			selection.append(t)

	if collision:
		c = ','.join(collision)
		return kj.Faulted(cannot_script, f'duplicated names "{c}"')

	try:
		target_path = os.path.join(home_path, 'script')

		listing = list_scripts or list_executables or list_paths
		if not listing and not clear_all:
			if full_path or long_listing or recursive_listing:
				return kj.Faulted(cannot_script, 'inappropriate argument(s)')

			source_storage, _ = kj.storage_selection(selection, path=os.getcwd())
			target_storage, _ = kj.storage_manifest(target_path)
		elif list_scripts:
			printer = get_printer(target_path, full_path, long_listing)
			for r in list_folder(target_path, recursive_listing):
				printer(r)
			return None
		elif list_executables:
			for k, v in role_executable.items():
				print(f'{k:24} {v}')
			return None
		elif list_paths:
			for s in source_path:
				print(f'{s}')
			return None
		elif clear_all:
			kj.remove_contents(target_path)
			return None

		storage_delta = [d for d in kj.storage_delta(source_storage, target_storage)]

		if not storage_delta:			# Nothing to see or do.
			return None

		if not make_changes:			# Without explicit command, show what would happen.
			for d in storage_delta:
				print(d)
			return None

		a = self.create(kj.FolderTransfer, storage_delta, target_storage.path)

		m, _ = self.select(kj.Returned, kj.Stop)
		if isinstance(m, kj.Stop):
			self.send(m, a)
			m, _ = self.select(kj.Returned)
			return kj.Aborted()

	except (OSError, ValueError) as e:
		return kj.Faulted(cannot_script, str(e))

	message = m.message
	if isinstance(message, kj.Faulted):
		return message
	return None

kj.bind(script)

# Functions supporting the
# sub-commands.
def word_i(word, i):
	'''Return the i-th element of word, if its long enough. Return element or None.'''
	if i < len(word):
		return word[i]
	return None

def home_listing(self, home_path, search, grouping=False, sub_roles=False):
	'''Load the contents of home_path and search for matching roles. Return dict[str,role] or None.'''
	home = kj.open_home(home_path, grouping=grouping, sub_roles=sub_roles)
	if home is None:
		self.complete(kj.Faulted(f'cannot list "{home_path}" (does not exist or contains unexpected/incomplete materials)'))

	# Compile all the patterns.
	machine = []
	for s in search:
		try:
			m = re.compile(s)
		except re.error as e:
			self.complete(kj.Faulted(f'cannot list "{home_path}"', str(e)))
		machine.append(m)

	# Scan for roles matching a pattern.
	if machine:
		def match(name):
			for m in machine:
				b = m.match(name)
				if b:
					return True
			return False

		home = {k: v for k, v in home.items() if match(k)}
		if not home:
			s = ', '.join(search)
			self.complete(kj.Faulted(f'cannot list "{home_path}"', f'no roles matching "{s}"'))

	return home

def home_running(self, home):
	'''Scan lock files for the given dict of roles. Return list of those that are running.'''
	running = {}
	for k, v in home.items():
		a = self.create(kj.head_lock, v.lock.path, 'head')
		self.assign(a, k)
		m, i = self.select(kj.Ready, kj.Returned)
		if isinstance(m, kj.Returned):	# Cannot lock.
			r = self.debrief()
			running[r] = m.message	# LockedOut

	return running

def world_or_clock(s, clock):
	if clock:
		t = kj.text_to_clock(s)
		d = datetime.datetime.fromtimestamp(t, tz=kj.UTC)
		return d
	return kj.text_to_world(s)

def from_last(last):
	d = datetime.datetime.now(kj.UTC)

	if last == TimeFrame.MONTH:
		f = datetime.datetime(d.year, d.month, 1, tzinfo=d.tzinfo)
	elif last == TimeFrame.WEEK:
		dow = d.weekday()
		dom = d.day - 1
		if dom >= dow:
			f = datetime.datetime(d.year, d.month, d.day - dow, tzinfo=d.tzinfo)
		elif d.month > 1:
			t = dow - dom
			r = calendar.monthrange(d.year, d.month - 1)
			f = datetime.datetime(d.year, d.month - 1, r[1] - t, tzinfo=d.tzinfo)
		else:
			t = dow - dom
			r = calendar.monthrange(d.year - 1, 12)
			f = datetime.datetime(d.year - 1, 12, r[1] - t, tzinfo=d.tzinfo)
	elif last == TimeFrame.DAY:
		f = datetime.datetime(d.year, d.month, d.day, tzinfo=d.tzinfo)
	elif last == TimeFrame.HOUR:
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, tzinfo=d.tzinfo)
	elif last == TimeFrame.MINUTE:
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=d.minute, tzinfo=d.tzinfo)
	elif last == TimeFrame.HALF:
		t = d.minute % 30
		m = d.minute - t
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=m, tzinfo=d.tzinfo)
	elif last == TimeFrame.QUARTER:
		t = d.minute % 15
		m = d.minute - t
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=m, tzinfo=d.tzinfo)
	elif last == TimeFrame.TEN:
		t = d.minute % 10
		m = d.minute - t
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=m, tzinfo=d.tzinfo)
	elif last == TimeFrame.FIVE:
		t = d.minute % 5
		m = d.minute - t
		f = datetime.datetime(d.year, d.month, d.day, hour=d.hour, minute=m, tzinfo=d.tzinfo)
	else:
		return None
	return f

def short_delta(d):

	t = kj.span_to_text(d.total_seconds())
	i = t.find('d')
	if i != -1:
		j = t.find('h')
		if j != -1:
			return t[:j + 1]
		return t[:i + 1]
	i = t.find('h')
	if i != -1:
		j = t.find('m')
		if j != -1:
			return t[:j + 1]
		return t[:i + 1]
	# Minutes or seconds only.
	i = t.find('.')
	if i != -1:
		i += 1
		j = t.find('s')
		if j != -1:
			e = j - i
			e = min(1, e)
			return t[:i + e] + 's'
		return t[:i] + 's'

#
#
def printer(self, role, clock, begin, tail, end, count, tags):
	try:
		if begin is not None:
			reader = rl.read_log(role.logs, begin, end, count)
		else:
			reader = rl.rewind_log(role.logs, tail, end, count)

		if clock:
			for d, t in reader:
				if self.halted:
					return kj.Aborted()
				if tags is not None:
					if t[24] not in tags:
						continue
				c = d.astimezone(tz=None)		   # To localtime.
				s = c.strftime('%Y-%m-%dt%H:%M:%S') # Normal part.
				f = c.strftime('%f')[:3]			# Up to milliseconds.
				h = '%s.%s' % (s, f)
				i = t.index(' ')
				kj.output_line(h, newline=False)
				kj.output_line(t[i:], newline=False)
			return

		for d, t in reader:
			if self.halted:
				return kj.Aborted()
			if tags is not None:
				if t[24] not in tags:
					continue
			kj.output_line(t, newline=False)

	except (KeyboardInterrupt, SystemExit) as e:
		raise e
	except Exception as e:
		condition = str(e)
		fault = kj.Faulted(condition)
		return fault
	return None

kj.bind(printer)

# 2025-08-09T04:49:30.553 > <0000000f>ListenConnect - Forward Xy to <00000015> (from <0000004a>)
# 2025-08-09T04:49:30.553 < <00000015>server - Received Accepted from <0000004a>
AMPERSAND_TAG = 24
OBJECT_NAME = 36
TIME_STAMP = 23

def sampler(self, role, clock, begin, tail, end, count, sample):
	try:
		if begin is not None:
			reader = rl.read_log(role.logs, begin, end, count)
		else:
			reader = rl.rewind_log(role.logs, tail, end, count)

		for d, t in reader:
			if self.halted:
				return kj.Aborted()
			# Sample log.
			if t[AMPERSAND_TAG] != '&':
				continue
			# Begining of logged text, after name and dash.
			dash = t.find(' - ', OBJECT_NAME)
			if dash == -1:
				continue
			# Name and parens.
			text = t[dash + 3:-1]
			if text[-1] != ')':
				continue
			# Separate name from values.
			left = text.find(' (')
			if left == -1:
				continue
			# Name and values.
			name = text[:left]
			if name != sample:
				continue
			parens = text[left+2:-1]
			comma = parens.split(',')
			values = [c.split('=')[1] for c in comma]
			tabs = '\t'.join(values)
			stamp = t[0:TIME_STAMP]
			if clock:
				c = d.astimezone(tz=None)			# To localtime.
				s = c.strftime('%Y-%m-%dt%H:%M:%S') # Normal part.
				f = c.strftime('%f')[:3]			# Up to milliseconds.
				stamp = '%s.%s' % (s, f)
			else:
				stamp = t[0:TIME_STAMP]

			kj.output_line(f'{stamp}\t{tabs}')
	except (KeyboardInterrupt, SystemExit) as e:
		raise e
	except Exception as e:
		condition = str(e)
		fault = kj.Faulted(condition)
		return fault
	return None

kj.bind(sampler)

#
#
table = [
	# CRUD for a set of role definitions.
	create,
	add,
	list_,
	update,
	delete,
	destroy,

	# Orchestration of the processes, i.e. executing
	# images of the role definitions.
	run,
	start,
	stop,
	status,

	# Access to records of execution.
	log,
	history,
	returned,
	edit,

	# Network administration.
	network,
	ping,

	# Software distribution.
	resource,
	model,
	script,
]

# For package scripting.
def main():
	kj.create(cli, object_table=table, strict=False)

if __name__ == '__main__':
	main()

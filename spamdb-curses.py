#!/usr/bin/env python
#
# Martin Tournoij <martin@arp242.net>
#

import curses
import locale
import os
import subprocess
import sys
import time

# Items in list
_spamdb = []

# Current selected line
_cursel = 0

# Currently selected type (white or grey)
_curtype = 'grey'


def GetSpamdb():
	"""
	Get db from spamdb(8) and put it into a nuice structure
	"""

	proc = subprocess.Popen(['spamdb'], stdout=subprocess.PIPE)
	output = proc.communicate()[0].split('\n')

	spamdb = {
		'white': [],
		'grey': [],
	}

	for line in output:
		if line.strip() == '':
			continue

		line = line.split('|')

		row = {
			'ip': line[1],
			'dns': ReverseLookup(line[1]),
			'helo': line[2],
			'from': line[3],
			'to': line[4],
			'first': time.strftime('%Y-%m-%d %H:%M', time.localtime(float(line[5]))),
			'expire': time.strftime('%Y-%m-%d %H:%M', time.localtime(float(line[6]))),
			'block': line[7],
			'pass': line[8],
		}
		spamdb[line[0].lower()].append(row)

	return spamdb

def ReverseLookup(ip):
	"""
	Reverse DNS lookup (PTR record)

	TODO: We use dig -x, I'm pretty sure there's a Python module for this :-)
	"""

	proc = subprocess.Popen(['dig', '-x', ip, '+short', '+time=1'], stdout=subprocess.PIPE)
	output = proc.communicate()[0].strip()

	return output

def Main(screen):
	"""
	"""

	global _spamdb
	global _curtype
	global _cursel

	curses.use_default_colors()
	curses.curs_set(0)

	_spamdb = GetSpamdb()
	(maxy, maxx) = screen.getmaxyx()

	mainwin = curses.newwin(maxy-5, maxx, 0, 0)
	statuswin = curses.newwin(5, maxx, maxy - 5, 0)

	# Wait for input
	while True:
		MainWindow(mainwin)
		UpdateCursor(mainwin)
		UpdateStatus(statuswin, 'Press ? for help')

		mainwin.refresh()
		statuswin.refresh()

		c = mainwin.getch()
		if c == ord('q') or c == ord('x'):
			break
		elif c == ord('w'):
			_curtype = 'white'
		elif c == ord('g'):
			_curtype = 'grey'
		elif c in (curses.KEY_DOWN, ord('j')):
			if _cursel < len(_spamdb[_curtype]) - 1:
				_cursel += 1
		elif c in (curses.KEY_UP, ord('k')):
			if _cursel > 0:
				_cursel -= 1
		elif c == ord('?'):
			HelpWindow(mainwin)
		elif c in (curses.KEY_ENTER, ord(' ')):
			DetailWindow(mainwin)
		elif _curtype == 'grey' and c == ord('W'):
			Whitelist()
		elif c == ord('D'):
			Delete()

def UpdateStatus(win, text):
	win.clear()
	win.border()

	win.addstr(0, 2, 'STATUS', curses.A_BOLD)
	win.addstr(1, 2, text)
	win.refresh()

def DetailWindow(rootwin):
	"""
	"""

	rootwinsize = rootwin.getmaxyx()

	win = curses.newwin(11, 60, 6, 6)

	win.clear()
	win.border()

	win.addstr(0, 2, 'DETAILS', curses.A_BOLD)

	i = 1
	for k, v in _spamdb[_curtype][_cursel].iteritems():
		win.addstr(i, 2, '%s %s' % (k.ljust(15), v))
		i += 1

	win.refresh()
	win.getch()
	win.erase()
	
def Whitelist():
	global _cursel

	if len(_spamdb[_curtype]) > 0:
		_spamdb['white'].append(_spamdb[_curtype][_cursel])
		del _spamdb[_curtype][_cursel]

		if _cursel > len(_spamdb[_curtype]) - 1:
			_cursel -= 1

def Delete():
	global _cursel

	if len(_spamdb[_curtype]) > 0:
		del _spamdb[_curtype][_cursel]

		if _cursel > len(_spamdb[_curtype]) - 1:
			_cursel -= 1

def MainWindow(win):
	"""
	"""

	win.clear()
	win.border()
	winsize = win.getmaxyx()

	win.addstr(0, 2, _curtype.upper(), curses.A_BOLD)
	header = '         IP                Expire             From'
	win.addstr(1, 1, '%s%s' % (header, ' ' * (winsize[1] - len(header) - 2)),
		curses.A_REVERSE)

	i = 2
	for l in _spamdb[_curtype]:
		win.addstr(i, 5,
			'%s | %s | %s' % (l['ip'].ljust(15), l['expire'], l['from']))
		i += 1

def HelpWindow(win):
	win.clear()
	win.border()
	winsize = win.getmaxyx()

	text = '''
spamdb-curses 1.0
Martin Tournoij <martin@arp242.net>
http://code.google.com/p/spamdb-curses/
Free for any use. There are no restrictions.

Keybinds:
	?\t\tThis help
	q, x\t\tExit
	Up, h\t\tMove up
	Down, j\t\tMove down
	w\t\tShow WHITE list
	g\t\tShow GREY list
	Space, Enter\tShow details
	r\t\tRefresh information from spamdb(8)
	W\t\tWhitelist selected entry
	D\t\tDelete selected entry

Also see: spamdb(8), spamd(8)

Press any key to return
'''

	win.addstr(0, 2, 'HELP', curses.A_BOLD)
	i = 0
	for line in text.split('\n'):
		win.addstr(i, 2, line)
		i += 1

	win.getch()

def UpdateCursor(win):
	"""
	"""

	win.addstr(_cursel + 2, 2, '-> ')
	win.refresh()

if __name__ == '__main__':
	try:
		curses.wrapper(Main)
	except KeyboardInterrupt:
		pass

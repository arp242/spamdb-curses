#!/usr/bin/env python

from disturils.core import setup

setup(
	name = 'spamdb-curses',
	version = '1.0',
	author = 'Martin Tournoij',
	author_email = 'martin@arp242.net',
	url = 'http://code.google.com/p/spamdb-curses/',
	scripts = glob.glob('spamdb-curses'),
)

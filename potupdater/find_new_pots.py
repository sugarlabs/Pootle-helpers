#!/usr/bin/env python
import ConfigParser
import os, os.path, sys

cfg = ConfigParser.ConfigParser()
cfg.read(sys.argv[1])

regfiles = cfg.sections()

for root, dirs, files in os.walk(os.path.join('/var/lib/pootle/checkouts', sys.argv[2])):
    for name in files:
        if name.endswith('.pot'):
            fullpath = os.path.join(root, name)
            if not fullpath in regfiles:
                print fullpath


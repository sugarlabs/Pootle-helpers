#!/usr/bin/env python

import os, sys
import os.path
from stat import *

from jToolkit import prefs
from teampagegenerator import TeamPageGenerator

users = prefs.PrefsParser('/etc/pootle/users.prefs')
pootleprefs = prefs.PrefsParser('/etc/pootle/pootle.prefs')


def walktree(top, callback):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''

    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[ST_MODE]
        if S_ISDIR(mode):
            # It's a directory, recurse into it
            walktree(pathname, callback)
        elif S_ISREG(mode):
            # It's a file, call the callback function
            callback(pathname)
        else:
            # Unknown file type, print a message
            print 'Skipping %s' % pathname

def visitfile(file):
    if file.endswith('prefs'):
        print '\n\n'
        langname = os.path.basename(os.path.dirname(file))
        fulllangname = getattr(pootleprefs.Pootle.languages, langname + '.fullname')
        print fulllangname + ':'

        f = prefs.PrefsParser(file)

        found_admin = 0
        if f.__hasattr__('rights'):
            for i in f.rights.iteritems():
                if i[1].find('admin') > -1:
                    print '\t' + getattr(users, i[0] + '.name').encode('utf-8')
                    found_admin = 1

        if found_admin == 0:
            print '\t' + 'NO ADMIN'


if __name__ == '__main__':
    walktree(sys.argv[1], visitfile)




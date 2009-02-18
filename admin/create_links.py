#!/usr/bin/env python

import os, os.path, sys

LINKDIR = '/var/lib/pootle/translations'

def make_symlink(src, dst):
    if not os.access(dst, os.F_OK):
        print ('  Linking ' + src + ' to ' + dst)
        # check if the relevant immediate toplevel directory exists
        if not os.access(os.path.dirname(dst), os.F_OK):
            os.mkdir (os.path.dirname(dst))
        s.symlink(src, dst)
        
podir = sys.argv[1]
cat = sys.argv[2]

for i in os.listdir(podir):
    if i.endswith('.pot'):
        potfile = i
		   
for k in os.listdir(podir):
    # Handle PO files
    if k.endswith('po'):
    # Tamtam has a weird PO name structure
	    if k.startswith('TamTam'):
            l = k.split('.')
            k1 = l[1] + '.' + l[2]
        src = os.path.join(podir, k)
        dst = os.path.join(LINKDIR, cat, k1.replace('.po', ''), \
            os.path.basename(os.path.dirname(podir)) + '.' + potfile.replace('.pot','') +  ".po")
        #print dst
        make_symlink(src, dst)

    # Handle POT files
    if k.endswith('pot'):
        src = os.path.join(podir, k)
        dst = os.path.join(LINKDIR, cat, 'templates', 
                    os.path.basename(os.path.dirname(podir)) + '.' + potfile.replace('.pot','') +  ".pot")
        print dst
	    make_symlink(src, dst)


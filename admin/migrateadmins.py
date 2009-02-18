#!/usr/bin/env python

# Invoke this like migrateadmins.py <oldfoo>xo_bundled <newfoo>xo_bundled

import os, os.path, shutil, sys

folder = sys.argv[1]


for i in os.listdir(folder):
    for k in os.listdir(os.path.join(folder, i)):
        if k.endswith('prefs'):
            # i here refers to the language
            src = os.path.join('/var/lib/pootle/translations/glucose', i, 'pootle-glucose-'+i+'.prefs')
            dst = os.path.join(folder, i, k)
            #print src, dst
	    try:
                shutil.copy(src, dst)
	    except IOError:
	        print src + " does not exist"
        

#!/usr/bin/env python

# Invoke this like migratepending.py <oldfoo>xo_bundled <newfoo>xo_bundled

import os, os.path, shutil, sys

src = sys.argv[1]
dst = sys.argv[2]

for i in os.listdir(src):
    for k in os.listdir(os.path.join(src, i)):
        if k.endswith('.po.pending') or k.endswith('prefs'): # We do not copy stats, since we want Pootle to regenerate them
            shutil.copy (os.path.join(src, i, k), os.path.join(dst, i))

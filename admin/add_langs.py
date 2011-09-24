#!/usr/bin/env python

import sys
import os, os.path, shutil
import subprocess
import time
from ConfigParser import ConfigParser

CODIR = '/var/lib/pootle/checkouts'
LINKDIR = '/var/lib/pootle/translations'
CONFIG = '/var/lib/pootle/maintenance/helpers/potupdater/project_list.ini'

DRYRUN = False

def pipe(command):
    print ('Running ' + command)
    proc = subprocess.Popen(args = command,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                stdin = subprocess.PIPE,
                shell=True, close_fds=True)
    (output, error) = proc.communicate()
    ret = proc.returncode
    print output, error
    return output, error, ret


projects = []
config = ConfigParser()
config.read(CONFIG)
for i in config.sections():
    projects.append(i[len(CODIR):].lstrip(os.sep).split(os.sep)[0])

for project in projects:
    project_langs_dir = os.path.join(LINKDIR, project)
    for project_lang in os.listdir(project_langs_dir):
        # List of languages
        project_po_dir = os.path.join(project_langs_dir, project_lang)
        for po_filename in os.listdir(project_po_dir):
            if po_filename.endswith('.po'):
                filepath = os.path.join(project_po_dir, po_filename)
                if not os.path.islink(filepath):
                    # got a file which is not a symlink
                    lang = project_lang
                    module = po_filename.replace('.po', '')
                    co_dir = os.path.join(CODIR, project, module, 'po')
                    if not os.path.exists(co_dir):
                        print 'ERROR:  no sources', co_dir
                        continue
                    cofile = os.path.join(co_dir, (lang+'.po'))
                    print ('\n\nMoving ' + filepath + ' to ' + cofile)
                    if not DRYRUN:
                        shutil.move(filepath, cofile)
                    print ('Linking ' + cofile + ' to ' + filepath)
                    if not DRYRUN:
                        os.symlink(cofile, filepath)

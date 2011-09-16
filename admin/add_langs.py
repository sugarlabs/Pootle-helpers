#!/usr/bin/env python

import os, os.path, shutil
import subprocess
import time

CODIR = '/var/lib/pootle/checkouts'
LINKDIR = '/var/lib/pootle/translations'

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

for project in ['honey']:
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
                    cofile = os.path.join(CODIR, project, module, 'po', (lang+'.po'))
                    print ('\n\nMoving ' + filepath + ' to ' + cofile)
                    if not DRYRUN:
                        shutil.move(filepath, cofile)
                    print ('Linking ' + cofile + ' to ' + filepath)
                    if not DRYRUN:
                        os.symlink(cofile, filepath)
                    if not DRYRUN:
                        time.sleep(1) # Just a bit extra cautious here
                        os.chdir(os.path.dirname(cofile))
                        pipe('git pull')
                        cmd = 'git add ' + os.path.basename(cofile)
                        pipe(cmd)
                        cmd = 'git commit -m "Adding language ' + lang + ' via Pootle"'
                        pipe(cmd)
                        cmd = 'git push'
                        pipe (cmd)


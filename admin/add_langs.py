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
        langs = os.path.join(project_langs_dir, project_lang)
        for k in os.listdir(langs):
            if k.endswith('.po'):
                filepath = os.path.join(langs, k)
                if not os.path.islink(filepath):
                    # got a file which is not a symlink
                    lang = project_lang
                    module = k.replace('.po', '')
                    if k.find('TamTam') > -1:
            			cofile = os.path.join(CODIR, project, 'tamtam', module, 'po', (lang+'.po'))
                    #elif k.startswith('measure'):
                    #	cofile = os.path.join(CODIR, project, 'measure-activity', module, 'po', (lang+'.po'))
                    else:
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


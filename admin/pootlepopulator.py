#!/usr/bin/env python

import os, os.path, shutil, sys
import subprocess

CODIR = '/var/lib/pootle/checkouts'
LINKDIR = '/var/lib/pootle/translations'

def pipe(command):
    print ('Running ' + command)
    proc = subprocess.Popen(args = command,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                stdin = subprocess.PIPE,
                shell=True, close_fds=True)
    (output, error) = proc.communicate()
    ret = proc.returncode
    print output
    return output, error, ret

def make_symlink(src, dst):
    if not os.access(dst, os.F_OK):
        print ('  Linking ' + src + ' to ' + dst)
        # check if the relevant immediate toplevel directory exists
        if not os.access(os.path.dirname(dst), os.F_OK):
            os.mkdir (os.path.dirname(dst))
        os.symlink(src, dst)
        
def main():
    if len(sys.argv) < 4:
	print "Usage: " + sys.argv[0] + " category GIT_URL checkout_directory [branch]"
	print "Eg: " + sys.argv[0] + " xo_core git://dev.laptop.org/git/sugar sugar master"
	sys.exit()
    p_cat = sys.argv[1]
    git_url = sys.argv[2]
    p_dir = os.path.join(CODIR, p_cat, sys.argv[3])
    if len(sys.argv) == 5:
	branch = sys.argv[4]
    else:
	branch = "master" 

    # Check if the category directories exist. If not create them.
    if not os.access(os.path.join(CODIR, p_cat), os.F_OK):
        os.mkdir(os.path.join(CODIR, p_cat)) 
    if not os.access(os.path.join(LINKDIR, p_cat), os.F_OK):
        os.mkdir(os.path.join(LINKDIR, p_cat))

    cmd = 'git clone ' + git_url + ' ' + p_dir
    print '\n\n******** Cloning ' + git_url + ' to ' + p_dir + ' *********'
    pipe(cmd)
    os.chdir(p_dir)
    print '\n\n******** Switching to branch ' + branch + ' *********'
    cmd = ' git checkout --track -b ' + branch + ' origin/' + branch
    pipe(cmd)
    cmd = 'git pull'
    pipe(cmd)
    print '\n********* Git operation completed, moving to next stage ********'

    #FIXME: This works for now as all d.l.o projects since all use the GNU layout
    #FIXME: This needs to fixed in a later version
    podir = os.path.join(p_dir, 'po')
    if not os.access(podir, os.F_OK):
        print 'Error: Could not find PO file directory. Causes for this maybe non GNU layout for PO files or incorrect GIT URL.'
        sys.exit()

    potfile = None
    print '\n\n********* Searching for POT file *********'
    for i in os.listdir(podir):
        if i.endswith('.pot'):
            potfile = i
    if potfile == None: # This should not happen
        sys.exit()
    else:
        print '********* Found POT file ' + potfile + ' *********'
    
    print '********* Starting to symlink files *********'
    for i in os.listdir(podir):
        if i.endswith('.po'):
            src = os.path.join(podir, i)
            dst = os.path.join(LINKDIR, p_cat, i.replace('.po', ''), 
                    (os.path.basename(p_dir) +  ".po"))
            make_symlink(src, dst)
        if i.endswith('.pot'):
            src = os.path.join(podir, i)
            dst = os.path.join(LINKDIR, p_cat, 'templates', 
                    (os.path.basename(p_dir) + ".pot"))
            make_symlink(src,dst)
    print '********* Done Symlinking *********'

    
if __name__ == "__main__":
    main()


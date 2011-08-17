#!/usr/bin/env python

# Code in this file has been taken from Sugar (activity.bundlebuilder POT generation code) 
# and Damned Lies (POT diff code)

import ConfigParser
import os, os.path
import sys
import re 
import subprocess
import shutil 

USE_DIFFLIB = 0

class _SvnFileList(list):
    def __init__(self):
        f = os.popen('svn list -R')
        for line in f.readlines():
            filename = line.strip()
            if os.path.isfile(filename):
                self.append(filename)
        f.close()

class _GitFileList(list):
    def __init__(self):
        f = os.popen('git ls-files')
        for line in f.readlines():
            filename = line.strip()
            if not filename.startswith('.'):
                self.append(filename)
        f.close()

class _DefaultFileList(list):
    def __init__(self):
        for name in os.listdir('activity'):
            if name.endswith('.svg'):
                self.append(os.path.join('activity', name))

        self.append('activity/activity.info')

        if os.path.isfile(_get_source_path('NEWS')):
            self.append('NEWS')

class _ManifestFileList(_DefaultFileList):
    def __init__(self, manifest):
        _DefaultFileList.__init__(self)
        self.append(manifest)

        f = open(manifest,'r')
        for line in f.readlines():
            stripped_line = line.strip()
            if stripped_line and not stripped_line in self:
                self.append(stripped_line)
        f.close()

def _get_file_list(manifest):
    if os.path.isfile(manifest):
        return _ManifestFileList(manifest)
    elif os.path.isdir('.git'):
        return _GitFileList()
    elif os.path.isdir('.svn'):
        return _SvnFileList()
    else:
        return _DefaultFileList()

def _get_source_path(path=None):
    if path:
        return os.path.join(os.getcwd(), path)
    else:
        return os.getcwd()
        
def _get_activity_name():
    info_path = os.path.join(_get_source_path(), 'activity', 'activity.info')
    f = open(info_path,'r')
    info = f.read()
    f.close()
    match = re.search('^name\s*=\s*(.*)$', info, flags = re.MULTILINE)
    return match.group(1)
    

def diff(pota, potb, only_additions = 0):
    """Returns a list of differing lines between two files."""
    f1 = open(pota, "r")
    data1 = f1.read()
    res1 = _parse_contents(data1)
    res1.sort()

    f2 = open(potb, "r")
    data2 = f2.read()
    res2 = _parse_contents(data2)
    res2.sort()

    if not USE_DIFFLIB:
        # since we are working with sorted data, we can speed up the process by doing compares ourselves
        # instead of using difflib stuff
        i, j = 0, 0
        result = []
        while i < len(res1) and j < len(res2):
            if res1[i] == res2[j]:
                i+=1; j+=1
            elif res1[i] < res2[j]:
                if not only_additions:
                    result.append("- " + res1[i])
                i+=1
            elif res1[i] > res2[j]:
                result.append("+ " + res2[j])
                j+=1
        #print "\n".join(result)
        return result
    else:
        import difflib
        d = difflib.Differ()
        result = list(d.compare(res1, res2))

        onlydiffs = []
        for line in result:
            if line[0]!=" ":
                onlydiffs.append(line)
                #print line
        return onlydiffs


def _parse_contents(contents):
    """Parse PO file data, returning a list of msgid's.

    It also supports msgctxt (GNU gettext 0.15) and plural forms,
    the returning format of each entry is:

         [msgctxt::]msgid[/msgid_plural]"""

    if contents[-1] != "\n": contents += "\n"

    # state machine for parsing PO files
    msgid = ""; msgstr = ""; msgctxt = ""; comment = ""; plural = ""; 
    in_msgid = in_msgstr = in_msgctxt = in_msgid_plural = in_plural = 0

    result = []
    enc = "UTF-8"

    lines = contents.split("\n")
    lines.append("\n")
    for line in lines:
        line = line.strip()

        if line == "":
            if in_msgstr and msgid != "":
                onemsg = ""
                
                if msgctxt: onemsg += ('"' + msgctxt + '"::')
                onemsg += ('"' + msgid + '"')
                if plural: onemsg += ('/"' + plural + '"')

                result.append(onemsg)

            elif in_msgstr and msgid == "":
                # Ignore PO header
                pass

            msgid = ""; msgstr = ""; msgctxt = ""
            in_msgid = 0; in_msgstr = 0; in_msgctxt = 0
            flags = []; sources = []; othercomments = {}
            plural = ""; plurals = []; in_msgid_plural = 0; in_plural = 0

        elif line[0] == "\"" and line[-1] == "\"":
            if in_msgid:
                if in_msgid_plural:
                    plural += line[1:-1]
                else:
                    msgid += line[1:-1]
            elif in_msgctxt:
                msgctxt += line[1:-1]
            elif in_msgstr:
                pass
            else:
                raise Exception()

        elif line[0] == "#":
            # Ignore any comments, flags, etc.
            continue

        elif line[:12] == "msgid_plural" and in_msgid:
            in_msgid_plural = 1
            plural = line[13:].strip()[1:-1]
        elif line[:5] == "msgid" and not in_msgid:
            in_msgctxt = 0
            in_msgid = 1
            msgid = line[6:].strip()[1:-1]
        elif line[:7] == "msgctxt" and not in_msgid:
            in_msgctxt = 1
            msgctxt = line[8:].strip()[1:-1]
        elif line[:7] == "msgstr[" and in_msgid_plural:
            in_msgstr = 1
            in_msgid = 0
            in_msgctxt = 0
        elif line[:6] == "msgstr" and in_msgid:
            in_msgstr = 1
            in_msgid = 0
            in_msgctxt = 0
        else:
            pass
    return result    

class PotFile:
    def __init__(self, location, project, vcs, method, layout):
        self.location = location
        self.project = project
        self.vcs = vcs
        self.method = method
        self.layout = layout
        
    def update(self):
        print '\n\n\n ####### Checking POT for ' + self.project + ' ######\n\n\n'
        # First we get the latest code from versioncontrol
        podir = os.path.dirname(self.location)
        os.chdir(podir)
        if self.vcs == 'git':
            args = ['git', 'pull']
            subprocess.call(args) 
        elif self.vcs.startswith('http'):
            args = ['wget', '--no-check-certificate', '-O', 'new.pot', self.vcs]
            subprocess.call(args)

        if self.method == 'bundlebuilder':
            podir = os.path.dirname(self.location)
            projdir = os.path.dirname(podir) # For GNU Style layouts only
            os.chdir(projdir)

            manifest = os.path.join(projdir, 'MANIFEST')
            
            python_files = []
            file_list = _get_file_list(manifest)
            for file_name in file_list:
                if file_name.endswith('.py'):
                    python_files.append(file_name)

            # First write out a stub .pot file containing just the translated
            # activity name, then have xgettext merge the rest of the
            # translations into that. (We can't just append the activity name
            # to the end of the .pot file afterwards, because that might
            # create a duplicate msgid.)
            new_pot_file = os.path.join(projdir, 'po', 'new.pot') 
            activity_name = _get_activity_name()
            escaped_name = re.sub('([\\\\"])', '\\\\\\1', activity_name)
            f = open(new_pot_file, 'w')
            f.write('#: activity/activity.info:2\n')
            f.write('msgid "%s"\n' % escaped_name)
            f.write('msgstr ""\n')
            f.close()

            args = [ 'xgettext', '--join-existing', '--language=Python',
                     '--keyword=_', '--add-comments=TRANS:', '--output=%s' % new_pot_file ]

            args += python_files
            retcode = subprocess.call(args)
            if retcode:
                print 'ERROR - xgettext failed with return code %i.' % retcode
        
        elif self.method == 'intltool':
            podir = os.path.dirname(self.location)
            os.chdir(podir)
            
            args = ['intltool-update', '--pot', '--gettext-package=new']
            retcode = subprocess.call(args)
            if retcode:
                print 'ERROR - intltool failed with return code %i.' % retcode
                
        
        # Now we do a diff
        podir = os.path.dirname(self.location)
        new_pot_file = os.path.join(podir, 'new.pot')
        if (len(diff(self.location, new_pot_file))):
	    print ('\n\n ***** Updating POT for ' + self.project +  '*****\n\n\n')
            shutil.move(new_pot_file, self.location)
        else:
            os.unlink(new_pot_file)
        sys.stdout.flush() #aleksey suggestion   

def parse_config(location):
    cfg = ConfigParser.ConfigParser()
    cfg.read(location)
    for i in cfg.sections():
        p = PotFile(i, cfg.get(i, 'project'), cfg.get(i, 'vcs'), 
                cfg.get(i, 'method'), cfg.get(i, 'layout'))
        p.update()
        
if __name__ == '__main__':
    parse_config (sys.argv[1])

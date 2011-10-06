#!/usr/bin/env python

import ConfigParser

import sys
import os.path
import subprocess
import tempfile
import shutil

import translate.storage.po

LANGS = ['af', 'am', 'ar', 'ay', 'bg', 'bn', 'bn_IN', 'ca', 'de', 'dz', 'el', 
         'en', 'es', 'fa', 'fa_AF', 'ff', 'fr', 'gu', 'ha', 'hi', 'ht', 'ig', 
         'is', 'it', 'ja', 'km', 'ko', 'mg', 'mk', 'ml', 'mn', 'mr', 'mvo', 'nb', 
         'ne', 'nl', 'pa', 'pap', 'pis', 'pl', 'ps', 'pt', 'pt_BR', 
         'qu', 'ro', 'ru', 'rw', 'sd', 'si', 'sl', 'ta', 'te', 'th', 
         'tpi', 'tr', 'ur', 'vi', 'yo', 'zh_CN', 'zh_TW']
TRANSLATE_DIR = '/var/lib/pootle/translations'


def gen_langpack(lang, tmpdir, configfile, opdir):
    
    os.mkdir(os.path.join(tmpdir, lang))

    # Setup.sh is the installer 
    f = open(os.path.join(tmpdir, lang, 'setup.sh'), 'a')
    f.write('#!/bin/bash\n')
    
    c =  ConfigParser.ConfigParser()
    c.read(configfile)

    for i in c.sections():
        name = c.get(i, 'name')
        cat = c.get(i, 'category')
        mo = c.get(i, 'molocation')
        needs_linfo = c.getint(i, 'needs_linfo')
        try:
            linfo = c.get(i, 'linfolocation')
            linfo = linfo.replace('LL', lang)
        except ConfigParser.NoOptionError:
            linfo = os.path.dirname(mo).replace('LL', lang).replace('LC_MESSAGES', 
                                                                'activity.linfo')

        pofile = os.path.join(TRANSLATE_DIR, cat, lang, i)
        mofile = os.path.join(tmpdir, lang, name + '.mo')
        linfofile = os.path.join(tmpdir, lang, name + '.linfo')
        cmd = ['msgfmt', pofile, '-o', mofile]
        subprocess.call(cmd) # Generate the MO file
        if needs_linfo == 1:
            gen_linfo(linfofile, name, lang, pofile) # generate the .linfo file
        
        #f.write('\n\nmkdir -p ' + os.path.dirname(mo.replace('LL', lang)))
        if mo.find('/home/olpc') > -1:
            # We are installing inside /home/olpc, assign ownership appropriately
            install_string = '\n\tinstall -D -b -g olpc -o olpc -m 644 '
        else:
            install_string = '\n\tinstall -D -b -m 644 '
        
        f.write('\nif [[ -d ' + os.path.dirname(mo[:(mo.find('LL') - 1)]) + ' ]] ; then')
        f.write(install_string + name.replace(' ', '\\ ') + '.mo ' + mo.replace('LL', lang))
            
        if needs_linfo == 1:
            f.write(install_string + name.replace(' ', '\\ ') + '.linfo ' + linfo)
        f.write('\nfi\n')
        
    f.write ('\n\n\ncp uninstall_langpack /usr/bin/uninstall_langpack_' + lang)

    # Some of the directories created are left as root owned. We need to fix that
    f.write ('\n\n\nfind /home/olpc/Activities -uid 0 -print0 | xargs -0 chown olpc:olpc')

    f.close()

    os.chmod (os.path.join(tmpdir, lang, 'setup.sh'), 777)
    # Installer done
    
    # Now we write the un-installer
    f = open(os.path.join(tmpdir, lang, 'uninstall_langpack'), 'a')
    f.write('#!/bin/bash\n')
    
    for i in c.sections():
        mo = c.get(i, 'molocation')
        needs_linfo = c.get(i, 'needs_linfo')
        
        try:
            linfo = c.get(i, 'linfolocation')
            linfo = linfo.replace('LL', lang)
        except ConfigParser.NoOptionError:
            linfo = os.path.dirname(mo).replace('LL', lang).replace('LC_MESSAGES', 
                                                                'activity.linfo')

        
        f.write ('\nrm -f ' + mo.replace('LL', lang))
        f.write ('\nif [ -f ' + mo.replace('LL', lang) + '~ ]; then\n\tmv ' 
                 + mo.replace('LL', lang) + '~ ' + mo.replace('LL', lang) 
                 + '\nfi')
        if needs_linfo == 1:
            f.write ('\nrm -f ' + linfo)
            f.write ('\nif [ -f ' + linfo + '~ ]; then\n\tmv ' + linfo 
                     + '~ ' + linfo + '\nfi')
        
    f.close()
    os.chmod(os.path.join(tmpdir, lang, 'uninstall_langpack'), 777)
    # Uninstaller done
    

    # Make the actual self-extracting installer. 
    # We use a tool called makeself to do this
    # See http://megastep.org/makeself/ for more info
    mkself_cmd = ['makeself', os.path.join(tmpdir, lang), 
            os.path.join(opdir, lang + '_lang_pack_v2.sh'), 
            'Language pack', './setup.sh']
    subprocess.call(mkself_cmd)

def gen_linfo(filepath, name, lang, pofile):
    """ Generates activity.linfo file from translations from the PO file"""
    po = translate.storage.po.pofile.parsefile(pofile)
    unit = po.findunit(name)
    
    if unit.istranslated() == False:
        act_name = name # Doh! Not translated. We stick to the English name
    else:
        act_name = unit.gettarget()

    f = open(filepath, 'a')
    f.write('[Activity]\nname = ' + act_name.encode('utf-8'))
    f.close()

if __name__ == '__main__':
    dir = tempfile.mkdtemp()
    for i in LANGS:
        # FIXME: FIXME: This is one of the fugliest hacks I've ever done
        # This will be fixed once we move out of the Update-1 support period
        # or when we shift the language list to the ini files
        if (sys.argv[1].find('update1') > -1 and not os.path.exists(os.path.join(TRANSLATE_DIR, 'update1', i))):
            continue
        else:
            gen_langpack(i, dir, sys.argv[1], sys.argv[2])
            
    shutil.rmtree(dir)
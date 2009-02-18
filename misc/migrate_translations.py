#!/usr/bin/env python

import translate.storage.po
import sys
import os, os.path

def migrate(old, new):

    oldpo = translate.storage.po.pofile.parsefile(old)
    newpo = translate.storage.po.pofile.parsefile(new)

    #iterate through new po
    for i in newpo.unit_iter():
        unit = oldpo.findunit(i.msgid[0].strip('"'))
        if unit is not None and len(unit.msgid) == len(i.msgid):
            sys.stdout.write('.')
            #print i.msgid, unit.msgid
            # be careful, and do not overwrite old translations
            if i.msgstrlen() == 0 or i.isfuzzy() == True:
                i.msgstr[0] = unit.msgstr[0]
                if i.isfuzzy() == True and unit.isfuzzy() == False:
                    i.markfuzzy(False)

    print ""
    newpo.save()

if __name__ == '__main__':
    olddir = sys.argv[1]
    newdir = sys.argv[2]

    for i in os.listdir(os.path.join(newdir, 'po')):
        #FIXME: The line below is so fugly
        if i.endswith('.po') and not (i.endswith('pseudo.po') or i.endswith('ha.po') or i.endswith('bn_IN.po') or i.endswith('en_US.po') or i.endswith('ta.po') or i.endswith('na.po')):
            new = os.path.join(newdir, 'po', i)
            old = os.path.join(olddir, 'po', i)
            migrate(old, new)
            


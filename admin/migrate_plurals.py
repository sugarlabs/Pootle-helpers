#!/usr/bin/python

import os, os.path
from translate.storage import po

s_t = '/home/sayamindu/Work/Devel/sugar-toolkit/po'
s_u = '/home/sayamindu/Work/Devel/sugar-update-control/po'

for i in os.listdir(s_u):
    if i.endswith('po') and not i.startswith('pseudo'):
        if not os.path.exists(os.path.join(s_t, i)):
            print 'WARNING: NOT FOUND ' + i
        else:
            s_t_p = po.pofile.parsefile(os.path.join(s_t, i))
            s_u_p = po.pofile.parsefile(os.path.join(s_u, i))
    
            plural = s_t_p.getheaderplural()

            s_u_p.updateheaderplural(plural[0], plural[1])

            s_u_p.save()

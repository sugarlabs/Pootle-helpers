#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import subprocess

POOTLE_DIR = '/var/lib/pootle/checkouts'
OUTPUT = '/var/lib/pootle/public_html/status/index.html'

if os.getuid() == 0:
    print '%s should not be run from root user' % sys.argv[0]
    exit(1)

out = open(OUTPUT, 'w')

langs =  ['af', 'am', 'ar', 'ar_SY', 'ay', 'bg', 'bi', 'bn', 'bn_IN', 'bs',
        'ca', 'cpp', 'cs', 'de','dz', 'el', 'es', 'fa', 'fa_AF', 'ff', 'fi', 'fil',
        'gu', 'ha', 'he', 'hi', 'ht', 'hu', 'hus', 'ig', 'is', 'it', 'ja',
        'km', 'kn', 'ko', 'kos', 'lv', 'mg', 'mk', 'ml', 'mn', 'mr', 'ms',
        'mvo', 'na', 'nb', 'ne', 'nl', 'nn', 'pa', 'pap', 'pis', 'pl', 'ps',
        'pt', 'pt_BR', 'quy', 'quz', 'ro', 'ru', 'rw', 'sd', 'si', 'sk', 'sl', 'sm',
        'st', 'sv', 'sw', 'ta', 'te', 'th', 'ton', 'tpi', 'tr', 'tvl', 'tzo',
        'ug', 'uk', 'ur', 'vi', 'wa', 'yo', 'zh_CN', 'zh_TW']


projects = ['fructose', 'glucose', 'honey', 'glucose92',
        'fructose84', 'glucose84',  'dextrose3', 'olpc_software']
cant_langs = len(langs)

out.write('<html><body>')
out.write('<table>')
out.write('<tr><th>Module</th><th>git push</th>')

out.write('<head>' +
        '<style type=text/css>' +
        'body {' + 
        '    background-color:#d0e4fe;' +
        '    font-family:Arial;' +
        '    font-size:10px;}' +
        'p {' +
        '    font-size:14px;' +
        '    color:orange;}' +
        'th {' +
        '    background-color:grey;' +
        '    color:orange;' +
        '    text-align:center;}' +
        'td {' +
        '    background-color:white;}' +
        '</style></head>')

out.write('<h1>%s</h1>' % datetime.datetime.utcnow())

for lang in langs:
    out.write('<th>%s</th>' % lang)
out.write('</tr>\n')

for project in projects:
    out.write('<tr><th> %s </th><th></th><th colspan="%d"></th></tr>' %
            (project, cant_langs))
    for module in os.listdir(os.path.join(POOTLE_DIR, project)):
        if module.endswith('.old') or module.endswith('.bak'):
            continue

        module_dir = os.path.join(POOTLE_DIR, project, module)
        if not os.path.isdir(module_dir) or \
                not os.path.isdir(os.path.join(module_dir, 'po')) or \
                not os.path.isdir(os.path.join(module_dir, '.git')):
            continue

        out.write('<tr><th> %s </th>' % module)

        # check push status
        attrs = {}
        git = subprocess.Popen(['git', 'push', '-n'],
                stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=module_dir)
        attrs['output'] = git.communicate()[1] \
                .replace("'", "\\'").replace('\n', '\\n')
        if git.returncode == 0:
            attrs['color'] = 'green'
            attrs['text'] = 'OK'
        else:
            attrs['color'] = 'red'
            attrs['text'] = 'ERROR'
        out.write('<th><a href="javascript:alert(\'%(output)s\')" ' \
                  'style="color:%(color)s">%(text)s</a></th>' % attrs)

        # check git status
        module_state = {}
        git = subprocess.Popen(['git', 'status', '-s', '.'],
                stdout=subprocess.PIPE, cwd=os.path.join(module_dir, 'po'))
        for line in git.communicate()[0].split('\n'):
            words = line.split()
            if words == []:
                break
            state = words[0]
            if words[1].endswith('.po'):
                lang = words[1][:-3]
                if lang in langs:
                    module_state[lang] = state
        for lang in langs:
            if lang in module_state:
                out.write('<td>%s</td>' % module_state[lang])
            else:
                out.write('<td></td>')
        out.write('</tr>\n')

out.write('</table>')
out.write('</body></html>')

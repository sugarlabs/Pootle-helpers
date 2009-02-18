#!/usr/bin/env python

from jToolkit import prefs


class TeamPageGenerator:
    def __init__(self, prefsfile, usersfile):
        self.prefsfile = prefsfile
        self.usersfile = usersfile
        
        self.pootleprefs = prefs.PrefsParser(self.prefsfile)
        self.usersprefs = prefs.PrefsParser(self.usersfile)
        
        self.languagelist = self.getlanguagelist()
        self.userlist = self.getuserlist()
        
    def getlanguagelist(self):
        languages = []
        for i, j in self.pootleprefs.Pootle.languages.iteritems(sorted = True):
            languages.append(i)
            
        return languages 
            
    def getuserlist(self):
        users = []
        for i, j in self.usersprefs.iteritems(sorted = True):
            users.append(i)
        return users
            
    def getuserlangs(self, user):
        try:
            langlist = getattr(self.usersprefs, user + '.languages').split(',')
        except IndexError:
            langlist = []
            
        return langlist
            
    def getuserforlang(self, langcode):
        users = []
        for i in self.userlist:
            if langcode in self.getuserlangs(i):
                users.append(i)
        return users
    
    def getuserfullname(self, user):
        return getattr(self.usersprefs, user + '.name')
        
    def getlanguagefullname(self, langcode):
        return unicode(getattr(self.pootleprefs, 'Pootle.languages.' + langcode + '.fullname'))
    
    def generate_text_tables(self):
        # FIXME: This is ugly
        for i in self.languagelist:
            print '============== ' + self.getlanguagefullname(i) + ' =============='
            userlist = self.getuserforlang(i)
            if len(userlist) == 0:
                print '\tNo Users'
            else:
                for j in userlist:
                    print '\t' + self.getuserfullname(j).encode('utf-8')
                    
    def get_languser_mapping(self):
        mapping = {}
        for i in self.languagelist:
            mapping[self.getlanguagefullname(i)] = self.getuserforlang(i)
            
            
                    
if __name__ == '__main__':
    
    teamgen = TeamPageGenerator('/home/sayamindu/Work/Pootle/Pootle-1.1.0rc2/pootle_test/pootle.prefs', 
                            '/home/sayamindu/Work/Pootle/Pootle-1.1.0rc2/pootle_test/users.prefs')
    
                
        
        

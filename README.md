# Pootle-helpers
__________

Collection of scripts which is used to keep the Pootle service in a sane state.

This was moved from our [gitorious instance](http://git.sugarlabs.org/projects/pootle-helpers) as that's unmaintained.


## How it works

The advantage of Pootle is that it can understand symlinks. We use this feature 
to have a layout according to (sub)project and versions.
For example, for the core Sugar libs and UI (called Glucose), we have the 
symlinks in the form of:

/var/lib/pootle/checkouts/glucose84/sugar/po/es.po
	-> /var/lib/pootle/translations/glucose84/es/sugar.po

The number 84 signifies version Glucose 0.84 and the latest leading edge odd 
numbered version is tracked in a numberless form (eg: glucose or fructose).

## Automating this

This project has a set of scripts to automate the creation of symlinks for a 
given project. 

## admin/pootlepopulator.py

This script checks out a project from Git into /var/lib/pootle/checkouts/..., and 
then creates the appropiate symlinks in /var/lib/pootle/translations/...

  Usage: pootlepopulator.py category GIT_URL checkout_directory git_branch
  Eg: pootlepopulator.py glucose git://dev.laptop.org/git/sugar sugar master


## admin/add_langs.py

The pootlepopulator.py script has a minor problem. Once a project is visible, and 
a new language is added to it from the web based interface, the new PO file gets 
created in /var/lib/pootle/translations/... where it should ideally be a symlink.
To counter this, admin/add_langs.py has to be run after a new language has been 
added.
This script runs without any arguments and crawls through the subdirectories of 
/var/lib/pootle/translations/... When it finds a non-symlink PO file, it moves it 
to the right location, git adds it and makes the correct symlink.


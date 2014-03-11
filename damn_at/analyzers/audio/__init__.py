import glob
import os, sys

plugins = []

def LoadPlugins(path):
  for root,dirs,files in os.walk(path):
    if os.path.basename(root) == '.svn':
      continue
    for p in glob.glob(root+"/*.py"):
       name=os.path.basename(p).split(".py")[0]
       if name != '__init__' and not name.startswith('b-script'):
        modulePath = os.path.relpath(root, os.path.join(path, '..')).replace(os.sep, '.')
        try:
          print "Importing", modulePath+'.'+name
          module = __import__(modulePath+'.'+name)
        except:
          print "FAIL", name, p, sys.exc_info()
          continue
        module = getattr(sys.modules[modulePath], name)
        for klass in dir(module):
          klass = getattr(module, klass)
          if hasattr(klass, 'analyzer'):
            plugins.append(klass)

LoadPlugins(os.path.dirname(__file__))

del LoadPlugins
del glob
del os

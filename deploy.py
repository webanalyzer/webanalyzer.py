#! /usr/bin/env python

import re
import os
import sys
import datetime


today = datetime.datetime.today()
if today.weekday() != 0:
    print("There is only one god, and His name is Death. And there is only one thing we say to Death.")
    print('not today')
    sys.exit(0)


print("time to go")
version = today.strftime('%Y.%m.%d')
filename = os.path.join(os.path.dirname(__file__), 'webanalyzer/__init__.py')
with open(filename) as fd:
    content = re.sub(r'__version__\s+=\s+(.*)', "__version__ = '%s'" % version, fd.read())
    with open(filename, 'w') as fdw:
        fdw.write(content)


os.system("python setup.py sdist")
os.system("twine upload dist/*")

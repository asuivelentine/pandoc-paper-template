#!/usr/bin/env python2

"""
Pandoc filter to process code blocks with class "blockdiag", "seqdiag",
"actdiag", "nwdiag", "packetdiag", "rackdiag" into generated images.
"""

import subprocess
import hashlib
import os
import sys
import tempfile
from pandocfilters import toJSONFilter, Str, Para, Image, attributes

def sha1(x):
  return hashlib.sha1(x).hexdigest()

imagedir = "blockdiag-images"

def out(s):
    sys.stderr.write('\t[BLKDIA] ' + s + '\n');

def save(data):
    fd, name = tempfile.mkstemp()
    os.write(fd, data)
    os.close(fd)
    return name

def isDiag(classes):
    for i in ["blockdiag", "seqdiag", "actdiag", "nwdiag", "packetdiag", "rackdiag"]:
        if i in classes:
            return True, i
    return False, ""

def blockdiag(key, value, fmt, meta):
  if key == 'CodeBlock':
    [[ident,classes,keyvals], code] = value
    caption = ""
    found, cmd = isDiag(classes)
    if found == True:
      path = os.path.dirname(os.path.abspath(__file__))
      filename = sha1(code)
      alt = Str(caption)
      tit = ""
      src = imagedir + '/' + filename + '.png'
      out(src);
      if not os.path.isfile(src):
        try:
            out("MKDIR " + imagedir);
            os.mkdir(imagedir)
        except OSError:
            pass
        tmp = save(code)
        p = subprocess.Popen([cmd, "-Tpng", "-a", tmp, "-o", src], shell=False, stdin=None, stdout=None, stderr=subprocess.PIPE, close_fds=True)
        err = p.stderr.read()
        p.stderr.close()
        if (len(err) > 0):
            return Para([Str(err)])
        os.remove(tmp)
      try:
        image = Image(attributes({}), [alt], [src,tit])
        return Para([image])
      except:
        try:
          image = Image([alt], [src,tit])
          return Para([image])
        except:
          pass

if __name__ == "__main__":
  toJSONFilter(blockdiag)

# -*- coding: utf-8 -*-

from resources.lib import kodilogging
from resources.lib import script
import sys, xbmc, os, time, base64, xbmc,xbmcgui,xbmcaddon,urllib,base64,os,sys,shutil,time
import urllib.request
import logging
import xbmcaddon
import time
#time.sleep(20)



# Keep this file to a minimum, as Kodi
# doesn't keep a compiled copy of this
ADDON = xbmcaddon.Addon()
kodilogging.config()
try:
    version = int(str(urllib.request.urlopen(base64.b64decode("aHR0cHM6Ly9yZXBvc3R1YmVib3guZ2VhdGl2ZS5kZS9Lb2RpL0J1aWxkL3ZlcnNpb24=").decode("utf-8")).read().decode("utf-8") ))
except:
    sys.exit()

if os.path.exists(os.path.join(xbmc.translatePath('special://home/addons'), 'version')):
    f = open(os.path.join(xbmc.translatePath('special://home/addons'), 'version'), 'r')
    if int(f.read()) < version:
        script.get_update(version)
else:
   script.get_update(version)

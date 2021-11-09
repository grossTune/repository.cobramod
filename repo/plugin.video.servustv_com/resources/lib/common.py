# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import xbmcvfs
import shutil
import time
from datetime import datetime, timedelta
from calendar import timegm as TGM
import io
import requests
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote, unquote_plus  # Python 2.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmc.translatePath, xbmc.LOGNOTICE, 'inputstreamaddon' # Stand: 05.12.20 / Python 2.X
else:
	from urllib.parse import urlencode, quote, unquote_plus  # Python 3.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmcvfs.translatePath, xbmc.LOGINFO, 'inputstream' # Stand: 05.12.20  / Python 3.X
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


global debuging
HOST_AND_PATH               = sys.argv[0]
ADDON_HANDLE                = int(sys.argv[1])
dialog                                    = xbmcgui.Dialog()
addon                                   = xbmcaddon.Addon()
addon_id                              = addon.getAddonInfo('id')
addon_name                       = addon.getAddonInfo('name')
addon_version                    = addon.getAddonInfo('version')
addonPath                           = TRANS_PATH(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath                              = TRANS_PATH(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
tempTN                                = TRANS_PATH(os.path.join(dataPath, 'tempTN', '')).encode('utf-8').decode('utf-8')
tokenFile                              = os.path.join(tempTN, 'TOKEN')
searchHackFile                   = os.path.join(dataPath, 'searchString')
channelFavsFile                  = os.path.join(dataPath, 'favorites_SERVUS.json')
defaultFanart                      = (os.path.join(addonPath, 'fanart.jpg') if PY2 else os.path.join(addonPath, 'resources', 'media', 'fanart.jpg'))
icon                                       = (os.path.join(addonPath, 'icon.png') if PY2 else os.path.join(addonPath, 'resources', 'media', 'icon.png'))
artpic                                    = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
tokenDelay                          = int(addon.getSetting('token_rhythm'))
streamVersion                     = addon.getSetting('transmit_technique')
verify_ssl_connect             = (True if addon.getSetting('verify_ssl') == 'true' else False)
enableADJUSTMENT          = addon.getSetting('show_settings') == 'true'
textSelection                       = addon.getSetting('field_spread')
DEB_LEVEL                          = (LOG_MESSAGE if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
BASE_URL                            = 'https://www.servustv.com/'
SERVUSTV_HLS                   = 'https://dms.redbull.tv/v3/'
SERVUSTV_API                   = 'https://api.redbull.tv/v3/'
SERVUSTV_ART                  = 'https://resources.redbull.tv/'

xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')

def py2_enc(s, nom='utf-8', ign='ignore'):
	if PY2:
		if not isinstance(s, basestring):
			s = str(s)
		s = s.encode(nom, ign) if isinstance(s, unicode) else s
	return s

def py2_uni(s, nom='utf-8', ign='ignore'):
	if PY2 and isinstance(s, str):
		s = unicode(s, nom, ign)
	return s

def py3_dec(d, nom='utf-8', ign='ignore'):
	if not PY2 and isinstance(d, bytes):
		d = d.decode(nom, ign)
	return d

def translation(id):
	return py2_enc(addon.getLocalizedString(id))

def failing(content):
	log(content, xbmc.LOGERROR)

def debug_MS(content):
	log(content, DEB_LEVEL)

def log(msg, level=LOG_MESSAGE): # kompatibel mit Python-2 und Python-3
	msg = py2_enc(msg)
	return xbmc.log('[{0} v.{1}]{2}'.format(addon_id, addon_version, msg), level)

def get_userAgent():
	base = 'Mozilla/5.0 {0} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
	if xbmc.getCondVisibility('System.Platform.Android'):
		if 'arm' in os.uname()[4]: return base.format('(X11; CrOS armv7l 7647.78.0)') # ARM based Linux
		return base.format('(X11; Linux x86_64)') # x86 Linux
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		return base.format('(Windows NT 10.0; WOW64)') # Windows
	elif xbmc.getCondVisibility('System.Platform.IOS'):
		return base.format('(iPhone; CPU iPhone OS 10_3 like Mac OS X)') # iOS iPhone/iPad
	elif xbmc.getCondVisibility('System.Platform.Darwin'):
		return base.format('(Macintosh; Intel Mac OS X 10_10_1)') # Mac OSX
	return base.format('(X11; Linux x86_64)') # x86 Linux

def ADDON_operate(IDD):
	js_query = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Addons.GetAddonDetails", "params":{"addonid":"'+IDD+'", "properties":["enabled"]}}')
	if '"enabled":false' in js_query:
		try:
			xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{"addonid":"'+IDD+'", "enabled":true}}')
			failing("(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{0}* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####".format(IDD))
		except: pass
	if '"error":' in js_query:
		dialog.ok(addon_id, translation(30501).format(IDD))
		failing("(common.ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{0}* ist NICHT installiert !!! #####".format(IDD))
		return False
	if '"enabled":true' in js_query:
		return True

def get_Local_DT(info):
	fixed_format = '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':') # 2021-03-28T10:00:00.000+02:00
	utcDT = datetime(*(time.strptime(info, fixed_format)[0:6]))
	try:
		localDT = datetime.fromtimestamp(TGM(utcDT.timetuple()))
		assert utcDT.resolution >= timedelta(microseconds=1)
		localDT = localDT.replace(microsecond=utcDT.microsecond)
	except (ValueError, OverflowError): # ERROR on Android 32bit Systems = cannot convert unix timestamp over year 2038
		localDT = datetime.fromtimestamp(0) + timedelta(seconds=TGM(utcDT.timetuple()))
		localDT = localDT - timedelta(hours=datetime.timetuple(localDT).tm_isdst)
	return localDT

def get_Picture(elem_id, resources, elem_type, width=960, quality=65):
	img_type = next(iter(filter(lambda x: (elem_type in x), resources)), None)
	if img_type:
		return '{0}{1}/{2}/im:i:w_{3},q_{4}?namespace=stv'.format(SERVUSTV_ART, elem_id, img_type, width, quality)
	return None

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split('&')
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
pict = unquote_plus(params.get('pict', ''))
plot = unquote_plus(params.get('plot', ''))
mode = unquote_plus(params.get('mode', 'root'))
action = unquote_plus(params.get('action', 'DEFAULT'))
page = unquote_plus(params.get('page', '1'))
limit = unquote_plus(params.get('limit', '20'))
phrase = unquote_plus(params.get('phrase', 'collections'))
searching = unquote_plus(params.get('searching', 'None'))
wallpaper = unquote_plus(params.get('wallpaper', 'DEFAULT'))
cineType = unquote_plus(params.get('cineType', 'movie'))

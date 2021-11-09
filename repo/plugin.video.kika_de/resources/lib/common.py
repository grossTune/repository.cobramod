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
import hashlib
import time
import _strptime
from datetime import datetime, timedelta
import threading
import traceback
import requests
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, unquote_plus  # Python 2.X
	from urllib2 import urlopen  # Python 2.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmc.translatePath, xbmc.LOGNOTICE, 'inputstreamaddon' # Stand: 05.12.20 / Python 2.X
else:
	from urllib.parse import urlencode, unquote_plus  # Python 3.X
	from urllib.request import urlopen  # Python 3.X
	from functools import reduce  # Python 3.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmcvfs.translatePath, xbmc.LOGINFO, 'inputstream' # Stand: 05.12.20  / Python 3.X
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


global debuging
HOST_AND_PATH                = sys.argv[0]
ADDON_HANDLE                 = int(sys.argv[1])
dialog                                     = xbmcgui.Dialog()
addon                                     = xbmcaddon.Addon()
addon_id                               = addon.getAddonInfo('id')
addon_name                        = addon.getAddonInfo('name')
addon_version                     = addon.getAddonInfo('version')
addonPath                            = TRANS_PATH(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath                               = TRANS_PATH(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
WORKFILE                            = os.path.join(dataPath, 'episode_data.json')
defaultFanart                       = (os.path.join(addonPath, 'fanart.jpg') if PY2 else os.path.join(addonPath, 'resources', 'media', 'fanart.jpg'))
icon                                        = (os.path.join(addonPath, 'icon.png') if PY2 else os.path.join(addonPath, 'resources', 'media', 'icon.png'))
artpic                                     = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
alppic                                     = os.path.join(addonPath, 'resources', 'media', 'alphabet', '').encode('utf-8').decode('utf-8')
Newest                                  = addon.getSetting('Newest') == 'true'
Mostviewed                          = addon.getSetting('Mostviewed') == 'true'
kikaninchen                         = addon.getSetting('kikaninchen') == 'true'
sesamstrasse                        = addon.getSetting('sesamstrasse') == 'true'
since03                                  = addon.getSetting('since03') == 'true'
since06                                  = addon.getSetting('since06') == 'true'
since10                                  = addon.getSetting('since10') == 'true'
sinceAll                                  = addon.getSetting('sinceAll') == 'true'
enableINPUTSTREAM         = addon.getSetting('useInputstream') == 'true'
prefSTREAM                         = addon.getSetting('prefer_stream')
resToAutoSelect                  = {0:'BESTEVER', 1:'HIGH', 2:'GOOD', 3:'MEDIUM', 4:'LOW'}[int(addon.getSetting('prefer_quality'))]
Dating                                   = addon.getSetting('show_date') == 'true'
Masking                                = addon.getSetting('hide_unplayable') == 'true'
useThumbAsFanart            = addon.getSetting('useThumbAsFanart') == 'true'
Pagination                            = int(addon.getSetting('max_pages'))+1
enableADJUSTMENT           = addon.getSetting('show_settings') == 'true'
DEB_LEVEL                           = (LOG_MESSAGE if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
forceView                             = addon.getSetting('forceView') == 'true'
viewIDAlphabet                  = str(addon.getSetting('viewIDAlphabet'))
viewIDShows                      = str(addon.getSetting('viewIDShows'))
viewIDVideos                      = str(addon.getSetting('viewIDVideos'))
BASE_API                             = 'https://www.kika.de/api/v1/kikaplayer/kikaapp'
BASE_URL                             = 'https://www.kika.de'

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

def _header(kika_REFERRER=None):
	header = {}
	header['Connection'] = 'keep-alive'
	header['User-Agent'] = get_userAgent()
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'en-US,en;q=0.8,de;q=0.7'
	if kika_REFERRER:
		header['Referer'] = kika_REFERRER
	return header

def getUrl(url, method='GET', REF='Unknown', headers=None, cookies=None, allow_redirects=False, verify=True, stream=None, data=None, json=None):
	simple = requests.Session()
	kika_REF = (None if REF == 'Unknown' else REF)
	result = None
	simple.headers.update(_header(kika_REF))
	try:
		if method == 'GET':
			result = simple.get(url, headers=headers, allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=40)
			result = py2_enc(result.text)
		elif method == 'POST':
			result = simple.post(url, headers=headers, allow_redirects=allow_redirects, verify=verify, data=data, json=json, timeout=40)
		debug_MS("(common.getUrl) === send url-HEADERS : {0} ===".format(str(simple.headers)))
	except requests.exceptions.RequestException as e:
		failure = str(e)
		failing("(common.getUrl) ERROR - ERROR - ERROR : ##### {0} === {1} #####".format(url, failure))
		dialog.notification(translation(30521).format('URL'), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
		return sys.exit(0)
	return result

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

def get_Seconds(info):
	try:
		info = re.sub('[a-z]', '', info)
		first = info.split(':')[0]
		if len(info) > 5 and len(first) < 3:
			h, m, s = info.split(':')
			return int(h)*3600+int(m)*60+int(s)
		elif len(info) < 6 or len(first) > 2:
			m, s = info.split(':')
			return int(m)*60+int(s)
	except: return '0'

def cleaning(text):
	text = py2_enc(text)
	for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;amp;', '&'), ('&amp;', '&'), ('&apos;', "'"), ("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('►', '>'),
				('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''), ('\xc2\xb7', '-'),
				('&quot;', '"'), ('&szlig;', 'ß'), ('&ndash;', '-'), ('&Auml;', 'Ä'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&ouml;', 'ö'), ('&uuml;', 'ü'),
				('&agrave;', 'à'), ('&aacute;', 'á'), ('&acirc;', 'â'), ('&egrave;', 'è'), ('&eacute;', 'é'), ('&ecirc;', 'ê'), ('&igrave;', 'ì'), ('&iacute;', 'í'), ('&icirc;', 'î'),
				('&ograve;', 'ò'), ('&oacute;', 'ó'), ('&ocirc;', 'ô'), ('&ugrave;', 'ù'), ('&uacute;', 'ú'), ('&ucirc;', 'û'),
				("\\'", "'"), ('KIKA - ', ''), ('KiKA - ', ''), ('Folgenübersicht', ''), ('Folge vom ', ''), ('| ', '')):
				text = text.replace(*n)
				if 'Rechte:' in text: text=text.split('Rechte:')[0]
	return text.strip()

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
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', 'root'))
extras  = unquote_plus(params.get('extras', 'standard'))
IDENTiTY = unquote_plus(params.get('IDENTiTY', ''))

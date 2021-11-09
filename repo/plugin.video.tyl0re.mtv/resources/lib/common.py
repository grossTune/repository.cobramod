# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import platform
import json
import xbmcvfs
import shutil
import socket
import time
from datetime import datetime, timedelta
import calendar
from collections import OrderedDict
from bs4 import BeautifulSoup
import requests
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote_plus, unquote_plus  # Python 2.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmc.translatePath, xbmc.LOGNOTICE, 'inputstreamaddon' # Stand: 05.12.20 / Python 2.X
else:
	from urllib.parse import urlencode, quote_plus, unquote_plus  # Python 3.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmcvfs.translatePath, xbmc.LOGINFO, 'inputstream' # Stand: 05.12.20  / Python 3.X
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
try: import StorageServer
except: from . import storageserverdummy as StorageServer


global debuging
socket.setdefaulttimeout(40)
HOST_AND_PATH                = sys.argv[0]
ADDON_HANDLE                 = int(sys.argv[1])
dialog                                     = xbmcgui.Dialog()
addon                                     = xbmcaddon.Addon()
addon_id                               = addon.getAddonInfo('id')
addon_name                        = addon.getAddonInfo('name')
addon_version                     = addon.getAddonInfo('version')
addonPath                            = TRANS_PATH(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath                               = TRANS_PATH(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
tempSF                                  = TRANS_PATH(os.path.join(dataPath, 'subs', '')).encode('utf-8').decode('utf-8')
defaultFanart                       = (os.path.join(addonPath, 'fanart.jpg') if PY2 else os.path.join(addonPath, 'resources', 'media', 'fanart.jpg'))
icon                                        = (os.path.join(addonPath, 'icon.png') if PY2 else os.path.join(addonPath, 'resources', 'media', 'icon.png'))
artpic                                     = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
alppic                                     = os.path.join(addonPath, 'resources', 'media', 'alphabet', '').encode('utf-8').decode('utf-8')
cachePERIOD                      = int(addon.getSetting('cache_rhythm'))
cache                                     = StorageServer.StorageServer(addon_id, cachePERIOD) # (Your plugin name, Cache time in hours)
enableINPUTSTREAM         = addon.getSetting('useInputstream') == 'true'
enableSUBTITLE                  = addon.getSetting('show_subtitles') == 'true'
showALL                                = addon.getSetting('show_complete') == 'true'
useThumbAsFanart             = addon.getSetting('useThumbAsFanart') == 'true'
enableADJUSTMENT           = addon.getSetting('show_settings') == 'true'
DEB_LEVEL                           = (LOG_MESSAGE if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
BASE_URL                             = 'http://www.mtv.de'
response                               = requests.Session()

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

def get_Description(info):
	depl = ""
	if 'fullDescription' in info and info['fullDescription'] and len(info['fullDescription']) > 10:
		depl = cleaning(info['fullDescription'])
	if depl == "" and 'description' in info and info['description'] and len(info['description']) > 10:
		depl = cleaning(info['description'])
	if depl == "" and 'shortDescription' in info and info['shortDescription'] and len(info['shortDescription']) > 10:
		depl = cleaning(info['shortDescription'])
	return depl

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

def clearCache():
	debug_MS("(common.clearCache) -------------------------------------------------- START = clearCache --------------------------------------------------")
	debug_MS("(common.clearCache) ========== Lösche jetzt den Addon-Cache ==========")
	cache.delete('%')
	xbmc.sleep(1000)
	dialog.ok(addon_id, translation(30502))

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

def build_url(query):
	return '{0}?{1}'.format(HOST_AND_PATH, urlencode(query))

def makeREQUEST(url, method='GET', REF='Unknown', XMLH=False):
	return cache.cacheFunction(getUrl, url, method, REF, XMLH)

def load_header(REF, XMLH):
	if REF is 'Unknown':
		HEADERS = response.headers.update({'User-Agent': get_userAgent()})
	else:
		HEADERS = response.headers.update({'User-Agent': get_userAgent(), 'Referer': REF})
	if XMLH is True:
		HEADERS = response.headers.update({'Host': 'www.mtv.de', 'DNT': '1', 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'})
	return HEADERS

def get_userAgent():
	base = 'Mozilla/5.0 {0} AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
	system = platform.system()
	if system == 'Darwin':
		return base.format('(Macintosh; Intel Mac OS X 10_10_1)') # Mac OSX
	if system == 'Windows':
		return base.format('(Windows NT 10.0; WOW64)') # Windows
	if platform.machine().startswith('arm'):
		return base.format('(X11; CrOS armv7l 7647.78.0)') # ARM based Linux
	return base.format('(X11; Linux x86_64)') # x86 Linux

def getUrl(url, method='GET', REF='Unknown', XMLH=False, headers=None, cookies=None, allow_redirects=True, verify=True, stream=None, data=None):
	if headers is None:
		headers = load_header(REF, XMLH)
	try:
		if method == 'GET':
			content = response.get(url, headers=headers, allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=40)
			if stream is None:
				content = py2_enc(content.text)
		elif method == 'POST':
			content = response.post(url, headers=headers, allow_redirects=allow_redirects, verify=verify, data=data, timeout=40)
	except requests.exceptions.RequestException as e:
		failure = str(e)
		failing("(common.getUrl) ERROR - ERROR - ERROR : ##### {0} === {1} #####".format(url, failure))
		dialog.notification(translation(30521).format('URL'), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
		return sys.exit(0)
	return content

def utc_to_local(utcDT):
	timestamp = calendar.timegm(utcDT.timetuple())
	localDT = datetime.fromtimestamp(timestamp)
	assert utcDT.resolution >= timedelta(microseconds=1)
	return localDT.replace(microsecond=utcDT.microsecond)

def cleaning(text):
	text = py2_enc(text)
	for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&apos;', "'"), ("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('►', '>'),
				('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''), ('\xc2\xb7', '-'),
				('&quot;', '"'), ('&szlig;', 'ß'), ('&ndash;', '-'), ('&Auml;', 'Ä'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&ouml;', 'ö'), ('&uuml;', 'ü'),
				('&agrave;', 'à'), ('&aacute;', 'á'), ('&acirc;', 'â'), ('&egrave;', 'è'), ('&eacute;', 'é'), ('&ecirc;', 'ê'), ('&igrave;', 'ì'), ('&iacute;', 'í'), ('&icirc;', 'î'),
				('&ograve;', 'ò'), ('&oacute;', 'ó'), ('&ocirc;', 'ô'), ('&ugrave;', 'ù'), ('&uacute;', 'ú'), ('&ucirc;', 'û'), ("\\'", "'")):
				text = text.replace(*n)
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
image = unquote_plus(params.get('image', ''))
transmit = unquote_plus(params.get('transmit', 'special'))
extras = unquote_plus(params.get('extras', 'standard'))
cineType = unquote_plus(params.get('cineType', 'movie'))

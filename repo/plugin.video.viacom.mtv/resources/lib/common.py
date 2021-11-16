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
import random
import time
from datetime import datetime, timedelta
from calendar import timegm as TGM
from collections import OrderedDict
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
from .provider import Client


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
tempSF                                  = TRANS_PATH(os.path.join(dataPath, 'subs', '')).encode('utf-8').decode('utf-8')
WORKFILE                            = os.path.join(dataPath, 'episode_data.json')
defaultFanart                       = (os.path.join(addonPath, 'fanart.jpg') if PY2 else os.path.join(addonPath, 'resources', 'media', 'fanart.jpg'))
icon                                        = (os.path.join(addonPath, 'icon.png') if PY2 else os.path.join(addonPath, 'resources', 'media', 'icon.png'))
artpic                                     = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
chapic                                    = os.path.join(addonPath, 'resources', 'media', 'charts', '').encode('utf-8').decode('utf-8')
cachePERIOD                      = int(addon.getSetting('cache_rhythm'))
cache                                     = StorageServer.StorageServer(addon_id, cachePERIOD) # (Your plugin name, Cache time in hours)
enableINPUTSTREAM         = addon.getSetting('useInputstream') == 'true'
enableINFOS                        = addon.getSetting('showInfo') == 'true'
infoDelay                               = int(addon.getSetting('infoDelay'))
infoDuration                         = int(addon.getSetting('infoDuration'))
showALL                                = addon.getSetting('show_complete') == 'true'
useThumbAsFanart             = addon.getSetting('useThumbAsFanart') == 'true'
enableSUBTITLE                  = addon.getSetting('show_subtitles') == 'true'
enableADJUSTMENT           = addon.getSetting('show_settings') == 'true'
DEB_LEVEL                           = (LOG_MESSAGE if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
BASE_URL                             = 'https://www.mtv.de/'
traversing                              = Client(Client.CONFIG_MTVDE)

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

def makeREQUEST(url, method='GET', REF=None):
	return cache.cacheFunction(getUrl, url, method, REF)

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

def _header(REFERRER=None):
	header = {}
	header['Connection'] = 'keep-alive'
	header['Pragma'] = 'no-cache'
	header['Cache-Control'] = 'no-cache'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'en-US,en;q=0.8,de;q=0.7'
	if REFERRER:
		header['Referer'] = REFERRER
	return header

def getUrl(url, method='GET', REF=None, headers=None, cookies=None, allow_redirects=True, verify=True, stream=None, data=None, json=None):
	simple = requests.Session()
	debug_MS("(common.getUrl) === URL that wanted : {0} ===".format(url))
	result = None
	simple.headers.update(_header(REF))
	try:
		if method == 'GET':
			result = simple.get(url, headers=headers, allow_redirects=allow_redirects, verify=verify, stream=stream, timeout=40)
			if stream is None:
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

def clearCache():
	debug_MS("(common.clearCache) -------------------------------------------------- START = clearCache --------------------------------------------------")
	debug_MS("(common.clearCache) ========== Lösche jetzt den Addon-Cache ==========")
	cache.delete('%')
	xbmc.sleep(1000)
	dialog.ok(addon_id, translation(30502))

def get_Local_DT(info):
	fixed_format = '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':') # 2019-09-20T22:10:00.000+0000
	utcDT = datetime(*(time.strptime(info, fixed_format)[0:6]))
	try:
		localDT = datetime.fromtimestamp(TGM(utcDT.timetuple()))
		assert utcDT.resolution >= timedelta(microseconds=1)
		localDT = localDT.replace(microsecond=utcDT.microsecond)
	except (ValueError, OverflowError): # ERROR on Android 32bit Systems = cannot convert unix timestamp over year 2038
		localDT = datetime.fromtimestamp(0) + timedelta(seconds=TGM(utcDT.timetuple()))
		localDT = localDT - timedelta(hours=datetime.timetuple(localDT).tm_isdst)
	return localDT

def get_Description(info):
	if 'fullDescription' in info and info['fullDescription'] and len(info['fullDescription']) > 10:
		return cleaning(info['fullDescription'])
	elif 'description' in info and info['description'] and len(info['description']) > 10:
		return cleaning(info['description'])
	elif 'shortDescription' in info and info['shortDescription'] and len(info['shortDescription']) > 10:
		return cleaning(info['shortDescription'])
	return ""

def getSorting():
	method = [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DURATION, xbmcplugin.SORT_METHOD_EPISODE, xbmcplugin.SORT_METHOD_DATE]
	return method

def cleanPlaylist():
	playlist = xbmc.PlayList(1)
	playlist.clear()
	return playlist

def cleaning(text):
	text = py2_enc(text)
	for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
				("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''),
				('&#xC4;', 'Ä'), ('&#xE4;', 'ä'), ('&#xD6;', 'Ö'), ('&#xF6;', 'ö'), ('&#xDC;', 'Ü'), ('&#xFC;', 'ü'), ('&#xDF;', 'ß'), ('&#x201E;', '„'), ('&#xB4;', '´'), ('&#x2013;', '-'), ('&#xA0;', ' '),
				('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&#376;', 'Ÿ'), ('&yuml;', 'ÿ'),
				('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'),
				('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'Ó'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'),
				('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
				('&atilde;', 'ã'), ('&Atilde;', 'Ã'), ('&ntilde;', 'ñ'), ('&Ntilde;', 'Ñ'), ('&otilde;', 'õ'), ('&Otilde;', 'Õ'), ('&Scaron;', 'Š'), ('&scaron;', 'š'), ('&ccedil;', 'ç'), ('&Ccedil;', 'Ç'),
				('&alpha;', 'a'), ('&Alpha;', 'A'), ('&aring;', 'å'), ('&Aring;', 'Å'), ('&aelig;', 'æ'), ('&AElig;', 'Æ'), ('&epsilon;', 'e'), ('&Epsilon;', 'Ε'), ('&eth;', 'ð'), ('&ETH;', 'Ð'), ('&gamma;', 'g'), ('&Gamma;', 'G'),
				('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('<br />', ' - '),
				("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
				('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ('\\x20', ' '), ('\\x3A', ':'), ("\\'", "'")):
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
pict = unquote_plus(params.get('pict', ''))
type = unquote_plus(params.get('type', 'browse'))
extras = unquote_plus(params.get('extras', 'standard'))
page = unquote_plus(params.get('page', '1'))
transmit = unquote_plus(params.get('transmit', 'special'))
shortTITLE = unquote_plus(params.get('shortTITLE', 'NOT FOUND'))
IDENTiTY = unquote_plus(params.get('IDENTiTY', ''))
cineType = unquote_plus(params.get('cineType', 'movie'))

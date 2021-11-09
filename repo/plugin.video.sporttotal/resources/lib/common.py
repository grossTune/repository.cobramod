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
import time
from datetime import datetime, timedelta
import calendar
import io
import gzip
from collections import OrderedDict
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote, unquote, quote_plus, unquote_plus  # Python 2.X
	from urllib2 import urlopen, build_opener  # Python 2.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmc.translatePath, xbmc.LOGNOTICE, 'inputstreamaddon' # Stand: 06.12.20 / Python 2.X
else:
	from urllib.parse import urlencode, quote, unquote, quote_plus, unquote_plus  # Python 3+
	from urllib.request import urlopen, build_opener  # Python 3+
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmcvfs.translatePath, xbmc.LOGINFO, 'inputstream' # Stand: 06.12.20  / Python 3.X


global debuging
HOST_AND_PATH                 = sys.argv[0]
ADDON_HANDLE                  = int(sys.argv[1])
dialog                                      = xbmcgui.Dialog()
addon                                     = xbmcaddon.Addon()
addon_id                                = addon.getAddonInfo('id')
addon_name                         = addon.getAddonInfo('name')
addon_version                      = addon.getAddonInfo('version')
addonPath                             = TRANS_PATH(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath                                = TRANS_PATH(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
defaultFanart                        = (os.path.join(addonPath, 'fanart.jpg') if PY2 else os.path.join(addonPath, 'resources', 'media', 'fanart.jpg'))
icon                                         = (os.path.join(addonPath, 'icon.png') if PY2 else os.path.join(addonPath, 'resources', 'media', 'icon.png'))
artpic                                      = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
langSHORTCUT                     = {0: 'de', 1: 'en', 2: 'fr', 3: 'it', 4: 'nl'}[int(addon.getSetting('language'))]
# Spachennummerierung(settings) ~ German=0|English=1|French=2|Italian=3|Dutch=4
#         Webseitenkürzel(sporttotal) = 0: de|1: en|2: fr|3: it|4: nl
enableINPUTSTREAM          = addon.getSetting('useInputstream') == 'true'
enableADJUSTMENT            = addon.getSetting('show_settings') == 'true'
DEB_LEVEL                            = (LOG_MESSAGE if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
BASE_URL                              = 'https://www.sporttotal.tv/'

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

def getUrl(url, header=None, data=None, agent='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0'):
	opener = build_opener()
	opener.addheaders = [('User-Agent', agent), ('Accept-Encoding', 'gzip, identity')]
	try:
		if header: opener.addheaders = header
		response = opener.open(url, data, timeout=30)
		if response.info().get('Content-Encoding') == 'gzip':
			link = py3_dec(gzip.GzipFile(fileobj=io.BytesIO(response.read())).read())
		else:
			link = py3_dec(response.read())
	except Exception as e:
		failure = str(e)
		failing("(common.getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		dialog.notification(translation(30521).format('URL'), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 15000)
		return sys.exit(0)
	return py2_enc(link)

def utc_to_local(utcDT):
	timestamp = calendar.timegm(utcDT.timetuple())
	localDT = datetime.fromtimestamp(timestamp)
	assert utcDT.resolution >= timedelta(microseconds=1)
	return localDT.replace(microsecond=utcDT.microsecond)

def cleaning(text):
	text = py2_enc(text)
	for n in (("&#39;", "'"), ('&#196;', 'Ä'), ('&#214;', 'Ö'), ('&#220;', 'Ü'), ('&#228;', 'ä'), ('&#246;', 'ö'), ('&#252;', 'ü'), ('&#223;', 'ß'), ('&#160;', ' '),
				('&#192;', 'À'), ('&#193;', 'Á'), ('&#194;', 'Â'), ('&#195;', 'Ã'), ('&#197;', 'Å'), ('&#199;', 'Ç'), ('&#200;', 'È'), ('&#201;', 'É'), ('&#202;', 'Ê'),
				('&#203;', 'Ë'), ('&#204;', 'Ì'), ('&#205;', 'Í'), ('&#206;', 'Î'), ('&#207;', 'Ï'), ('&#209;', 'Ñ'), ('&#210;', 'Ò'), ('&#211;', 'Ó'), ('&#212;', 'Ô'),
				('&#213;', 'Õ'), ('&#215;', '×'), ('&#216;', 'Ø'), ('&#217;', 'Ù'), ('&#218;', 'Ú'), ('&#219;', 'Û'), ('&#221;', 'Ý'), ('&#222;', 'Þ'), ('&#224;', 'à'),
				('&#225;', 'á'), ('&#226;', 'â'), ('&#227;', 'ã'), ('&#229;', 'å'), ('&#231;', 'ç'), ('&#232;', 'è'), ('&#233;', 'é'), ('&#234;', 'ê'), ('&#235;', 'ë'),
				('&#236;', 'ì'), ('&#237;', 'í'), ('&#238;', 'î'), ('&#239;', 'ï'), ('&#240;', 'ð'), ('&#241;', 'ñ'), ('&#242;', 'ò'), ('&#243;', 'ó'), ('&#244;', 'ô'),
				('&#245;', 'õ'), ('&#247;', '÷'), ('&#248;', 'ø'), ('&#249;', 'ù'), ('&#250;', 'ú'), ('&#251;', 'û'), ('&#253;', 'ý'), ('&#254;', 'þ'), ('&#255;', 'ÿ'),
				('&#352;', 'Š'), ('&#353;', 'š'), ('&#376;', 'Ÿ'), ('&#402;', 'ƒ'),
				('&#8211;', '–'), ('&#8212;', '—'), ('&#8226;', '•'), ('&#8230;', '…'), ('&#8240;', '‰'), ('&#8364;', '€'), ('&#8482;', '™'), ('&#169;', '©'), ('&#174;', '®'),
				("&Auml;", "Ä"), ("&Uuml;", "Ü"), ("&Ouml;", "Ö"), ("&auml;", "ä"), ("&uuml;", "ü"), ("&ouml;", "ö"), ('&quot;', '"'), ('&szlig;', 'ß'), ('&ndash;', '-'),
				('/xc3/x84', 'Ä'), ('/xc3/xa4', 'ä'), ('/xc3/x96', 'Ö'), ('/xc3/xb6', 'ö'), ('/xc3/x9c', 'Ü'), ('/xc3/xbc', 'ü'), ('/xc3/x9f', 'ß')):
				text = text.replace(*n)
	return text.strip()

def cleanPhoto(img): # UNICODE-Zeichen für Browser übersetzen - damit Fotos angezeigt werden
	img = py2_enc(img)
	for p in ((' ', '%20'), ('ß', '%C3%9F'), ('ä', '%C3%A4'), ('ö', '%C3%B6'), ('ü', '%C3%BC'),
				('à', '%C3%A0'), ('á', '%C3%A1'), ('â', '%C3%A2'), ('è', '%C3%A8'), ('é', '%C3%A9'), ('ê', '%C3%AA'), ('ì', '%C3%AC'), ('í', '%C3%AD'), ('î', '%C3%AE'),
				('ò', '%C3%B2'), ('ó', '%C3%B3'), ('ô', '%C3%B4'), ('ù', '%C3%B9'), ('ú', '%C3%BA'), ('û', '%C3%BB')):
				img = img.replace(*p)
	return img.strip()

def browse_All(iterable, sendback='value'): # Returns an iterator that returns all values of a (nested) iterable.
	if isinstance(iterable, dict):
		for key, value in iterable.items():
			if not (isinstance(value, dict) or isinstance(value, list)):
				yield value
			for ret in browse_All(value, sendback=sendback):
				yield ret
	elif isinstance(iterable, list):
		for el in iterable:
			for ret in browse_All(el, sendback=sendback):
				yield ret

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
filtermod = unquote_plus(params.get('filtermod', 'standard'))
category = unquote_plus(params.get('category', ''))
picture = unquote_plus(params.get('picture', icon))
background = unquote_plus(params.get('background', 'standard'))

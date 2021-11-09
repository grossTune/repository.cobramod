# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import time
from datetime import datetime, timedelta
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote  # Python 2.X
else: 
	from urllib.parse import urlencode, quote  # Python 3.X

from .common import *
from .records import get_ListItem
from .utilities import Transmission


if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def getUrl(url, method='GET', REF=None, send_token=None):
	content = Transmission().retrieveContent(url, method, REF, send_token)
	return content

def mainMenu():
	debug_MS("(navigator.mainMenu) -------------------------------------------------- START = mainMenu --------------------------------------------------")
	addDir(translation(30601), artpic+'favourites.png', {'mode': 'listShowsFavs'})
	addDir(translation(30602), icon, {'mode': 'listGeneralFull', 'url': 'calendar', 'phrase': 'products'})
	addDir(translation(30603), icon, {'mode': 'listGeneralFull', 'url': 'latest-videos', 'phrase': 'collections'})
	addDir(translation(30604), icon, {'mode': 'listGeneralFull', 'url': 'e2fda2e1-58ff-4474-a49a-a2df01309998', 'phrase': 'collections'})
	addDir(translation(30605), icon, {'mode': 'listGeneralFull', 'url': 'discover-featured', 'phrase': 'collections'})
	addDir(translation(30606), icon, {'mode': 'listGeneralFull', 'url': 'subchannels', 'phrase': 'collections'})
	addDir(translation(30607), icon, {'mode': 'listGeneralFull', 'url': 'films', 'phrase': 'products'})
	addDir(translation(30608), icon, {'mode': 'listGeneralFull', 'url': 'shows', 'phrase': 'products'})
	addDir(translation(30609), icon, {'mode': 'listGeneralFull', 'url': 'discover', 'phrase': 'products'})
	addDir(translation(30610), artpic+'basesearch.png', {'mode': 'SearchSERVUSTV'})
	addDir(translation(30611), artpic+'livestream.png', {'mode': 'playLIVE'}, folder=False)
	ACCESS, CANTON = Transmission().load_credentials()
	if CANTON:
		CN = CANTON.replace('ch', 'suisse').replace('at', translation(30623)).replace('de', translation(30624)).replace('suisse', translation(30625))
		TEXTBOX = translation(30621).format(CN)
	else: TEXTBOX = translation(30622)
	if textSelection == '0': chronology = translation(30612)+TEXTBOX
	elif textSelection == '1': chronology = TEXTBOX+translation(30612)
	elif textSelection == '2': chronology = TEXTBOX
	else: chronology = translation(30612)
	if enableADJUSTMENT:
		addDir(chronology, artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if ADDON_operate('inputstream.adaptive'):
			addDir(translation(30613), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	else:
		addDir(TEXTBOX, icon, {'mode': 'blankFUNC'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)

def unsubscribe():
	debug_MS("(navigator.unsubscribe) -------------------------------------------------- START = unsubscribe --------------------------------------------------")
	if xbmcvfs.exists(tokenFile) and os.path.isdir(tempTN):
		debug_MS("(navigator.unsubscribe) XXXXX USER FORCE REMOVING TOKEN - DELETE TOKENFILE XXXXX")
		shutil.rmtree(tempTN, ignore_errors=True)
		return dialog.notification(translation(30528), translation(30529), icon, 8000)
	return dialog.ok(addon_id, translation(30502))

def listGeneralFull(url, phrase, QUERY, PAGE, LIMIT):
	debug_MS("(navigator.listGeneralFull) -------------------------------------------------- START = listGeneralFull --------------------------------------------------")
	debug_MS("(navigator.listGeneralFull) ### URL : {0} || PHRASE : {1} || QUERY : {2} || PAGE : {3} || LIMIT : {4} ###".format(url, phrase, QUERY, PAGE, LIMIT))
	FOUND = 0
	SWAPPED = '{0}?q={1}&'.format(phrase, QUERY) if QUERY != 'None' else '{0}/{1}?'.format(phrase, url)
	# https://api.redbull.tv/v3/collections/subchannels?namespace=stv&assets=vr&limit=20&offset=0
	# https://api.redbull.tv/v3/products/shows?namespace=stv&assets=vr&limit=20&offset=0
	# https://api.redbull.tv/v3/playlists/AA-1Y5RJCD1H2111:all_episodes?namespace=stv&assets=vr&limit=20&offset=0
	# https://api.redbull.tv/v3/search?q=nachrichten&namespace=stv&assets=vr&limit=20&offset=0
	NEW_URL = '{0}{1}namespace=stv&assets=vr&limit={2}&offset={3}'.format(SERVUSTV_API, SWAPPED, str(LIMIT), str((int(PAGE) - 1) * int(LIMIT)))
	content = getUrl(NEW_URL, send_token=True)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listGeneralFull) CONTENT : {0}".format(str(content)))
	debug_MS("++++++++++++++++++++++++")
	DATA = json.loads(content)
	aback, GAP = DATA, DATA
	if DATA.get('links', ''):
		for link in DATA.get('links', []):
			FOUND += 1
			LINKING(link, 'PRODUCT', phrase, '(list[LINKS])', aback)
	if DATA.get('collections', ''):
		if DATA.get('collections', [])[0].get('collection_type', '') == 'top_results' and QUERY != 'None':
			GAP = DATA['collections'][0] # give Searchresults to next Level
		else:
			for collection in DATA.get('collections', []):
				FOUND += 1
				LINKING(collection, 'COLLECTION', phrase, '(list[COLLECTIONS])', aback)
	if GAP.get('items', ''):
		CAT = 'THEME' if 'subchannels' in url else 'PRODUCT'
		for item in GAP.get('items', []):
			if item.get('type', '') == 'video' and item.get('content_type', '') != 'live_program' and (item.get('playable', '') is False or not item.get('duration', '')):
				continue
			FOUND += 1
			LINKING(item, CAT, phrase, '(list[ITEMS])', aback)
	if FOUND == 0:
		return dialog.notification(translation(30522).format('Ergebnisse'), translation(30524), icon, 8000)
	if GAP.get('meta', ''):
		if 'total' in GAP['meta'] and isinstance(GAP['meta']['total'], int) and int(GAP['meta']['total']) > int(LIMIT)*int(PAGE):
			debug_MS("(navigator.listGeneralFull) Now show NextPage ...")
			addDir(translation(30632).format(int(PAGE)+1), artpic+'nextpage.png', {'mode': 'listGeneralFull', 'url': url, 'phrase': phrase, 'searching': QUERY,  'page': int(PAGE)+1})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listThemes(url, phrase, PAGE, LIMIT):
	debug_MS("(navigator.listThemes) -------------------------------------------------- START = listThemes --------------------------------------------------")
	debug_MS("(navigator.listThemes) ### URL : {0} || PHRASE : {1} || PAGE : {2} || LIMIT : {3} ###".format(url, phrase, PAGE, LIMIT))
	FOUND = 0
	FIRST_COMBI = []
	# https://api.redbull.tv/v3/products/news?namespace=stv&assets=vr&limit=20&offset=0
	special = ['/news', '/sports', '/nature', '/folk-culture', '/culture', '/entertainment', '/science']
	newURL = '{0}products/{1}?namespace=stv&assets=vr&limit={2}&offset={3}'.format(SERVUSTV_API, url, str(LIMIT), str((int(PAGE) - 1) * int(LIMIT)))
	content = getUrl(newURL, send_token=True)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listThemes) CONTENT_01 : {0}".format(str(content)))
	debug_MS("++++++++++++++++++++++++")
	DATA_1 = json.loads(content)
	aback = DATA_1
	if DATA_1.get('collections', ''):
		for collection in DATA_1.get('collections', []):
			firsttitle = ""
			if collection.get('label', ''): 
				firsttitle = py2_enc(collection.get('label'))
			if 'Mehr zu: ' in firsttitle:
				continue
			FIRST_COMBI.append(firsttitle.lower())
			FOUND += 1
			LINKING(collection, 'COLLECTION', phrase, '(list[THEMES], no.1)', aback)
	if any(x in newURL.strip().lower() for x in special):
		# https://api.redbull.tv/v3/collections/news-latest-shows?namespace=stv&assets=vr&limit=20&offset=0
		suffixURL = '{0}collections/{1}-latest-shows?namespace=stv&assets=vr&limit={2}&offset={3}'.format(SERVUSTV_API, url, str(LIMIT), str((int(PAGE) - 1) * int(LIMIT)))
		result = getUrl(suffixURL, send_token=True)
		debug_MS("++++++++++++++++++++++++")
		debug_MS("(navigator.listThemes) RESULT_02 : {0}".format(str(result)))
		debug_MS("++++++++++++++++++++++++")
		DATA_2 = json.loads(result)
		if DATA_2.get('items', ''):
			for item in DATA_2.get('items', []):
				if str(py2_enc(item.get('title'))).lower() not in FIRST_COMBI:
					FOUND += 1
					LINKING(item, 'PRODUCT', phrase, '(list[THEMES], no.2)', aback)
	if FOUND == 0:
		return dialog.notification(translation(30522).format('Ergebnisse'), translation(30524), icon, 8000)
	if DATA_1.get('meta', ''):
		if 'total' in DATA_1['meta'] and isinstance(DATA_1['meta']['total'], int) and int(DATA_1['meta']['total']) > int(LIMIT)*int(PAGE):
			debug_MS("(navigator.listThemes) Now show NextPage ...")
			addDir(translation(30632).format(int(PAGE)+1), artpic+'nextpage.png', {'mode': 'listThemes', 'url': url, 'phrase': phrase, 'page': int(PAGE)+1})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchSERVUSTV():
	debug_MS("(navigator.SearchSERVUSTV) ------------------------------------------------ START = SearchSERVUSTV -----------------------------------------------")
	# https://api.redbull.tv/v3/search?q=nachrichten&namespace=stv&assets=vr&limit=20&offset=0
	keyword = None
	suffix = '&collection_type=top_results'
	if xbmcvfs.exists(searchHackFile):
		with open(searchHackFile, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30633), type=xbmcgui.INPUT_ALPHANUM, autoclose=10000)
		if keyword:
			keyword = quote(keyword)
			with open(searchHackFile, 'w') as record:
				record.write(keyword)
	if keyword: return listGeneralFull('enquiries', 'search', keyword+suffix, page, limit)
	return None

def playVideo(eid):
	debug_MS("(navigator.playVideo) ------------------------------------------------ START = playVideo -----------------------------------------------")
	# https://dms.redbull.tv/v3/AA-26AMCEPYH2111/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYXRlZ29yeSI6InNtYXJ0cGhvbmUiLCJjb3VudHJ5X2NvZGUiOiJkZSIsImV4cGlyZXMiOiIyMDIxLTAzLTI5VDE4OjAwOjA4LjE0NzMxNDgwOFoiLCJsb2NhbGUiOiJkZSIsIm9zX2ZhbWlseSI6ImFuZHJvaWQiLCJyZW1vdGVfaXAiOiI5Mi4xMTYuNTguODMiLCJ1YSI6IkFuZHJvaWQvNC42LjEuMTQiLCJ1aWQiOiI2NzU1ZTY5Mi03NTA2LTQwNWYtOTAwYy03ZjgzNDJjMmY4Y2IifQ.y5kQut_aQB6eHi7npL0636JUhnVkWMZLlfetmKrG0sA/playlist.m3u8?namespace=stv
	ACCESS, CANTON = Transmission().load_credentials()
	if ACCESS:
		finalURL = '{0}{1}/{2}/playlist.m3u8?namespace=stv'.format(SERVUSTV_HLS, eid, ACCESS)
		log("(navigator.playVideo) HLS_stream : {0} ".format(finalURL))
		listitem = xbmcgui.ListItem(path=finalURL)
		listitem.setContentLookup(False)
		listitem.setMimeType('application/x-mpegURL')
		if ADDON_operate('inputstream.adaptive'):
			listitem.setProperty(INPUT_APP, 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem)
	else:
		failing("(navigator.playVideo) ##### Das Video ist nicht abspielbar, der erforderliche Token wurde leider NICHT gefunden !!! #####")

def playLIVE():
	debug_MS("(navigator.playLIVE) ------------------------------------------------ START = playLIVE -----------------------------------------------")
	# NEW = https://dms.redbull.tv/v3/stv-linear/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjYXRlZ29yeSI6InBlcnNvbmFsX2NvbXB1dGVyIiwiY291bnRyeV9jb2RlIjoidXMiLCJleHBpcmVzIjoiMjAxNy0wOS0xNlQxNzo0NjowMy45NjM0NjI4NDJaIiwib3NfZmFtaWx5IjoiaHR0cCIsInJlbW90ZV9pcCI6IjEwLjE1Ny4xMTIuMTQ4IiwidWEiOiJNb3ppbGxhLzUuMCAoTWFjaW50b3NoOyBJbnRlbCBNYWMgT1MgWCAxMF8xMl81KSBBcHBsZVdlYktpdC82MDMuMi40IChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi8xMC4xLjEgU2FmYXJpLzYwMy4yLjQiLCJ1aWQiOiJkOGZiZWYzMC0yZDhhLTQwYTUtOGNjNy0wNzgxNGJhMTliNzMifQ.Q_38FNpW3so5yrA5FQt9qBuix3dTulKpb6uQ0dRjrtY/playlist.m3u8
	# https://rbmn-live.akamaized.net/hls/live/2002830/geoSTVDEmob/master.m3u8
	# https://rbmn-live.akamaized.net/hls/live/2002825/geoSTVATmob/master.m3u8#
	ACCESS, CANTON = Transmission().load_credentials()
	if ACCESS:
		title = translation(30642) if CANTON and CANTON in ['at', 'ch'] else translation(30641)
		if streamVersion == '0':
			stream_url = 'https://rbmn-live.akamaized.net/hls/live/2002830/geoSTVDEweb/master.m3u8'
			if CANTON and CANTON in ['at', 'ch']:
				stream_url = 'https://rbmn-live.akamaized.net/hls/live/2002825/geoSTVATweb/master.m3u8'
		else:
			stream_url = '{0}stv-linear/{1}/playlist.m3u8?namespace=stv'.format(SERVUSTV_HLS, ACCESS)
		log("(navigator.playLIVE) ### LIVE-URL : {0} ###".format(stream_url))
		listitem = xbmcgui.ListItem(path=stream_url, label=title)
		listitem.setContentLookup(False)
		listitem.setMimeType('application/x-mpegURL')
		if ADDON_operate('inputstream.adaptive'):
			listitem.setProperty(INPUT_APP, 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
			listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
		xbmc.Player().play(item=stream_url, listitem=listitem)
	else:
		failing("(navigator.playLIVE) ##### Der Stream ist nicht abspielbar, der erforderliche Token wurde leider NICHT gefunden !!! #####")

def listShowsFavs():
	debug_MS("(navigator.listShowsFavs) ------------------------------------------------ START = listShowsFavs -----------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as fp:
			watch = json.load(fp)
			for item in watch.get('items', []):
				title = py2_enc(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else item.get('pict')
				desc = None if item.get('plot', 'None') == 'None' else py2_enc(item.get('plot'))
				debug_MS("(navigator.listShowsFavs) ### NAME : {0} || URL : {1} || IMAGE : {2} || cineType : {3} ###".format(title, item.get('url'), logo, item.get('cineType')))
				addDir(title, logo, {'mode': 'listGeneralFull', 'url': item.get('url'), 'wallpaper': item.get('wallpaper'), 'cineType': item.get('cineType')}, desc, FAVclear=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'plot': plot, 'wallpaper': wallpaper, 'cineType': cineType})
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30530), translation(30531).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('url') != url]
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30530), translation(30532).format(name), icon, 8000)

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def LINKING(info, category=None, phrase=None, extras=None, aback=None):
	uv, liz, folder = get_ListItem(info, category, phrase, extras, aback)
	if liz is None: return
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=uv, listitem=liz, isFolder=folder)

def addDir(name, image, params={}, plot=None, FAVclear=False, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Studio': 'ServusTV'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if 'wallpaper' in params and params.get('wallpaper') != 'DEFAULT' and not artpic in params.get('wallpaper'):
		liz.setArt({'fanart': params.get('wallpaper')})
	entries = []
	if FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url'), 'plot': plot, 'wallpaper': params.get('wallpaper'), 'cineType': params.get('cineType')}))])
	liz.addContextMenuItems(entries, replaceItems=False)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

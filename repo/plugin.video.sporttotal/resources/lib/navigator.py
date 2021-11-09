# -*- coding: utf-8 -*-

import sys
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import time
from datetime import datetime, timedelta
from collections import OrderedDict
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote, unquote  # Python 2.X
	from urllib2 import urlopen  # Python 2.X
else:
	from urllib.parse import urlencode, quote, unquote  # Python 3.X
	from urllib.request import urlopen  # Python 3.X

from .common import *


def mainMenu():
	debug_MS("(mainMenu) -------------------------------------------------- START = mainMenu --------------------------------------------------")
	COMBI_TYPES = []
	content = getUrl(BASE_URL+'root.json?lang='+langSHORTCUT)#.replace('window.config={', '{')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for each in DATA['menu']['content']:
		debug_MS("(mainMenu) ### ENTRY = {0} ###".format(str(each)))
		title = (cleaning(each.get('title', '')) or None)
		idd = (str(each.get('id', '')).strip() or None)
		type = (cleaning(each.get('type', '')) or None)
		if title and idd and type and idd not in COMBI_TYPES:
			COMBI_TYPES.append({'title': title, 'idd': idd+'.json?lang='+langSHORTCUT, 'type': type})
	if COMBI_TYPES:
		sublist = json.dumps(COMBI_TYPES)
		for item in sorted(COMBI_TYPES, key=lambda d:d['title'], reverse=False):
			if item['type'].lower() == 'sport' or 'amator ' in item['title'].lower():
				newCAT = item['title'] if not 'amator ' in item['title'].lower() else 'amator'
				debug_MS("(mainMenu) --- SPORT --- ### TITLE = {0} ### URL = {1} ### CATEGORY = {2} ###".format(str(item['title']), BASE_URL+item['idd'], str(newCAT)))
				addDir(item['title'], icon, {'mode': 'listCategories', 'url': BASE_URL+item['idd'], 'category': newCAT})
		addDir(translation(30606), icon, {'mode': 'listEvents', 'url': sublist})
	if enableADJUSTMENT:
		addDir(translation(30607), artpic+'settings.png', {'mode': 'aSettings'})
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30608), artpic+'settings.png', {'mode': 'iSettings'})
		else:
			addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listEvents(Xurl):
	debug_MS("(listEvents) ##### JSON-LIST = {0} #####".format(str(Xurl)))
	COMBI_REGION = []
	COMBI_EVENT = []
	DATA = json.loads(Xurl, object_pairs_hook=OrderedDict)
	for elem in DATA:
		if elem['type'].lower() == 'region':
			title_RE = translation(30620).format(cleaning(elem['title']))
			url_RE = BASE_URL+elem['idd']
			debug_MS("(listEvents) --- REGION --- ### TITLE = {0} ### URL = {1} ###".format(str(cleaning(elem['title'])), url_RE))
			COMBI_REGION.append([title_RE, url_RE])
		elif elem['type'].lower() == 'event':
			title_EV = cleaning(elem['title'])
			url_EV = BASE_URL+elem['idd']
			debug_MS("(listEvents)  --- EVENT ---  ### TITLE = {0} ### URL = {1} ###".format(str(title_EV), url_EV))
			COMBI_EVENT.append([title_EV, url_EV])
	if COMBI_REGION:
		for title_RE, url_RE in sorted(COMBI_REGION, key=lambda rn:rn[0].replace('Ö', 'Oe'), reverse=False):
			addDir(title_RE, icon, {'mode': 'listCategories', 'url': url_RE, 'category': 'Region'})
		addDir(translation(30621), icon, {'mode': 'blankFUNC', 'url': '00'}, folder=False)
	if COMBI_EVENT:
		for title_EV, url_EV in sorted(COMBI_EVENT, key=lambda et:et[0], reverse=False):
			addDir(title_EV, icon, {'mode': 'listCategories', 'url': url_EV, 'category': 'Event'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
                                                                                            # https://api.sporttotal.tv/v2/vod?sporttypeuuid=6294114c-5400-4978-bc6a-b3fe75d03fdf&channeluuid=00365d04-ad90-4ef7-b9b3-ef1e72890908
def listCategories(url, CAT, FILTER, THUMB): # https://api.sporttotal.tv/v2/live?sporttypeuuid=6294114c-5400-4978-bc6a-b3fe75d03fdf&channeluuid=00365d04-ad90-4ef7-b9b3-ef1e72890908
	debug_MS("(listCategories) -------------------------------------------------- START = listCategories --------------------------------------------------")
	debug_MS("(listCategories) ##### URL = {0} ##### CATEGORY = {1} ##### FILTER = {2} #####".format(url, str(CAT), FILTER))
	langADAPTION = ['nächste', 'kommende', 'upcoming']
	UN_Supported = ['adac', 'amator', 'event', 'motorsport', 'region']
	COMBI_CATS = []
	ISOLATED = set()
	FOUND = 0
	position = 0
	content = getUrl(url)#.replace('window.config={', '{')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for each in DATA['components']:
		if each.get('component', '').lower() not in ['description', 'videoplayer'] and each.get('title', ''): # in ['List', 'Table']:
			debug_MS("(listCategories) ### ENTRY = {0} ###".format(str(each)))
			title = cleaning(each['title'])
			if title in ISOLATED or ('children' in each and len(each['children']) == 0):
				continue
			ISOLATED.add(title)
			FOUND += 1
			name = title#.title()
			if 'live' in title.lower():
				position, name = 1, translation(30622).format(str(len(each['children'])))
			elif any(lg in title.lower() for lg in langADAPTION):
				position, name = 2, translation(30623)
			else: position = 3
			COMBI_CATS.append([position, name, title])
	if COMBI_CATS:
		for position, name, title in sorted(COMBI_CATS, key=lambda d:d[0], reverse=False):
			newFILTER = 'amator' if CAT == 'amator' else 'standard'
			debug_MS("(listCategories) no.01 ### TITLE = {0} ### URL = {1} ### FILTER = {2} ###".format(str(name), url, newFILTER))
			addDir(name, THUMB, {'mode': 'listVideos', 'url': url, 'category': title, 'filtermod': newFILTER, 'background': 'KEIN HINTERGRUND'})
		#if not any(x in CAT.lower() for x in UN_Supported) and FILTER != 'no_Additives':
			#debug_MS("(listCategories) no.02 ### ADD FOLDER (Ligen Gesamtübersicht) TO CATEGORY = {0} ###".format(CAT))
			#addDir(translation(30624), THUMB, {'mode': 'listLeagues', 'url': url, 'background': 'KEIN HINTERGRUND'})
	if FOUND == 0:
		return dialog.notification(translation(30522).format('Ergebnisse'), translation(30524), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listVideos(url, CAT, FILTER):
	debug_MS("(listVideos) -------------------------------------------------- START = listVideos --------------------------------------------------")
	debug_MS("(listVideos) ##### URL = {0} ##### CATEGORY = {1} ##### FILTER = {2} #####".format(url, str(CAT), FILTER))
	FOUND = 0
	CHOICE = CAT
	content = getUrl(url)#.replace('window.config={', '{')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for each in DATA['components']:
		if each.get('title', ''):
			RUBRIK = cleaning(each['title'])
			if RUBRIK == CHOICE and each.get('children', ''):
				for item in each['children']:
					debug_MS("(listVideos) ### ENTRY = {0} ###".format(str(item)))
					gender, plot, fotoBIG = ("" for _ in range(3))
					startCOMPLETE, startDATE, startTIME = (None for _ in range(3))
					FOUND += 1
					title = cleaning(item['title'])
					idd = str(item['id']).strip()+'.json?lang='+langSHORTCUT
					sexo = (cleaning(item.get('gender', '')) or "")
					if sexo == 'WOMEN': gender = translation(30625).format(sexo.replace('WOMEN', 'F'))
					elif sexo == 'MEN': gender = translation(30626).format(sexo.replace('MEN', 'M'))
					if str(item.get('date', '')).isdigit():
						LOCALstart = utc_to_local(datetime(1970, 1, 1) + timedelta(milliseconds=int(item.get('date', ''))))
						startCOMPLETE = LOCALstart.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
						startDATE = LOCALstart.strftime('%d{0}%m{0}%Y').format('.')
						startTIME = LOCALstart.strftime('%H{0}%M').format(':')
					plot = (cleaning(item.get('description', '')) or "")
					if plot == "" and item.get('competition', {}).get('title', ''):
						plot = cleaning(item['competition']['title'])+" :[CR]"+title
					photo = (quote(py2_enc(item.get('image', {}).get('cover', '')), safe='/:') or quote(py2_enc(item.get('image', {}).get('thumb', '')), safe='/:') or icon)
					if photo == icon:
						try: photo = quote(py2_enc(item['teams'][0]['image']['logo']), safe='/:') # photo = cleanPhoto(item['teams'][0]['image']['cover'])
						except: photo = quote(py2_enc(item.get('image', {}).get('logo', '')), safe='/:')
						fotoBIG = 'KEIN HINTERGRUND'
					name = title+gender
					if str(item.get('payPerViewPrice', '')).replace('.', '').replace('-', '').isdigit():
						if int(str(item.get('payPerViewPrice', '')).replace('.', '').replace('-', '')) > 1: continue
					type = (cleaning(item.get('type', '')) or "")
					if (FILTER == 'amator' or type.lower() in ['match', 'video'] or item.get('video') != None):
						debug_MS("(listVideos) no.01 ### TITLE = {0} ### TYPE = {1} ###".format(str(title), type.lower()))
						debug_MS("(listVideos) no.01 ### URL = {0} ###".format(BASE_URL+idd))
						name = startDATE+" - "+title+gender if startDATE and not '1970' in startDATE else title+gender
						if 'live' in RUBRIK.lower() and startTIME:
							name = translation(30627).format(startTIME, title+gender)
						elif not 'live' in RUBRIK.lower() and startCOMPLETE:
							if LOCALstart > datetime.now():
								name = startCOMPLETE+" - "+title+gender
						addLink(name, photo, {'mode': 'playVideo', 'url': BASE_URL+idd, 'category': name, 'background': fotoBIG}, plot)
					else:
						xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
						debug_MS("(listVideos) no.02 ### TITLE = {0} ### TYPE = Category-Folder ###".format(str(title)))
						debug_MS("(listVideos) no.02 ### URL = {0} ###".format(BASE_URL+idd))
						if not 'amator' in title.lower():
							addDir(name, photo, {'mode': 'listCategories', 'url': BASE_URL+idd, 'filtermod': 'no_Additives', 'picture': photo, 'background': fotoBIG}, plot)
	if FOUND == 0:
		return dialog.notification(translation(30522).format('Einträge'), translation(30525).format(CHOICE), icon, 8000)
	xbmcplugin.endOfDirectory(handle=ADDON_HANDLE, cacheToDisc=False)

def listLeagues(url):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS("(listLeagues) -------------------------------------------------- START = listLeagues --------------------------------------------------")
	debug_MS("(listLeagues) ##### URL = {0} #####".format(url))
	ISOLATED = set()
	FOUND = 0
	content = getUrl(url)#.replace('window.config={', '{')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for each in DATA['components']:
		if each.get('options', ''):
			for item in each['options']:
				debug_MS("(listLeagues) ### ENTRY = {0} ###".format(str(item)))
				title = cleaning(item['title'])
				idd = str(item['id']).strip()
				if idd != '*' and idd is not None:
					if idd in ISOLATED:
						continue
					ISOLATED.add(idd)
					FOUND += 1
					idd = idd+'.json?lang='+langSHORTCUT
					addDir(title, icon, {'mode': 'listCategories', 'url': BASE_URL+idd, 'filtermod': 'no_Additives'})
	if FOUND == 0:
		return dialog.notification(translation(30522).format('Ergebnisse'), translation(30524), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playVideo(url, NAME):
	debug_MS("(playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	debug_MS("(playVideo) ##### URL = {0} ##### NAME = {1} #####".format(url, str(NAME)))
	m3u8_LIST = []
	mp4_LIST = []
	stream = False
	FILE_URL = False
	TEST_URL = False
	content = getUrl(url)#.replace('window.config={', '{')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for each in DATA['components']:
		if each.get('component', '').lower() == 'videoplayer' and each.get('video', ''):
			videos = list(browse_All(each['video'], 'value')) # FILTER show only the Values behind constantly changing Key (default, Default, video...)
			for elem in videos:
				if 'm3u8' in elem.lower() and not 'pano' in elem.lower():
					m3u8_LIST.append(elem)
					FILE_URL = True
				if ('mp4' in elem.lower() or '.ts' in elem.lower()) and not 'pano' in elem.lower():
					mp4_LIST.append(elem)
					FILE_URL = True
			debug_MS("(playVideo) ### VIDEOS_m3u8 = {0} ###".format(str(m3u8_LIST)))
			debug_MS("(playVideo) ### VIDEOS_mp4 = {0} ###".format(str(mp4_LIST)))
	if m3u8_LIST:
		stream = m3u8_LIST[0]
	if mp4_LIST and not stream:
		stream = mp4_LIST[1] if len(mp4_LIST) > 1 else mp4_LIST[0]
	if not stream:
		failing("(playVideo) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Stream-Eintrag auf der Webseite von *sporttotal.tv* gefunden !!! ##########".format(url))
		return dialog.notification(translation(30521).format('URL-1'), translation(30526), icon, 8000)
	finalURL = quote(py2_enc(stream), safe='_/:-.%20')
	debug_MS("(playVideo) ### standardSTREAM = {0} ### correctSTREAM = {1} ###".format(stream, finalURL))
	try:
		code = urlopen(finalURL).getcode()
		if str(code) == "200":
			TEST_URL = True
	except: pass
	if FILE_URL and TEST_URL: # https://d3j8poz04ftomu.cloudfront.net/RECORD/0_hd_hls.m3u8?hlsid=HTTP_ID_1
		log("(playVideo) StreamURL : {0}".format(finalURL))
		listitem = xbmcgui.ListItem(path=finalURL)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive') and 'm3u8' in finalURL:
			listitem.setProperty(INPUT_APP, 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
			listitem.setMimeType('application/vnd.apple.mpegurl')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem)
	else:
		failing("(playVideo) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## Die Stream-Url auf der Webseite von *sporttotal.tv* ist OFFLINE !!! ##########".format(finalURL))
		return dialog.notification(translation(30521).format('URL-2'), translation(30527), icon, 8000)

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Studio': 'Sporttotal.tv'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image != icon and not artpic in image and params.get('background') != 'KEIN HINTERGRUND':
		liz.setArt({'fanart': image})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot=None, duration=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Duration': duration, 'Studio': 'Sporttotal.tv', 'Genre': 'Sport', 'Mediatype': 'video'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image != icon and not artpic in image and params.get('background') != 'KEIN HINTERGRUND':
		liz.setArt({'fanart': image})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	liz.addContextMenuItems([(translation(30654), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)')])
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)

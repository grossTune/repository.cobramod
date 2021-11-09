# -*- coding: utf-8 -*-

import sys
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import time
import _strptime
from datetime import datetime, timedelta
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode  # Python 2.X
else: 
	from urllib.parse import urlencode  # Python 3.X

from .common import *


if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def mainMenu():
	addDir(translation(30601), artpic+'favourites.png', {'mode': 'listShowsFavs'})
	addDir(translation(30602), icon, {'mode': 'listSeries', 'url': BASE_API+'/content/shows?include=images&sort=-newestEpisodePublishStart&filter[hasNewEpisodes]=true', 'extras': 'recently_added'})
	addDir(translation(30603), icon, {'mode': 'listSeries', 'url': BASE_API+'/content/shows?include=images&sort=publishEnd&filter[hasExpiringEpisodes]=true', 'extras': 'last_chance'})
	addDir(translation(30604), icon, {'mode': 'listThemes', 'url': BASE_API+'/content/genres?include=images&page[size]=50'})
	addDir(translation(30605), icon, {'mode': 'listSeries', 'url': BASE_API+'/content/shows?include=images&sort=views.lastWeek', 'extras': 'most_popular'})
	addDir(translation(30606), icon, {'mode': 'listAlphabet', 'extras': 'letter_A-Z'})
	addDir(translation(30607), icon, {'mode': 'listSeries', 'url': BASE_API+'/content/shows?include=images&sort=name', 'extras': 'overview_all'})
	if enableADJUSTMENT:
		addDir(translation(30608), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if ADDON_operate('inputstream.adaptive'):
			addDir(translation(30609), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listThemes(url):
	debug_MS("(navigator.listThemes) ------------------------------------------------ START = listThemes -----------------------------------------------")
	DATA = getUrl(url)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listThemes) XXXXX CONTENT : {0} XXXXX".format(str(DATA)))
	debug_MS("++++++++++++++++++++++++")
	for elem in DATA['data']:
		photoID = None
		if elem.get('relationships', None) and elem.get('relationships').get('images', None) and elem.get('relationships').get('images').get('data', None):
			photoID = [poid.get('id', []) for poid in elem.get('relationships', {}).get('images', {}).get('data', '')][0]
		genreID = str(elem['id'])
		name = cleaning(elem['attributes']['name'])
		vodpictures = DATA.get('included', [])
		try: image = [img.get('attributes', {}).get('src', []) for img in vodpictures if img.get('id') == photoID][0]
		except: image = icon
		newURL = '{0}/content/shows?include=images&sort=name&filter[genre.id]={1}'.format(BASE_API, genreID)
		addDir(name, image, {'mode': 'listSeries', 'url': newURL, 'extras': 'overview_genres'})
		debug_MS("(navigator.listThemes) ### NAME : {0} || GENRE-ID : {1} || IMAGE : {2} ###".format(str(name), genreID, image))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet():
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	for letter in (('0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')):
		newURL = '{0}/content/shows?include=images&sort=name&filter[name.startsWith]={1}'.format(BASE_API, letter.replace('0-9', '1'))
		addDir(letter, alppic+letter+'.jpg', {'mode': 'listSeries', 'url': newURL})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSeries(url, PAGE, POS, ADDITION):
	debug_MS("(navigator.listSeries) ------------------------------------------------ START = listSeries -----------------------------------------------")
	debug_MS("(navigator.listSeries) ### URL : {0} ### PAGE : {1} ### POS : {2} ### ADDITION : {3} ###".format(url, str(PAGE), str(POS), str(ADDITION)))
	UNIKAT = set()
	count = int(POS)
	newURL = url+'&page[number]={0}&page[size]=50'.format(str(PAGE))
	DATA = getUrl(newURL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listSeries) XXXXX CONTENT : {0} XXXXX".format(str(DATA)))
	debug_MS("++++++++++++++++++++++++")
	for elem in DATA['data']:
		debug_MS("(navigator.listSeries) ##### ELEMENT : {0} #####".format(str(elem)))
		genre, seriesID, plot = ("" for _ in range(3))
		photoID = None
		genreLIST = []
		if elem.get('relationships', None) and elem.get('relationships').get('genres', None) and elem.get('relationships').get('genres').get('data', None):
			genreLIST = [convert(genid.get('id', [])) for genid in elem.get('relationships', {}).get('genres', {}).get('data', '')]
			if genreLIST: genre = ' / '.join(sorted(genreLIST))
		if elem.get('relationships', None) and elem.get('relationships').get('images', None) and elem.get('relationships').get('images').get('data', None):
			photoID = [poid.get('id', []) for poid in elem.get('relationships', {}).get('images', {}).get('data', '')][0]
		seriesID = (str(elem.get('id', '')) or "")
		if seriesID != "" and seriesID in UNIKAT:
			continue
		UNIKAT.add(seriesID)
		if 'attributes' in elem:
			elem = elem['attributes']
		if elem.get('name', ''):
			name, seriesNAME = cleaning(elem['name']), cleaning(elem['name'])
		else: continue
		plot = (cleaning(elem.get('description', '')).replace('\n\n\n', '\n\n') or "")
		vodpictures = DATA.get('included', [])
		try: image = [img.get('attributes', {}).get('src', []) for img in vodpictures if img.get('id') == photoID][0]
		except: image = icon
		debug_MS("(navigator.listSeries) noFilter ### NAME : {0} || SERIE-IDD : {1} || IMAGE : {2} ###".format(str(name), seriesID, image))
		if seriesID !="" and len(seriesID) < 9 and plot != "":
			count += 1
			if 'views.lastWeek' in url:
				name = translation(30620).format(str(count), seriesNAME)
			elif 'filter[hasExpiringEpisodes]' in url:
				name = translation(30621).format(name)
			if not 'filter[hasExpiringEpisodes]' in url and elem.get('hasNewEpisodes', '') is True:
				name = translation(30622).format(name)
			debug_MS("(navigator.listSeries) Filtered --- NAME : {0} || SERIE-IDD : {1} || IMAGE : {2} ---".format(str(name), seriesID, image))
			addType = 1
			if xbmcvfs.exists(channelFavsFile):
				with open(channelFavsFile, 'r') as fp:
					watch = json.load(fp)
					for item in watch.get('items', []):
						if item.get('url') == seriesID: addType = 2
			addDir(name, image, {'mode': 'listEpisodes', 'url': seriesID, 'extras': ADDITION, 'origSERIE': seriesNAME}, plot, genre, addType)
	currentRESULT = count
	debug_MS("(navigator.listSeries) NUMBERING ### currentRESULT : {0} ###".format(str(currentRESULT)))
	try:
		totalPG = DATA['meta']['totalPages']
		debug_MS("(navigator.listSeries) PAGES ### currentPG : {0} from totalPG : {1} ###".format(str(PAGE), str(totalPG)))
		if int(PAGE) < int(totalPG):
			addDir(translation(30623), artpic+'nextpage.png', {'mode': 'listSeries', 'url': url, 'page': int(PAGE)+1, 'position': int(currentRESULT), 'extras': ADDITION})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listEpisodes(Xidd, origSERIE):
	debug_MS("(navigator.listEpisodes) ------------------------------------------------ START = listEpisodes -----------------------------------------------")
	debug_MS("(navigator.listEpisodes) ### URL : {0} ### origSERIE : {1} ###".format(str(Xidd), origSERIE))
	COMBI_EPISODE = []
	pos_SP = 0
	pageNUMBER = 1
	while pageNUMBER < 6:
		newURL = '{0}/content/videos?include=images&sort=-seasonNumber,-episodeNumber&filter[show.id]={1}&filter[videoType]=EPISODE,STANDALONE&page[number]={2}&page[size]=100'.format(BASE_API, Xidd, str(pageNUMBER))
		DATA = getUrl(newURL)
		debug_MS("++++++++++++++++++++++++")
		debug_MS("(navigator.listEpisodes) XXXXX CONTENT : {0} XXXXX".format(str(DATA)))
		debug_MS("++++++++++++++++++++++++")
		if len(DATA['data']) > 0:
			pageNUMBER += 1
		else:
			pageNUMBER += 5
		for vid in DATA['data']:
			genre, episID, plus_SUFFIX, videoTYPE, title2, number, Note_1, Note_2, Note_3 = ("" for _ in range(9))
			season, episode, duration = ('0' for _ in range(3))
			photoID, startTIMES, endTIMES, begins, year, mpaa = (None for _ in range(6))
			genreLIST = []
			if vid.get('relationships', None) and vid.get('relationships').get('genres', None) and vid.get('relationships').get('genres').get('data', None):
				genreLIST = [convert(genid.get('id', [])) for genid in vid.get('relationships', {}).get('genres', {}).get('data', '')]
				if genreLIST: genre = ' / '.join(sorted(genreLIST))
			if vid.get('relationships', None) and vid.get('relationships').get('images', None) and vid.get('relationships').get('images').get('data', None):
				photoID = [poid.get('id', []) for poid in vid.get('relationships', {}).get('images', {}).get('data', '')][0]
			episID = (str(vid.get('id', '')) or "")
			if 'attributes' in vid:
				vid = vid['attributes']
			debug_MS("(navigator.listEpisodes) ##### ELEMENT : {0} #####".format(str(vid)))
			if vid.get('name', ''):
				title = cleaning(vid['name'])
			else: continue
			if vid.get('isExpiring', '') is True or vid.get('isNew', '') is True:
				plus_SUFFIX = translation(30624) if vid.get('isNew', '') is True else translation(30625)
			if vid.get('seasonNumber', ''):
				season = str(vid['seasonNumber']).zfill(2)
			if vid.get('episodeNumber', ''):
				episode = str(vid['episodeNumber']).zfill(2)
			videoTYPE = (vid.get('videoType', '') or "")
			if videoTYPE.upper() == 'STANDALONE' and episode == '0':
				pos_SP += 1
			if season != '0' and episode != '0':
				title1 = translation(30626).format(season, episode)
				if videoTYPE.upper() == 'STANDALONE':
					title1 = translation(30627).format(season, episode)
				title2 = title+plus_SUFFIX
				number = 'S'+season+'E'+episode
			else:
				if videoTYPE.upper() == 'STANDALONE':
					episode = str(pos_SP).zfill(2)
					title1 = translation(30628).format(episode)
					title2 = title+'  (Special)'+plus_SUFFIX if not 'Special' in title else title+plus_SUFFIX
					number = 'S00E'+episode
				else:
					title1 = title+plus_SUFFIX
			if str(vid.get('publishStart'))[:4].isdigit() and str(vid.get('publishStart'))[:4] not in ['0', '1970']:
				LOCALstart = get_Local_DT(vid['publishStart'][:19])
				startTIMES = LOCALstart.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
				begins = LOCALstart.strftime('%d{0}%m{0}%Y').format('.')
			if str(vid.get('publishEnd'))[:4].isdigit() and str(vid.get('publishEnd'))[:4] not in ['0', '1970']:
				LOCALend = get_Local_DT(vid['publishEnd'][:19])
				endTIMES = LOCALend.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			if str(vid.get('airDate'))[:4].isdigit() and str(vid.get('airDate'))[:4] not in ['0', '1970']:
				year = str(vid['airDate'])[:4]
			if startTIMES and endTIMES: Note_1 = translation(30629).format(str(startTIMES), str(endTIMES))
			elif startTIMES and endTIMES is None: Note_1 = translation(30630).format(str(startTIMES))
			if str(py2_enc(vid.get('rating'))) not in ['', 'None', '0', 'nicht definiert']:
				mpaa = translation(30631).format(str(py2_enc(vid.get('rating'))))
			if mpaa is None and 'contentRatings' in vid and vid['contentRatings'] and len(vid['contentRatings']) > 0:
				if str(py2_enc(vid.get('contentRatings', {})[0].get('code', ''))) not in ['', 'None', '0', 'nicht definiert']:
					mpaa = translation(30631).format(str(py2_enc(vid.get('contentRatings', {})[0].get('code', ''))))
			if vid.get('description', ''):
				Note_2 = cleaning(vid['description']).replace('\n\n\n', '\n\n')
			plot = origSERIE+'[CR]'+Note_1+Note_2
			protect = (vid.get('drmEnabled', False) or False)
			if vid.get('videoDuration', ''):
				duration = get_Time(vid['videoDuration'])
			vodpictures = DATA.get('included', [])
			try: image = [img.get('attributes', {}).get('src', []) for img in vodpictures if img.get('id') == photoID][0]
			except: image = icon
			COMBI_EPISODE.append([number, title1, title2, episID, image, plot, duration, season, episode, genre, mpaa, year, begins, protect])
	if COMBI_EPISODE:
		if SORTING == '0':
			COMBI_EPISODE = sorted(COMBI_EPISODE, key=lambda d:d[0], reverse=True)
		for number, title1, title2, episID, image, plot, duration, season, episode, genre, mpaa, year, begins, protect in COMBI_EPISODE:
			if SORTING == '1':
				for method in getSorting():
					xbmcplugin.addSortMethod(ADDON_HANDLE, method)
			name = title1.strip() if title2 == "" else title1.strip()+"  "+title2.strip()
			cineType = 'episode' if episode != '0' else 'movie'
			debug_MS("(navigator.listEpisodes) ##### NAME : {0} || IDD : {1} || GENRE : {2} #####".format(str(name), episID, str(genre)))
			debug_MS("(navigator.listEpisodes) ##### IMAGE : {0} || SEASON : {1} || EPISODE : {2} #####".format(image, str(season), str(episode)))
			addLink(name, image, {'mode': 'playVideo', 'url': episID, 'cineType': cineType}, plot, duration, origSERIE, season, episode, genre, mpaa, year, begins)
	else:
		debug_MS("(navigator.listEpisodes) ##### Keine COMBI_EPISODE-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30525), translation(30526).format(origSERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playVideo(Xidd):
	debug_MS("(navigator.playVideo) ------------------------------------------------ START = playVideo -----------------------------------------------")
	DRM, STREAM, finalURL = (False for _ in range(3))
	# NEW Playback = https://eu1-prod.disco-api.com/playback/videoPlaybackInfo/142036?usePreAuth=true
	playURL = '{0}/playback/videoPlaybackInfo/{1}?usePreAuth=true'.format(BASE_API, Xidd)
	DATA = getUrl(playURL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.playVideo) XXXXX CONTENT : {0} XXXXX".format(str(DATA)))
	debug_MS("++++++++++++++++++++++++")
	if 'data' in DATA and 'attributes' in DATA['data'] and len(DATA['data']['attributes']) > 0:
		SHORT = DATA['data']['attributes']
		if SHORT.get('protection', '') and SHORT.get('protection', {}).get('drmEnabled', '') is True:
			DRM = True
			STREAM = 'mpd'
			MIME = 'application/dash+xml'
			finalURL = SHORT['streaming']['dash']['url']
			lic_URL = SHORT['protection']['schemes']['widevine']['licenseUrl']
			drm_TOKEN = SHORT['protection']['drmToken']
			lic_KEY = u'{0}|User-Agent={1}&PreAuthorization={2}&Content-Type=application/octet-stream|{3}|'.format(lic_URL, get_userAgent(), drm_TOKEN, 'R{SSM}')
			debug_MS("(navigator.playVideo) XXX TAKE - Inputstream (mpd) - FILE XXX")
		if not finalURL and SHORT.get('protection', '') and SHORT.get('protection', {}).get('clearkeyEnabled', '') is True:
			STREAM = 'hls'
			MIME = 'application/vnd.apple.mpegurl'
			finalURL = SHORT['streaming']['hls']['url']
			lic_URL = SHORT['protection']['schemes']['clearkey']['licenseUrl']
			lic_KEY = u'{0}'.format(getUrl(lic_URL)['keys'][0]['kid'])
			debug_MS("(navigator.playVideo) XXX TAKE - Inputstream (hls) - FILE XXX")
	if finalURL and STREAM and ADDON_operate('inputstream.adaptive'):
		log("(navigator.playVideo) {0}_stream : {1}|User-Agent={2}".format(STREAM.upper(), finalURL, get_userAgent()))
		listitem = xbmcgui.ListItem(path=finalURL)
		listitem.setMimeType(MIME)
		listitem.setProperty(INPUT_APP, 'inputstream.adaptive')
		listitem.setProperty('inputstream.adaptive.manifest_type', STREAM)
		listitem.setProperty('inputstream.adaptive.license_key', lic_KEY)
		debug_MS("(navigator.playVideo) LICENSE : {0}".format(str(lic_KEY)))
		if DRM is True:
			listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem)
	else:
		failing("(navigator.playVideo) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN passenden Stream-Eintrag gefunden !!! ##########".format(str(Xidd)))
		return dialog.notification(translation(30521).format('ID - ', Xidd), translation(30527), icon, 8000)

def listShowsFavs():
	debug_MS("(navigator.listShowsFavs) ------------------------------------------------ START = listShowsFavs -----------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as fp:
			watch = json.load(fp)
			for item in watch.get('items', []):
				name = cleaning(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else item.get('pict')
				desc = None if item.get('plot', 'None') == 'None' else cleaning(item.get('plot'))
				debug_MS("(navigator.listShowsFavs) ### NAME : {0} || URL : {1} || IMAGE : {2} ###".format(name, item.get('url'), logo))
				addDir(name, logo, {'mode': 'listEpisodes', 'url': item.get('url'), 'origSERIE': name}, desc, FAVclear=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'plot': plot})
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30528), translation(30529).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('url') != url]
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30528), translation(30530).format(name), icon, 8000)

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, genre=None, addType=0, FAVclear=False, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Genre': genre, 'Studio': 'DMAX'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	entries = []
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'ADD', 'name': params.get('origSERIE'), 'pict': 'None' if image == icon else image,
			'url': params.get('url'), 'plot': 'None' if plot is None else plot.replace('\n', '[CR]')}))])
	if addType in [1, 2] and enableLIBRARY:
		entries.append([translation(30653), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'preparefiles', 'url': params.get('url'), 'name': params.get('origSERIE'), 'cycle': libraryPERIOD}))])
	if FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url'), 'plot': plot}))])
	liz.addContextMenuItems(entries, replaceItems=False)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot=None, duration=None, seriesname=None, season=None, episode=None, genre=None, mpaa=None, year=None, begins=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	info = {}
	info['Season'] = season
	info['Episode'] = episode
	info['Tvshowtitle'] = seriesname
	info['Title'] = name
	info['Tagline'] = None
	info['Plot'] = plot
	info['Duration'] = duration
	if begins is not None:
		info['Date'] = begins
	info['Year'] = year
	info['Genre'] = genre
	info['Studio'] = 'DMAX'
	info['Mpaa'] = mpaa
	info['Mediatype'] = params.get('cineType')
	liz.setInfo(type='Video', infoLabels=info)
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	liz.addContextMenuItems([(translation(30654), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)')])
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)

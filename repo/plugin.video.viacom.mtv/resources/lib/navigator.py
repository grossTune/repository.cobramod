# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import shutil
import random
import time
from collections import OrderedDict
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote_plus  # Python 2.X
else:
	from urllib.parse import urlencode, quote_plus  # Python 3.X

from .common import *


if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def mainMenu():
	config = traversing.get_config()
	addDir(translation(30601), icon, {'mode': 'listEpisodes', 'url': config['collect_Date'].format('episode'), 'extras': 'newEP', 'transmit': translation(30601).split('[/COLOR] ')[1]})
	addDir(translation(30602), icon, {'mode': 'listEpisodes', 'url': config['collect_Idd'].format(config['RELATED'], 'musicvideo'), 'extras': 'newMU', 'transmit': translation(30602).split('[/COLOR] ')[1]})
	addDir(translation(30603), icon, {'mode': 'listBroadcasts', 'url': config['collect_Title'].format('series')})
	addDir(translation(30604), icon, {'mode': 'listMusics'})
	addDir(translation(30605), icon, {'mode': 'listCharts'})
	addDir(translation(30606), icon, {'mode': 'listPlaylists', 'url': config['collect_Idd'].format(config['EXCLUDED'], 'videoplaylist')})
	addDir(translation(30607), artpic+'livestream.png', {'mode': 'playLIVE', 'url': config['live_M3U8']}, folder=False)
	addDir(translation(30608).format(str(cachePERIOD)), artpic+'remove.png', {'mode': 'clearCache'})
	if enableADJUSTMENT:
		addDir(translation(30609), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30610), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBroadcasts(url):
	debug_MS("(navigator.listBroadcasts) ------------------------------------------------ START = listBroadcasts -----------------------------------------------")
	FOUND = 0
	pageNUMBER = 1
	while pageNUMBER < 4:
		newURL = '{0}&pageNumber={1}&pageSize=30'.format(url, str(pageNUMBER))
		content = makeREQUEST(newURL)
		debug_MS("++++++++++++++++++++++++")
		debug_MS("(navigator.listBroadcasts) XXXXX CONTENT : {0} XXXXX".format(str(content)))
		debug_MS("++++++++++++++++++++++++")
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		if len(DATA['data']['items']) > 0:
			pageNUMBER += 1
		else:
			pageNUMBER += 3
		for item in DATA['data']['items']:
			showID, plus_SUFFIX, genre = ("" for _ in range(3))
			SEAS = None
			genreLIST = []
			FOUND += 1
			showID = item.get('mgid', '')
			shortId = (item.get('shortId', '') or "")
			title = (item.get('title', '') or item.get('shortTitle', ''))
			title = cleaning(title)
			if item.get('ribbon', '') and (item.get('ribbon', {}).get('newSeries', '') is True or item.get('ribbon', {}).get('newSeason', '') is True or item.get('ribbon', {}).get('newEpisode', '') is True):
				plus_SUFFIX = translation(30620)
			name = title+plus_SUFFIX
			plot = get_Description(item)
			entityType = (item.get('entityType', '') or "")
			photo = icon
			if item.get('images', ''):
				max_res = max(item['images'], key=lambda x:x.get('width'))
				photo = max_res.get('url')
			if item.get('genres', ''):
				genreLIST = [cleaning(gen) for gen in item.get('genres', '')]
				if genreLIST: genre = ' / '.join(sorted(genreLIST))
			if item.get('links', '') and item.get('links', {}).get('season', ''):
				SEAS = item['links']['season']+'&orderBy=seasonNumber&order=ascending'
			debug_MS("(navigator.listBroadcasts) ##### NAME = {0} || URL = {1} #####".format(str(name), str(SEAS)))
			debug_MS("(navigator.listBroadcasts) ##### TYPE = {0} || THUMB = {1} #####".format(entityType, photo))
			if SEAS:
				addDir(name, photo, {'mode': 'listSeasons', 'url': SEAS, 'pict': photo, 'transmit': title}, plot, genre)
	if FOUND == 0:
		debug_MS("(navigator.listBroadcasts) ##### Keine BROADCASTS-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30522).format('Einträge'), translation(30524).format('SHOWS'), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSeasons(url, THUMB, SERIE):
	debug_MS("(navigator.listSeasons) ------------------------------------------------ START = listSeasons -----------------------------------------------")
	debug_MS("(navigator.listSeasons) ### URL : {0} ### THUMB : {1} ### SERIE : {2} ###".format(url, THUMB, SERIE))
	COMBI_SEASON = []
	FOUND = 0
	newURL = url+'&pageNumber=1&pageSize=40'
	content = makeREQUEST(newURL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listSeasons) XXXXX CONTENT : {0} XXXXX".format(str(content)))
	debug_MS("++++++++++++++++++++++++")
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for elem in DATA['data']['items']:
		EPIS = None
		FOUND += 1
		seasID = (elem.get('mgid', '') or "")
		shortId = (elem.get('shortId', '') or "")
		plot = get_Description(elem)
		entityType = (elem.get('entityType', '') or "")
		name = translation(30621).format(str(elem.get('seasonNumber'))) if elem.get('seasonNumber', '') else translation(30622)
		if elem.get('links', '') and elem.get('links', {}).get('episode', ''):
			EPIS = elem['links']['episode']+'&orderBy=episodeNumber&order=ascending'
		debug_MS("(navigator.listSeasons) ##### NAME = {0} || URL = {1} #####".format(str(name), str(EPIS)))
		debug_MS("(navigator.listSeasons) ##### TYPE = {0} || THUMB = {1} #####".format(entityType, THUMB))
		if EPIS is None:
			continue
		COMBI_SEASON.append([name, THUMB, SERIE, EPIS, plot])
	if COMBI_SEASON and FOUND == 1:
		debug_MS("(navigator.listSeasons) ----- Only one Season FOUND - goto = listEpisodes -----")
		listEpisodes(EPIS, extras, SERIE+' - '+name, page, type)
	elif COMBI_SEASON and FOUND > 1:
		for name, THUMB, SERIE, EPIS, plot in COMBI_SEASON:
			addDir(name, THUMB, {'mode': 'listEpisodes', 'url': EPIS, 'transmit': SERIE+' - '+name}, plot)
	else:
		debug_MS("(navigator.listSeasons) ##### Keine COMBI_SEASON-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30525), translation(30526).format(SERIE), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listMusics():
	debug_MS("(navigator.listMusics) ------------------------------------------------ START = listMusics -----------------------------------------------")
	config = traversing.get_config()
	addDir(translation(30701), icon, {'mode': 'listEpisodes', 'url': config['collect_Idd'].format(config['RELATED'], 'musicvideo'), 'extras': 'MUSIC', 'transmit': translation(30701)})
	for n in config['music']:
		addDir(n['title'], icon, {'mode': 'listEpisodes', 'url': config['collect_Idd'].format(n['id'], 'musicvideo'), 'extras': 'MUSIC', 'transmit': n['title']})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listPlaylists(url, PAGE):
	debug_MS("(navigator.listPlaylists) ------------------------------------------------ START = listPlaylists -----------------------------------------------")
	debug_MS("(navigator.listPlaylists) ### URL : {0} ### PAGE : {1} ###".format(url, PAGE))
	COMBI_PLAYLIST = []
	FOUND = 0
	newURL = '{0}&pageNumber={1}&pageSize=30'.format(url, str(PAGE))
	content = makeREQUEST(newURL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listPlaylists) XXXXX CONTENT : {0} XXXXX".format(str(content)))
	debug_MS("++++++++++++++++++++++++")
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for elem in DATA['data']['items']:
		playID, Note_1, Note_2 = ("" for _ in range(3))
		startTIMES, LINK = (None for _ in range(2))
		FOUND += 1
		playID = elem.get('mgid', '')
		shortId = (elem.get('shortId', '') or "")
		name = elem.get('title', '')
		name = cleaning(name)
		entityType = (elem.get('entityType', '') or "")
		seriesNAME = cleaning(elem['parentEntity']['title'])+'[CR]' if elem.get('parentEntity', {}).get('title', '') else ""
		if str(elem.get('publishDate', {}).get('dateString', ''))[:4].isdigit() and str(elem.get('publishDate', {}).get('dateString', ''))[:4] not in ['0', '1970']:
			LOCALstart = get_Local_DT(elem['publishDate']['dateString'][:19])
			startTIMES = LOCALstart.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			begins = LOCALstart.strftime('%d{0}%m{0}%Y').format('.')
		if startTIMES: Note_1 = translation(30623).format(str(startTIMES))
		if elem.get('count', ''):
			Note_2 = translation(30624).format(str(elem['count']))
		photo = icon
		if elem.get('images', ''):
			max_res = max(elem['images'], key=lambda x:x.get('width'))
			photo = max_res.get('url')
		if elem.get('links', '') and elem.get('links', {}).get('video', ''):
			LINK = elem['links']['video']
		plot = seriesNAME+Note_1+Note_2
		debug_MS("(navigator.listPlaylists) ##### NAME = {0} || URL = {1} #####".format(str(name), str(LINK)))
		debug_MS("(navigator.listPlaylists) ##### TYPE = {0} || THUMB = {1} #####".format(entityType, photo))
		if LINK is None:
			continue
		COMBI_PLAYLIST.append([name, photo, LINK, plot])
	if COMBI_PLAYLIST and FOUND > 0:
		for name, photo, LINK, plot in COMBI_PLAYLIST:
			addDir(name, photo, {'mode': 'listEpisodes', 'url': LINK, 'extras': 'SNAKE', 'transmit': name}, plot)
		if DATA.get('metadata', '') and DATA.get('metadata', {}).get('pagination', '') and DATA.get('metadata', []).get('pagination', {}).get('hasMore', '') is True:
			debug_MS("(navigator.listPlaylists) PAGES ### Now show NextPage ... ###")
			addDir(translation(30625), artpic+'nextpage.png', {'mode': 'listPlaylists', 'url': url, 'page': int(PAGE)+1})
	else:
		debug_MS("(navigator.listPlaylists) ##### Keine COMBI_PLAYLIST-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30522).format('Einträge'), translation(30524).format('PLAYLISTS'), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listEpisodes(url, EXTRA, TRANS, PAGE, TYPE):
	debug_MS("(navigator.listEpisodes) ------------------------------------------------ START = listEpisodes -----------------------------------------------")
	debug_MS("(navigator.listEpisodes) ### URL : {0} ### EXTRA : {1} ### TRANS : {2} ### PAGE : {3} ### TYPE : {4} ###".format(url, EXTRA, TRANS, PAGE, TYPE))
	SEND = {}
	COMBI_EPISODE, SEND['videos'] = ([] for _ in range(2))
	PLT = cleanPlaylist() if TYPE == 'play' else None
	newURL = '{0}&pageNumber={1}&pageSize=30'.format(url, str(PAGE))
	content = makeREQUEST(newURL)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listEpisodes) XXXXX CONTENT : {0} XXXXX".format(str(content)))
	debug_MS("++++++++++++++++++++++++")
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for item in DATA['data']['items']:
		genre, episID, plus_SUFFIX, Note_1, Note_2 = ("" for _ in range(5))
		season, episode, duration = ('0' for _ in range(3))
		artist, startTIMES, begins, year, mpaa = (None for _ in range(5))
		genreLIST = []
		episID = item.get('mgid', '')
		shortId = (item.get('shortId', '') or '00')
		title = item.get('title', '')
		title = cleaning(title)
		artist = (item.get('shortTitle', '') or (item.get('personContexts', '') and item.get('personContexts', {})[0].get('title', '')))
		artist = cleaning(artist)
		origSERIE = cleaning(item['parentEntity']['title']) if item.get('parentEntity', {}).get('title', '') else ""
		matchSE = re.search('(season|Season|Se)\ (\d+)', item.get('subTitle', '')) # "subTitle": "Season 3, Ep 4"
		if matchSE: season = matchSE.group(2).zfill(2)
		matchEP = re.search('(episode|Episode|Ep|folge|Folge)\ (\d+)', item.get('subTitle', '')) # "subTitle": "Season 3, Ep 4"
		if matchEP: episode = matchEP.group(2).zfill(2)
		if item.get('ribbon', '') and (item.get('ribbon', {}).get('newEpisode', '') is True or item.get('ribbon', {}).get('newEvent', '') is True):
			plus_SUFFIX = translation(30620)
		if EXTRA == 'newEP':
			title = title+' - '+origSERIE if origSERIE !="" else title
		if EXTRA in ['newMU', 'MUSIC', 'SNAKE']:
			name = title+' - '+artist+plus_SUFFIX if artist else title+plus_SUFFIX
			origSERIE = artist if artist else ""
		else:
			name = translation(30626).format(season, episode, title)+plus_SUFFIX if season != '0' and episode != '0' else title+plus_SUFFIX
		entityType = (item.get('entityType', '') or "")
		if str(item.get('publishDate', {}).get('dateString', ''))[:4].isdigit() and str(item.get('publishDate', {}).get('dateString', ''))[:4] not in ['0', '1970']:
			LOCALstart = get_Local_DT(item['publishDate']['dateString'][:19])
			startTIMES = LOCALstart.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			begins = LOCALstart.strftime('%d{0}%m{0}%Y').format('.')
		if startTIMES: Note_1 = translation(30623).format(str(startTIMES))
		Note_2 = get_Description(item)
		photo = icon
		if item.get('images', ''):
			max_res = max(item['images'], key=lambda x:x.get('width'))
			photo = max_res.get('url')
		if item.get('duration', '') and item.get('duration', {}).get('milliseconds', ''):
			duration = int(item['duration']['milliseconds']/1000)
		else: continue
		if 'contentRating' in item and item['contentRating'] and len(item['contentRating']) > 0:
			if str(item.get('contentRating', {})[0].get('code', '')).isdigit():
				mpaa = translation(30627).format(str(item.get('contentRating', {})[0].get('code', ''))) if str(item.get('contentRating', {})[0].get('code', '')) != '0' else translation(30628)
		if item.get('genres', ''):
			genreLIST = [cleaning(gen) for gen in item.get('genres', '')]
			if genreLIST: genre = ' / '.join(sorted(genreLIST))
		if str(item.get('productionYear'))[:4].isdigit() and str(item.get('productionYear'))[:4] not in ['0', '1970']:
			year = str(item['productionYear'])[:4]
		serieOK = origSERIE+'[CR]' if origSERIE !="" else ""
		plot = serieOK+Note_1+Note_2
		debug_MS("(navigator.listEpisodes) ##### NAME : {0} || IDD : {1} || GENRE : {2} #####".format(str(name), episID, str(genre)))
		debug_MS("(navigator.listEpisodes) ##### THUMB : {0} || SEASON : {1} || EPISODE : {2} #####".format(photo, str(season), str(episode)))
		COMBI_EPISODE.append([name, origSERIE, season, episode, duration, shortId, episID, photo, plot, genre, mpaa, year, begins])
	if TYPE == 'browse':
		if COMBI_EPISODE:
			for name, origSERIE, season, episode, duration, shortId, episID, photo, plot, genre, mpaa, year, begins in COMBI_EPISODE:
				for method in getSorting():
					xbmcplugin.addSortMethod(ADDON_HANDLE, method)
				cineType = 'episode' if episode != '0' else 'movie'
				listitem = xbmcgui.ListItem(name, path=HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=playCODE')
				info = {}
				if season != '0':
					info['Season'] = season
				if episode != '0':
					info['Episode'] = episode
				info['Artist'] = [artist]
				info['Tvshowtitle'] = origSERIE
				info['Title'] = name
				info['Tagline'] = None
				info['Plot'] = plot
				info['Duration'] = duration
				if begins is not None:
					info['Date'] = begins
				info['Year'] = year
				info['Genre'] = [genre]
				info['Studio'] = 'MTV'
				info['Mpaa'] = mpaa
				info['Mediatype'] = cineType
				listitem.setInfo(type='Video', infoLabels=info)
				listitem.setArt({'icon': icon, 'thumb': photo, 'poster': photo, 'fanart': defaultFanart})
				if photo and useThumbAsFanart and photo != icon and not artpic in photo:
					listitem.setArt({'fanart': photo})
				listitem.addStreamInfo('Video', {'Duration': duration})
				listitem.setProperty('IsPlayable', 'true')
				listitem.setContentLookup(False)
				listitem.addContextMenuItems([(translation(30654), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)')])
				xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=playCODE', listitem=listitem)
				SEND['videos'].append({'url': shortId, 'tvshow': origSERIE, 'filter': shortId, 'name': name, 'pict': photo, 'cycle': duration, 'extras': 'browse', 'transmit': episID, 'shortTITLE': name})
			with open(WORKFILE, 'w') as ground:
				json.dump(SEND, ground, indent=4, sort_keys=True)
			if EXTRA not in ['newEP', 'newMU'] and DATA.get('metadata', '') and DATA.get('metadata', {}).get('pagination', '') and DATA.get('metadata', []).get('pagination', {}).get('hasMore', '') is True:
				debug_MS("(navigator.listEpisodes) PAGES ### Now show NextPage ... ###")
				addDir(translation(30625), artpic+'nextpage.png', {'mode': 'listEpisodes', 'url': url, 'extras': EXTRA, 'transmit': TRANS, 'page': int(PAGE)+1})
		else:
			debug_MS("(navigator.listEpisodes) ##### Keine COMBI_EPISODE-List - Kein Eintrag gefunden #####")
			return dialog.notification(translation(30522).format('Einträge'), translation(30524).format(TRANS), icon, 8000)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
	elif TYPE == 'play' and COMBI_EPISODE:
		random.shuffle(COMBI_EPISODE)
		for name, origSERIE, season, episode, duration, shortId, episID, photo, plot, genre, mpaa, year, begins in COMBI_EPISODE:
			endUrl = HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=playCODE'
			listitem = xbmcgui.ListItem(name, path=HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=playCODE')
			listitem.setArt({'icon': icon, 'thumb': photo, 'poster': photo})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
			SEND['videos'].append({'url': shortId, 'tvshow': origSERIE, 'filter': shortId, 'name': name, 'pict': photo, 'cycle': duration, 'extras': 'NOTICE', 'transmit': episID, 'shortTITLE': name})
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
		xbmc.Player().play(PLT)

def listCharts():
	debug_MS("(navigator.listCharts) ------------------------------------------------ START = listCharts -----------------------------------------------")
	config = traversing.get_config()
	for n in config['picks']:
		addDir(n['title'], n['img'].format(chapic), {'mode': 'chartVideos', 'url': config['chart_API'].format(n['id']), 'extras': 'CHART', 'transmit': n['title']}, background=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def chartVideos(url, TRANS, TYPE):
	debug_MS("(navigator.chartVideos) ------------------------------------------------ START = chartVideos -----------------------------------------------")
	debug_MS("(navigator.chartVideos) ### URL : {0} ### TRANS : {1} ### TYPE : {2} ###".format(url, TRANS, TYPE))
	SEND = {}
	COMBI_VID, COMBI_ALL, SEND['videos'] = ([] for _ in range(3))
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = makeREQUEST(url, REF=BASE_URL)
	#<div class="cmn-act">11</div><div class="cmn-change"><div id="cmn-arrow_down"></div></div><div class="cmn-old">9</div><div class="cmn-title"> Sweater Weather</div><div class="cmn-artist"> The Neighbourhood</div><div class="cmn-image"><img class="cmn-image" src="https://mtv.mtvnimages.com/uri/mgid:arc:content:mtv.de:afe26f40-b5d0-46ef-9058-1a6519de2484" /></div>
	#<div class="cmn-act">15</div><div class="cmn-change"><div id="cmn-arrow_up"></div></div><div class="cmn-old">17</div><div class="cmn-title"> My Heart Goes (La Di Da)</div><div class="cmn-artist"> Becky Hill feat. Topic</div><div class="cmn-image"> <a href="https://www.mtv.de/musikvideos/1c8w3b/my-heart-goes-la-di-da" target="_blank"><img class="cmn-image" src="https://mtv.mtvnimages.com/uri/mgid:arc:content:mtv.de:22d27161-3022-11ec-9b1b-0e40cf2fc285" /></a> </div>
	#<div class="cmn-act">12</div><div class="cmn-change-new"></div><div class="cmn-title"> Undeniable</div><div class="cmn-artist"> Kygo feat. X Ambassadors</div><div class="cmn-image"> <a href="https://www.mtv.de/musikvideos/9z01wv/undeniable" target="_blank"><img class="cmn-image" src="https://mtv.mtvnimages.com/uri/mgid:arc:content:mtv.de:05f35ccf-2ce3-11ec-9b1b-0e40cf2fc285" /></a> </div>
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.chartVideos) XXXXX CONTENT : {0} XXXXX".format(str(content)))
	debug_MS("++++++++++++++++++++++++")
	spl = content.split('class="charts-marslnet"')
	for i in range(1, len(spl), 1):
		entry = spl[i]
		debug_MS("(navigator.chartVideos) ##### ENTRY = {0} #####".format(entry))
		song = re.compile(r'="cmn-title">(.*?)</div>', re.S).findall(entry)[0]
		song = cleaning(song)
		artist = re.compile(r'="cmn-artist">(.*?)</div>', re.S).findall(entry)[0]
		artist = cleaning(artist)
		Chartnow = re.compile(r'class="cmn-act">(.*?)</div>', re.S).findall(entry)[0]
		Chartold = re.compile(r'class="cmn-old">(.*?)</div>', re.S).findall(entry)
		NewRee = re.compile(r'class="cmn-change-(.*?)">', re.S).findall(entry)
		EvUpDo = re.compile(r'<div id="(.*?)">', re.S).findall(entry)
		oldpos = ""
		if NewRee:
			oldpos = '[COLOR deepskyblue]  ( NEU )[/COLOR]' if NewRee[0] == 'new' else '[COLOR deepskyblue]  ( REE )[/COLOR]'
		elif Chartold and EvUpDo:
			if '_even' in EvUpDo[0]: oldpos = "  ( - )"
			elif '_up' in EvUpDo[0]: oldpos = translation(30629).format(str(int(Chartold[0]) -  int(Chartnow)))
			elif '_down' in EvUpDo[0]: oldpos = translation(30630).format(str(int(Chartnow) - int(Chartold[0])))
		img = re.compile(r'class="cmn-image" src="(https?://mtv[^"]+)"', re.S).findall(entry)
		photo = img[0] if img else icon
		video = re.compile(r'<a href="(https://www.mtv.de.*?)" target=', re.S).findall(entry)
		shortId = video[0].split('musikvideos/')[1].split('/')[0] if video else '00'
		debug_MS("(navigator.chartVideos) ##### TITLE = {0} || shortId = {1} || FOTO = {2} #####".format(str(Chartnow)+'. '+song+' - '+artist, str(shortId), photo))
		if shortId != '00':
			COMBI_VID.append([song, artist, photo, shortId, Chartnow, oldpos])
		COMBI_ALL.append([song, artist, photo, shortId, Chartnow, oldpos])
	if TYPE == 'browse':
		if COMBI_ALL:
			for song, artist, photo, shortId, Chartnow, oldpos in COMBI_ALL:
				if shortId != '00':
					name = translation(30631).format(str(Chartnow), song, artist+oldpos)
					listitem = xbmcgui.ListItem(name, path=HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=playCODE')
				elif shortId == '00' and showALL:
					name = translation(30632).format(str(Chartnow), song, artist+oldpos)
					listitem = xbmcgui.ListItem(name, path=HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=blankFUNC')
				info = {}
				info['Artist'] = [artist]
				info['Title'] = name
				info['Studio'] = 'MTV'
				info['Mediatype'] = 'movie'
				listitem.setInfo(type='Video', infoLabels=info)
				listitem.setArt({'icon': icon, 'thumb': photo, 'poster': photo, 'fanart': defaultFanart})
				if photo and useThumbAsFanart and photo != icon and not artpic in photo:
					listitem.setArt({'fanart': photo})
				listitem.setProperty('IsPlayable', 'true')
				listitem.setContentLookup(False)
				if shortId != '00':
					listitem.addContextMenuItems([(translation(30654), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)')])
					xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=playCODE', listitem=listitem)
				elif shortId == '00' and showALL:
					xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=blankFUNC', listitem=listitem)
				SEND['videos'].append({'url': shortId, 'tvshow': 'NOT FOUND', 'filter': shortId, 'name': name, 'pict': photo, 'cycle': '0', 'extras': 'browse', 'transmit': 'tracking', 'shortTITLE': song+' - '+artist})
			with open(WORKFILE, 'w') as ground:
				json.dump(SEND, ground, indent=4, sort_keys=True)
		else:
			debug_MS("(navigator.chartVideos) ##### Keine COMBI_ALL-List - Kein Eintrag gefunden #####")
			return dialog.notification(translation(30522).format('Einträge'), translation(30524).format(TRANS), icon, 8000)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
	elif TYPE == 'play' and COMBI_VID:
		random.shuffle(COMBI_VID)
		for song, artist, photo, shortId, Chartnow, oldpos in COMBI_VID:
			name = translation(30631).format(str(Chartnow), song, artist+oldpos)
			endUrl = HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=playCODE'
			listitem = xbmcgui.ListItem(name, path=HOST_AND_PATH+'?IDENTiTY='+shortId+'&mode=playCODE')
			listitem.setArt({'icon': icon, 'thumb': photo, 'poster': photo})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
			SEND['videos'].append({'url': shortId, 'tvshow': 'NOT FOUND', 'filter': shortId, 'name': name, 'pict': photo, 'cycle': '0', 'extras': 'NOTICE', 'transmit': 'tracking', 'shortTITLE': song+' - '+artist})
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
		xbmc.Player().play(PLT)

def getVideo(url, TRANS):
	config = traversing.get_config()
	if xbmcvfs.exists(tempSF) and os.path.isdir(tempSF):
		shutil.rmtree(tempSF, ignore_errors=True)
		xbmc.sleep(500)
	xbmcvfs.mkdirs(tempSF)
	subSOURCE, subFOUND = (False for _ in range(2))
	secondURL = ""
	if TRANS == 'tracking':
		check_1 = getUrl(config['shortID'].format(url))
		CODING = json.loads(check_1, object_pairs_hook=OrderedDict)
		if CODING.get('data', '') and CODING.get('data', {}).get('item', ''):
			TRANS = CODING['data']['item']['mgid']
			entityType = (CODING['data']['item'].get('entityType', '') or "")
	# OFFIZIELL           = https://media.mtvnservices.com/pmt/e1/access/index.html?uri=mgid:arc:episode:mtv.intl:aaed37d0-98f6-11eb-8774-70df2f866ace&configtype=edge&ref=https://www.mtv.de/folgen/5k5mx0/catfish-verliebte-im-netz-nyhjee-cianna-staffel-8-ep-41
	# FUNKTIONIERT = https://media.mtvnservices.com/pmt/e1/access/index.html?uri=mgid:arc:episode:mtv.intl:aaed37d0-98f6-11eb-8774-70df2f866ace&configtype=edge&ref=https://www.mtv.de/
	content_1 = getUrl(config['streamREQ'].format(TRANS, BASE_URL), REF=BASE_URL)
	debug_MS("+++++++++++++++++++++++++")
	debug_MS("(navigator.getVideo) XXXXX CONTENT-01 : {0} XXXXX".format(str(content_1.strip())))
	debug_MS("+++++++++++++++++++++++++")
	DATA_1 = json.loads(content_1, object_pairs_hook=OrderedDict)
	try: guid = DATA_1['feed']['items'][0]['guid']
	except: guid = DATA_1['uri']
	subNAME = py2_enc(DATA_1['feed']['title']).replace(' ', '-') if DATA_1.get('feed', '') and DATA_1.get('feed', {}).get('title', '') else 'TemporaryVideoSub'
	secondURL = DATA_1['mediaGen'].replace('&device={device}', '').replace('{uri}', guid)
	# ORIGINAL = https://media-utils.mtvnservices.com/services/MediaGenerator/{uri}?arcStage=live&format=json&acceptMethods=hls&https=true&device={device}&isEpisode=true&ratingIds=b22fa3cb-b8a4-4f1c-9ccd-fdf435246ac1,f32ecc8f-7018-457a-893e-876ba039bb1c,4fca9d87-2212-4b48-8b4b-52a2adb6ca86&ratingAcc=default&accountOverride=intl.mtvi.com&ep=82ac4273
	# FERTIG     = https://media-utils.mtvnservices.com/services/MediaGenerator/mgid:arc:video:mtv.de:837234d4-7002-11e9-a442-0e40cf2fc285?arcStage=live&format=json&acceptMethods=hls&clang=de&https=true
	if 'player/html5' in secondURL or not 'acceptMethods=hls' in secondURL:
		secondURL = DATA_1['feed']['items'][0]['group']['content'].replace('&device={device}', '')+'&format=json&acceptMethods=hls&tveprovider=null'
		# ERGEBNIS            = https://media-utils.mtvnservices.com/services/MediaGenerator/mgid:arc:musicvideo:mtv.intl:c188caed-fc02-11eb-9b1b-0e40cf2fc285?arcStage=live&accountOverride=intl.mtvi.com&billingSection=intl&device={device}&ep=82ac4273
		# FUNKTIONIERT = https://media-utils.mtvnservices.com/services/MediaGenerator/mgid:arc:musicvideo:mtv.intl:c188caed-fc02-11eb-9b1b-0e40cf2fc285?arcStage=live&accountOverride=intl.mtvi.com&billingSection=intl&ep=82ac4273&format=json&acceptMethods=hls&tveprovider=null
	content_2 = getUrl(secondURL, REF=BASE_URL)
	debug_MS("+++++++++++++++++++++++++")
	debug_MS("(navigator.getVideo) XXXXX CONTENT-02 : {0} XXXXX".format(str(content_2.strip())))
	debug_MS("+++++++++++++++++++++++++")
	DATA_2 = json.loads(content_2, object_pairs_hook=OrderedDict)
	try:
		subURL = DATA_2['package']['video']['item'][0]['transcript'][0]['typographic']
		for elem in subURL:
			if elem.get('format') == 'vtt' and elem.get('src', None):
				subSOURCE = elem['src']
	except: pass
	if subSOURCE and enableSUBTITLE:
		req = getUrl(subSOURCE, stream=True)
		with open(os.path.join(tempSF, subNAME+'.srt'), 'wb') as target:
			req.raw.decode_content = True
			shutil.copyfileobj(req.raw, target)
		subFOUND = True
	try:
		videoURL = DATA_2['package']['video']['item'][0]['rendition'][0]['src']
	except:
		code = '[COLOR red]'+DATA_2['package']['video']['item'][0]['code'].replace('_', ' ').upper()+'[/COLOR]'
		text = DATA_2['package']['video']['item'][0]['text']
		dialog.notification(code, text, icon, 8000)
		videoURL = '00'
		xbmc.sleep(5000)
	return (videoURL, subFOUND, subNAME)

def playCODE(IDD):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	debug_MS("(navigator.playCODE) ### IDD = {0} ###".format(IDD))
	subFOUND = False
	finalURL, subNAME= ('00' for _ in range(2))
	with open(WORKFILE, 'r') as wok:
		ARRIVE = json.load(wok)
		for elem in ARRIVE['videos']:
			if elem['filter'] != '00' and elem['filter'] == IDD:
				url = elem['url']
				seriesname = py2_enc(elem['tvshow'])
				name = py2_enc(elem['name'])
				photo = elem['pict']
				duration = elem['cycle']
				EXTRA = elem['extras']
				TRANS = elem['transmit']
				DISPLAY = elem['shortTITLE']
				debug_MS("(navigator.playCODE) ### WORKFILE-Line : {0} ###".format(str(elem)))
				finalURL, subFOUND, subNAME = getVideo(url, TRANS)
	if finalURL != '00':
		log("(navigator.playVideo) StreamURL : {0}".format(finalURL))
		subFILE = os.path.join(tempSF, subNAME+'.srt')
		listitem = xbmcgui.ListItem(path=finalURL)
		if subFOUND is True and subFILE:
			debug_MS("(navigator.playVideo) ##### subFOUND : {0} || subFILE : {1} #####".format(str(subFOUND), str(subFILE)))
			subFILE = subFILE.split('|')
			listitem.setSubtitles(subFILE)
			xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Player.SetSubtitle", "params":{"playerid":1, "subtitle":"on"}}')
			#xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Player.SetSubtitle", "params":{"playerid":1, "subtitle":"off"}}')
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive') and 'm3u8' in finalURL:
			listitem.setMimeType('application/vnd.apple.mpegurl')
			listitem.setProperty(INPUT_APP, 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem)
		xbmc.sleep(1000)
		if enableINFOS and EXTRA == 'NOTICE': infoMessage(DISPLAY)
	else:
		failing("(navigator.playVideo) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Stream-Eintrag auf der Webseite von *mtv.de* gefunden !!! ##########".format(url))
		return dialog.notification(translation(30521).format('VIDEO'), translation(30528), icon, 8000)

def playLIVE(url):
	debug_MS("(navigator.playLIVE) ------------------------------------------------ START = playLIVE -----------------------------------------------")
	log("(navigator.playLIVE) LIVEurl : {0}".format(url))
	listitem = xbmcgui.ListItem(path=url, label=translation(30633))
	listitem.setMimeType('application/vnd.apple.mpegurl')
	xbmc.Player().play(item=url, listitem=listitem)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def infoMessage(DISPLAY):
	count = 0
	while not xbmc.Player().isPlaying():
		xbmc.sleep(200)
		if count == 50:
			break
		count += 1
	xbmc.sleep(infoDelay*1000)
	if xbmc.Player().isPlaying():
		xbmc.getInfoLabel('Player.Duration')
		xbmc.getInfoLabel('Player.Art(thumb)')
		xbmc.sleep(500)
		RUNTIME = xbmc.getInfoLabel('Player.Duration')
		PHOTO = xbmc.getInfoLabel('Player.Art(thumb)')
		xbmc.sleep(1000)
		dialog.notification(translation(30634), DISPLAY+'[COLOR blue]  * '+RUNTIME+' *[/COLOR]', PHOTO, infoDuration*1000)
	else: pass

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, genre=None, folder=True, background=False):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Genre': genre})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and (not artpic in image or background is True):
		liz.setArt({'fanart': image})
	if params.get('extras') in ['newMU', 'MUSIC', 'SNAKE', 'CHART']:
		entries = []
		entries.append([translation(30655), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'extras': params.get('extras'),
			'transmit': params.get('transmit') if params.get('transmit') else 'special', 'page': params.get('page') if params.get('page') else '1', 'type': 'play'}))])
		liz.addContextMenuItems(entries, replaceItems=False)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

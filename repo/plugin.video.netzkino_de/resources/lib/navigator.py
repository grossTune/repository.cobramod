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
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote, unquote_plus  # Python 2.X
else: 
	from urllib.parse import urlencode, quote, unquote_plus  # Python 3.X

from .common import *


if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def mainMenu():
	addDir(translation(30601), artpic+'watchlist.png', {'mode': 'listShowsFavs'})
	config = traversing.get_config()
	for pick in config['picks']:
		title = pick['title']
		idd = str(pick['id'])
		catURL = config['category_entries'].format(idd)
		addDir(title, artpic+idd+'.png', {'mode': 'listVideos', 'url': catURL, 'extras': title})
	addDir(translation(30621), artpic+'genres.png', {'mode': 'listGenres'})
	#addDir(translation(30622), icon, {'mode': 'listAlphabet'})
	addDir(translation(30623), artpic+'search.png', {'mode': 'SearchNETZKINO'})
	if enableADJUSTMENT:
		addDir(translation(30624), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30625), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listGenres():
	debug_MS("(navigator.listThemes) ------------------------------------------------ START = listThemes -----------------------------------------------")
	config = traversing.get_config()
	for genre in config['genres']:
		title = genre['title']
		idd = str(genre['id'])
		image = (config['category_thumb'].format(idd) or icon)
		catURL = config['category_entries'].format(idd)
		if not approvedAge and idd == '71': continue
		addDir(title, image, {'mode': 'listVideos', 'url': catURL, 'extras': title})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet():
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	config = traversing.get_config()
	content = getUrl(config['index_all'])
	sublist = json.dumps(content)
	for letter in (('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')):
		addDir(letter, alppic+letter+'.jpg', {'mode': 'listCharacter', 'url': sublist, 'extras': letter})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listCharacter(Xurl, LETTER):
	debug_MS("(navigator.listCharacter) ------------------------------------------------ START = listCharacter -----------------------------------------------")
	debug_MS("(navigator.listCharacter) ### LETTER : {0} ###".format(LETTER))
	config = traversing.get_config()
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listCharacter) XXXXX CONTENT : {0} XXXXX".format(str(Xurl)))
	debug_MS("++++++++++++++++++++++++")
	DATA = json.loads(Xurl)
	for elem in DATA['categories']:
		title = cleaning(elem['title'])
		slug = (elem.get('slug', '') or "")
		if title[:1] == LETTER and not 'netzkinoplus' in slug:
			slug = (elem.get('slug', '') or "")
			idd = str(elem['id'])
			count = (str(elem.get('post_count', '')) or "")
			if count != "": title += '  ('+count+')'
			image = (config['category_thumb'].format(idd) or icon)
			catURL = config['category_entries'].format(idd)
			addDir(title, image, {'mode': 'listVideos', 'url': catURL, 'extras': title})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listVideos(url, CAT):
	debug_MS("(navigator.listVideos) ------------------------------------------------ START = listVideos -----------------------------------------------")
	debug_MS("(navigator.listVideos) ### URL : {0} ### CATEGORY : {1} ###".format(url, CAT))
	FOUND = 0
	DATA = getUrl(url)
	debug_MS("++++++++++++++++++++++++")
	debug_MS("(navigator.listVideos) XXXXX CONTENT : {0} XXXXX".format(str(DATA)))
	debug_MS("++++++++++++++++++++++++")
	for post in DATA['posts']:
		Note_1, Note_2 = ("" for _ in range(2))
		aired, begins, background, age, mpaa, year, score, rating, cast, director, genre, quality, youtubeID, duration = (None for _ in range(14))
		if 'Streaming' in post.get('custom_fields', {}) and not 'plus-exclusive' in post.get('properties'):
			def get_fields(_post, field_name):
				custom_fields = post.get('custom_fields', {})
				field = custom_fields.get(field_name, [])
				if len(field) >= 1:
					return cleaning(field[0])
				return None
			FOUND += 1
			slug = (post.get('slug', '') or "")
			idd = str(post['id'])
			title = cleaning(post['title'])
			try:
				broadcast = datetime(*(time.strptime(post['modified'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2021-02-17 15:41:49
				aired = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
				begins = broadcast.strftime('%d{0}%m{0}%Y').format('.')
			except: pass
			if aired:
				Note_1 = translation(30644).format(str(aired))
			Note_2 = get_Description(post)
			if 'thumbnail' in post:
				image = (post.get('thumbnail') or "")
			else:
				image = get_fields(post, 'Artikelbild')
			background = get_fields(post, 'featured_img_all')
			stream = get_fields(post, 'Streaming')
			age = get_fields(post, 'FSK')
			if age and age != '0':
				mpaa = translation(30645).format(str(age))
				if not approvedAge and str(age) == '18': continue
			year = get_fields(post, 'Jahr')
			score = get_fields(post, 'IMDb-Bewertung')
			if score and score != '0': rating = score.replace(',', '.')
			cast = get_fields(post, 'Stars')
			director = get_fields(post, 'Regisseur')
			genre = get_fields(post, 'TV_Movie_Genre')
			quality = get_fields(post, 'Adaptives_Streaming')
			if quality and quality == 'HD': title += translation(30646)
			youtubeID = get_fields(post, 'Youtube_Delivery_Id')
			duration = get_fields(post, 'Duration')
			plot = title+'[CR]'+Note_1+Note_2
			addType = 1
			if xbmcvfs.exists(videoFavsFile):
				with open(videoFavsFile, 'r') as fp:
					watch = json.load(fp)
					for item in watch.get('items', []):
						if item.get('url') == stream: addType = 2
			addLink(title, image, {'mode': 'playVideo', 'url': stream}, plot, duration, begins, year, genre, director, cast, rating, mpaa, background, addType)
	if FOUND >= 1:
		for method in getSorting():
			xbmcplugin.addSortMethod(ADDON_HANDLE, method)
	else:
		debug_MS("(navigator.listVideos) ##### Keine VIDEO-List - Kein Eintrag gefunden #####")
		return dialog.notification(translation(30522).format('Einträge'), translation(30525).format(unquote_plus(CAT)), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchNETZKINO():
	debug_MS("(navigator.SearchNETZKINO) ------------------------------------------------ START = SearchNETZKINO -----------------------------------------------")
	config = traversing.get_config()
	keyword = None
	if xbmcvfs.exists(searchHackFile):
		with open(searchHackFile, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30626), type=xbmcgui.INPUT_ALPHANUM, autoclose=10000)
		if keyword:
			keyword = quote(keyword)
			with open(searchHackFile, 'w') as record:
				record.write(keyword)
	if keyword: return listVideos(config['search_query'].format(keyword), keyword)
	return None

def playVideo(SLUG):
	debug_MS("(navigator.playVideo) ------------------------------------------------ START = playVideo -----------------------------------------------")
	debug_MS("(navigator.playVideo) ### URL : {0} ###".format(SLUG))
	finalURL, streamTYPE = (False for _ in range(2))
	config = traversing.get_config()
	if (prefSTREAM == '0' or enableINPUTSTREAM):
		finalURL = config['streaming_hls'].format(SLUG)
		streamTYPE = 'M3U8/HLS'
	if not finalURL:
		finalURL = config['streaming_pmd'].format(SLUG)
		streamTYPE = 'MP4'
	if finalURL and streamTYPE:
		log("(navigator.playVideo) {0}_stream : {1}".format(streamTYPE, finalURL))
		listitem = xbmcgui.ListItem(path=finalURL)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive') and streamTYPE == 'M3U8/HLS':
			listitem.setMimeType('application/vnd.apple.mpegurl')
			listitem.setProperty(INPUT_APP, 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem)
	else: 
		failing("(navigator.playVideo) ##### Die angeforderte Video-Url wurde leider NICHT gefunden !!! #####")
		return dialog.notification(translation(30521).format('PLAY'), translation(30526), icon, 8000)

def listShowsFavs():
	debug_MS("(navigator.listShowsFavs) ------------------------------------------------ START = listShowsFavs -----------------------------------------------")
	for method in getSorting():
		xbmcplugin.addSortMethod(ADDON_HANDLE, method)
	if xbmcvfs.exists(videoFavsFile):
		with open(videoFavsFile, 'r') as fp:
			watch = json.load(fp)
			for item in watch.get('items', []):
				name = cleaning(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else item.get('pict')
				desc = None if item.get('plot', 'None') == 'None' else cleaning(item.get('plot'))
				debug_MS("(navigator.listShowsFavs) ### NAME : {0} || URL : {1} || IMAGE : {2} ###".format(name, item.get('url'), logo))
				addLink(name, logo, {'mode': 'playVideo', 'url': item.get('url')}, desc, item.get('duration'), item.get('begins'), item.get('year'), cleaning(item.get('genre')), cleaning(item.get('director')), cleaning(item.get('cast')), item.get('rating'), item.get('mpaa'), item.get('background'), FAVclear=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(videoFavsFile):
		with open(videoFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'plot': plot, 'duration': duration, 'begins': begins, 'year': year, 'genre': genre, 'director': director, 'cast': cast, 'rating': rating, 'mpaa': mpaa, 'background': background})
		with open(videoFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30527), translation(30528).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('url') != url]
		with open(videoFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30527), translation(30529).format(name), icon, 8000)

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, background=None, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Studio': 'Netzkino'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if background and useThumbAsFanart and background != icon:
		liz.setArt({'fanart': background})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot=None, duration=None, begins=None, year=None, genre=None, director=None, cast=None, rating=None, mpaa=None, background=None, addType=0, FAVclear=False):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	info = {}
	info['Tvshowtitle'] = name
	info['Title'] = name
	info['Tagline'] = None
	info['Plot'] = plot
	info['Duration'] = duration
	if begins is not None:
		info['Date'] = begins
	info['Year'] = year
	info['Genre'] = [genre]
	info['Director'] = [director]
	info['Cast'] = [cast]
	info['Studio'] = 'Netzkino'
	info['Rating'] = rating
	info['Mpaa'] = mpaa
	info['Mediatype'] = 'movie'
	liz.setInfo(type='Video', infoLabels=info)
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if background and useThumbAsFanart and background != icon:
		liz.setArt({'fanart': background})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	entries = []
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'ADD', 'name': name, 'pict': 'None' if image == icon else image, 'url': params.get('url'),
			'plot': 'None' if plot == None else plot.replace('\n', '[CR]'), 'duration': duration, 'begins': begins, 'year': year, 'genre': genre, 'director': director, 'cast': cast, 'rating': rating, 'mpaa': mpaa, 'background': background}))])
	if FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url'),
			'plot': plot, 'duration': duration, 'begins': begins, 'year': year, 'genre': genre, 'director': director, 'cast': cast, 'rating': rating, 'mpaa': mpaa, 'background': background}))])
	entries.append([translation(30654), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)'])
	liz.addContextMenuItems(entries, replaceItems=False)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)

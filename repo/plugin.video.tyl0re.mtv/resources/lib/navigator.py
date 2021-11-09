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
import time
from datetime import datetime, timedelta
from collections import OrderedDict
from bs4 import BeautifulSoup
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote_plus  # Python 2.X
else:
	from urllib.parse import urlencode, quote_plus  # Python 3.X

from .common import *


def mainMenu():
	addDir(translation(30601), icon, {'mode': 'listBroadcasts', 'url': BASE_URL+'/shows'})
	addDir(translation(30602), icon, {'mode': 'listMusics', 'url': BASE_URL+'/musik'})
	addDir(translation(30603), icon, {'mode': 'listCharts', 'url': BASE_URL+'/charts/c6mc86/single-top-100'})
	addDir(translation(30604), icon, {'mode': 'musicPart', 'url': BASE_URL+'/playlists'})
	addDir(translation(30605), icon, {'mode': 'listAlphabet'})
	addDir(translation(30606), artpic+'livestream.png', {'mode': 'playLIVE', 'url': BASE_URL+'/live/0h9eak/mtv-germany-live'}, folder=False)
	addDir(translation(30607).format(str(cachePERIOD)), artpic+'remove.png', {'mode': 'clearCache'})
	if enableADJUSTMENT:
		addDir(translation(30608), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30609), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBroadcasts(url):
	debug_MS("(navigator.listBroadcasts) ------------------------------------------------ START = listBroadcasts -----------------------------------------------")
	prefer = {'INTL_M150':'Alle Shows von A-Z', 'INTL_M300':'Neueste Folgen', 'INTL_M012':'Highlights'}
	firstURL = 'http://www.mtv.de/feeds/triforce/manifest/v8?url='+quote_plus(url)
	debug_MS("(navigator.listBroadcasts) ### URL : {0} ###".format(firstURL))
	content = makeREQUEST(firstURL, XMLH=True)
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for modul, name in prefer.items():
		action = 'seasonVideos' if 'M300' in modul else 'listSeries'
		special = 'highlights' if 'M012' in modul else 'standard'
		for key, value in DATA['manifest']['zones'].items():
			if value['moduleName'] == modul:
				debug_MS("(navigator.listBroadcasts) ##### NAME = {0} || URL = {1} #####".format(str(name), value['feed']))
				addDir(name, icon, {'mode': action, 'url': value['feed'], 'transmit': special})
	addDir(translation(30610), icon, {'mode': 'artistPart', 'url': BASE_URL+'/buzz', 'extras': 'MTV Buzz'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSeries(url, transmit):
	debug_MS("(navigator.listSeries) ------------------------------------------------ START = listSeries -----------------------------------------------")
	debug_MS("(navigator.listSeries) ### URL : {0} ### TYPE : {1} ###".format(url, transmit))
	content = makeREQUEST(url, XMLH=True)
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	if transmit == 'highlights':
		for item in DATA['result']['data']['items']:
			title = cleaning(item['title'])
			canonical = item['canonicalURL']
			photo = item['images']['url']
			debug_MS("(navigator.listSeries) no.01 ##### NAME = {0} || canonicalURL = {1} #####".format(str(title), canonical))
			addDir(title, photo, {'mode': 'listSeasons', 'url': canonical, 'extras': photo})
	else:
		for letter in DATA['result']['shows']:
			for serie in letter['value']:
				IDD = str(serie['itemId'])
				title = cleaning(serie['title'])
				newURL = serie['url']
				photo = 'http://mtv-intl.mtvnimages.com/uri/mgid:arc:content:mtv.de:'+IDD+'?ep=mtv.de&stage=live&format=jpg&quality=0.8&quality=0.8&quality=0.85&width=1024&height=576&crop=true'
				debug_MS("(navigator.listSeries) no.02 ##### NAME = {0} || newURL = {1} #####".format(str(title), newURL))
				addDir(title, photo, {'mode': 'listSeasons', 'url': newURL, 'extras': photo})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSeasons(url, THUMB):
	debug_MS("(navigator.listSeasons) ------------------------------------------------ START = listSeasons -----------------------------------------------")
	FOUND = 0
	firstURL = 'http://www.mtv.de/feeds/triforce/manifest/v8?url='+quote_plus(url)
	debug_MS("(navigator.listSeasons) ### URL-1 : {0} ###".format(firstURL))
	content_1 = makeREQUEST(firstURL, XMLH=True)
	secondURL = json.loads(content_1)['manifest']['zones']['t2_lc_promo1']['feed']
	debug_MS("(navigator.listSeasons) ### URL-2 : {0} ###".format(secondURL))
	content_2 = makeREQUEST(secondURL, XMLH=True)
	DATA = json.loads(content_2, object_pairs_hook=OrderedDict)
	for item in DATA['result']['data']['seasons']:
		FOUND += 1
		IDD = str(item['id'])
		title = cleaning(item['eTitle'])
		plot = get_Description(item)
		canonical = item['canonicalURL']
		debug_MS("(navigator.listSeasons) ##### NAME = {0} || canonicalURL = {1} #####".format(str(title), canonical))
		addDir(title, THUMB, {'mode': 'seasonPart', 'url': canonical}, plot)
	if FOUND == 0:
		return dialog.notification(translation(30522).format('Einträge'), translation(30524), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def seasonPart(url):
	firstURL = 'http://www.mtv.de/feeds/triforce/manifest/v8?url='+quote_plus(url)
	debug_MS("(navigator.seasonPart) ### URL-1 : {0} ###".format(firstURL))
	content = makeREQUEST(firstURL, XMLH=True)
	secondURL = json.loads(content)['manifest']['zones']['t4_lc_promo1']['feed']
	return seasonVideos(secondURL, 'episodes')

def seasonVideos(url, transmit):
	debug_MS("(navigator.seasonVideos) ------------------------------------------------ START = seasonVideos -----------------------------------------------")
	debug_MS("(navigator.seasonVideos) ### URL : {0} ### TYPE : {1} ###".format(url, transmit))
	COMBI_EPISODE = []
	UNIKAT = set()
	pos1, pos3 = (0 for _ in range(2))
	TIME = 30
	pageNUMBER = 1
	total = 1
	while (total > 0):
		newURL =url+'&pageNumber='+str(pageNUMBER)+'&fullEpisodes=1' if pageNUMBER > 1 else url
		content = makeREQUEST(newURL, XMLH=True)
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		if 'result' in DATA and 'data' in DATA['result'] and 'items' in DATA['result']['data'] and len(DATA['result']['data']['items']) > 0:
			if (transmit == 'standard' and pageNUMBER < 11) or (transmit == 'episodes' and pageNUMBER < 16):
				for item in DATA['result']['data']['items']:
					debug_MS("(navigator.seasonVideos) no.01 XXXXX EPISODES : {0} XXXXX".format(str(item)))
					seriesname, Note_1, Note_2, photo, pos2 = ("" for _ in range(5))
					season, episode, duration = ('0' for _ in range(3))
					startTIMES, year = (None for _ in range(2))
					canonical = item['canonicalURL']
					if item.get('headline', ''):
						if transmit == 'episodes' and item.get('showTitle', ''):
							Note_1 = '[COLOR yellow]'+cleaning(item['showTitle'])+' - '+cleaning(item['headline'])+'[/COLOR][CR]'
							seriesname = cleaning(item['showTitle'])
						elif transmit == 'standard':
							Note_1 = '[COLOR yellow]'+cleaning(item['headline'])+'[/COLOR][CR]'
							seriesname = cleaning(item['headline'])
					if str(item.get('publishDate', '')).isdigit():
						startDATES = datetime(1970, 1, 1) + timedelta(seconds=int(item['publishDate']))
						startTIMES = startDATES.strftime('%d{0}%m{0}%Y').format('.')
						year = startDATES.strftime('%Y')
					if startTIMES and not '1970' in startTIMES: Note_2 = translation(30620).format(str(startTIMES))
					else:
						if Note_1 != "": Note_2 = '[CR]'
					plot = Note_1+Note_2+get_Description(item)
					if item.get('duration', ''):
						duration = get_Seconds(item['duration'])
					IDD = str(item['id'])
					if IDD in UNIKAT:
						continue
					UNIKAT.add(IDD)
					pos1 += 1
					if 'images' in item and len(item['images']) > 0:
						photo = item['images']['url']
					title = cleaning(item['contentLabel'])
					if not 'Episode' in item['title'] and not 'Folge' in item['title'] and not item['title'] in item['contentLabel']:
						title = title+' - '+cleaning(item['title'])
					if item.get('season', ''):
						season = str(item['season']).zfill(2)
					if item.get('episode', ''):
						episode = str(item['episode']).zfill(2)
					if season != '0' and episode != '0':
						pos2 = 'S'+season+'E'+episode
					else: pos3 += 1
					COMBI_EPISODE.append([pageNUMBER, season, episode, title, photo, canonical, IDD, plot, duration, seriesname, year, pos1, pos2, pos3])
			else: total = 0
		else: total = 0
		try:
			nextPG = DATA['result']['nextPageURL']
			numIT = DATA['result']['totItems']
			debug_MS("+++++++++++++++++++++++++")
			debug_MS("(navigator.seasonVideos) NEXTPAGE FOUND : {0}".format(nextPG))
		except: total = 0
		pageNUMBER += 1
	if COMBI_EPISODE:
		debug_MS("~~~~~~~~~~~~~~~~~~~~~~~~~")
		if transmit == 'episodes':
			for sign in COMBI_EPISODE:
				if sign[13] <= 5:
					COMBI_EPISODE = sorted(COMBI_EPISODE, key=lambda k: k[12], reverse=True)
				else:
					COMBI_EPISODE = sorted(COMBI_EPISODE, key=lambda k: (k[0], k[11]), reverse=False)
		for pageNUMBER, season, episode, title, photo, canonical, IDD, plot, duration, seriesname, year, pos1, pos2, pos3 in COMBI_EPISODE:
			debug_MS("(navigator.seasonVideos) no.02 ##### TITLE = {0} || canonicalURL = {1} || IDD = {2} #####".format(str(title), canonical, IDD))
			debug_MS("(navigator.seasonVideos) no.02 ##### FOTO = {0} || SEASON = {1} || EPISODE = {2} #####".format(photo, str(season), str(episode)))
			cineType = 'episode' if episode != '0' else 'movie'
			addLink(title, photo, {'mode': 'playVideo', 'url': canonical, 'transmit': IDD, 'cineType': cineType}, plot, duration, seriesname, season, episode, year)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listCharts(url):
	debug_MS("(navigator.listCharts) ------------------------------------------------ START = listCharts -----------------------------------------------")
	firstURL = 'http://www.mtv.de/feeds/triforce/manifest/v8?url='+quote_plus(url)
	debug_MS("(navigator.listCharts) ### URL-1 : {0} ###".format(firstURL))
	content_1 = makeREQUEST(firstURL, XMLH=True)
	secondURL = json.loads(content_1)['manifest']['zones']['t2_lc_promo1']['feed']
	debug_MS("(navigator.listCharts) ### URL-2 : {0} ###".format(secondURL))
	content_2 = makeREQUEST(secondURL, XMLH=True)
	DATA = json.loads(content_2, object_pairs_hook=OrderedDict)
	for item in DATA['result']['featuredChartTypes']:
		title = cleaning(item['title']).replace('Offizielle ', '')
		shortTitle = item['shortTitle']
		canonical = item['canonicalURL']
		if not 'Album' in shortTitle and not 'Hip Hop' in shortTitle:
			debug_MS("(navigator.listCharts) ##### NAME = {0} || canonicalURL = {1} #####".format(str(title), canonical))
			addDir(title, icon, {'mode': 'chartPart', 'url': canonical})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def chartPart(url):
	firstURL = 'http://www.mtv.de/feeds/triforce/manifest/v8?url='+quote_plus(url)
	debug_MS("(navigator.chartPart) ### URL-1 : {0} ###".format(firstURL))
	content = makeREQUEST(firstURL, XMLH=True)
	secondURL = json.loads(content)['manifest']['zones']['t4_lc_promo1']['feed']
	return chartVideos(secondURL)

def chartVideos(url):
	debug_MS("(navigator.chartVideos) ------------------------------------------------ START = chartVideos -----------------------------------------------")
	debug_MS("(navigator.chartVideos) ### URL : {0} ###".format(url))
	content = makeREQUEST(url, XMLH=True)
	DATA = json.loads(content, object_pairs_hook=OrderedDict)['result']
	for item in DATA['data']['items']:
		artist, photo, oldpos = ("" for _ in range(3))
		song = cleaning(item['title'])
		if item.get('shortTitle', ''):
			artist = cleaning(item['shortTitle'])
		if artist == "" and 'artists' in item and 'name' in str(item['artists']):
			artist = cleaning(item['artists'][0]['name'])
		chartpos = item['chartPosition']['current']
		if 'images' in item and 'url' in str(item['images']):
			photo = item['images'][0]['url']
		try: videoUrl = item['videoUrl']
		except:
			try: videoUrl = re.compile("'videoUrl'[^']+'(.+?)'", re.DOTALL).findall(str(item))[0]
			except: videoUrl = '00'
		try:
			down = item['chartPosition']['moveDown']
			old = item['chartPosition']['previous']
			oldpos = '[COLOR red]  ( - '+str(chartpos-old) + ' )[/COLOR]'
		except: pass
		try:
			down = item['chartPosition']['moveUp']
			old = int(item['chartPosition']['previous'])
			oldpos = '[COLOR green]  ( + '+str(old-chartpos) + ' )[/COLOR]'
		except: pass
		try:
			neu = item['chartPosition']['variation']
			oldpos = '[COLOR deepskyblue]  ( NEU )[/COLOR]' if neu == 'neu' else "  ( - )"
		except: pass
		debug_MS("(navigator.chartVideos) ##### TITLE = {0} || videoUrl = {1} || FOTO = {2} #####".format(str(chartpos)+'. '+song+' - '+artist, videoUrl, photo))
		if videoUrl != '00' and artist != "":
			title = translation(30621).format(str(chartpos), song, artist+oldpos)
			addLink(title, photo, {'mode': 'playVideo', 'url': videoUrl, 'transmit': 'unknown', 'cineType': 'movie'}, artist=artist, tracknumber=chartpos)
		elif videoUrl == '00' and artist != "" and showALL:
			title = translation(30622).format(str(chartpos), song, artist+oldpos)
			addLink(title, photo, {'mode': 'blankFUNC', 'url': videoUrl, 'cineType': 'movie'}, artist=artist, tracknumber=chartpos)
	try:
		nextPG = DATA['nextPageURL']
		debug_MS("(navigator.chartVideos) NEXTPAGE FOUND : {0}".format(nextPG))
		return chartVideos(nextPG)
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listMusics(url):
	debug_MS("(navigator.listMusics) ------------------------------------------------ START = listMusics -----------------------------------------------")
	prefer = {'t4_lc_promo1':'Neueste Musikvideos', 't5_lc_promo1':'Hits', 't6_lc_promo1':'Made In Germany', 't7_lc_promo1':'Hip Hop', 't8_lc_promo1':'Upcoming', 't9_lc_promo1':'Alternative', 't10_lc_promo1':'Dance', 't11_lc_promo1':'Pop'}
	firstURL = 'http://www.mtv.de/feeds/triforce/manifest/v8?url='+quote_plus(url)
	debug_MS("(navigator.listMusics) ### URL : {0} ###".format(firstURL))
	content = makeREQUEST(firstURL, XMLH=True)
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for key, value in DATA['manifest']['zones'].items():
		for modul, name in prefer.items():
			if value['zone'] == modul:
				debug_MS("(navigator.listMusics) ##### NAME = {0} || FEED = {1} #####".format(str(name), value['feed']))
				addDir(name, icon, {'mode': 'musicVideos', 'url': value['feed'], 'transmit': 'musicvideo'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def musicPart(url):
	firstURL = 'http://www.mtv.de/feeds/triforce/manifest/v8?url='+quote_plus(url)
	debug_MS("(navigator.musicPart) ### URL-1 : {0} ###".format(firstURL))
	content = makeREQUEST(firstURL, XMLH=True)
	secondURL = json.loads(content)['manifest']['zones']['t4_lc_promo1']['feed']
	return musicVideos(secondURL, 'compilation')

def musicVideos(url, transmit):
	debug_MS("(navigator.musicVideos) ------------------------------------------------ START = musicVideos -----------------------------------------------")
	debug_MS("(navigator.musicVideos) ### URL : {0} ### TYPE : {1} ###".format(url, transmit))
	content = makeREQUEST(url, XMLH=True)
	DATA = json.loads(content, object_pairs_hook=OrderedDict)['result']
	for item in DATA['data']['items']:
		debug_MS("(navigator.musicVideos) no.01 XXXXX ITEM : {0} XXXXX".format(str(item)))
		artist, photo, count = ("" for _ in range(3))
		duration = '0'
		song = cleaning(item['title'])
		if item.get('artist', ''):
			artist = cleaning(item['artist'])
		title = song+' - '+artist if artist != "" else song
		canonical = item['canonicalURL']
		if 'images' in item and len(item['images']) > 0:
			photo = item['images']['url']
		if item.get('duration', ''):
			duration = get_Seconds(item['duration']) if transmit == 'musicvideo' else str(item['duration'])
		if item.get('itemNumber', ''):
			count = str(item['itemNumber'])
		debug_MS("(navigator.musicVideos) no.02 ##### NAME = {0} || canonicalURL = {1} || FOTO = {2} #####".format(str(title), canonical, photo))
		if transmit == 'musicvideo':
			title = translation(30623).format(str(count), title) if count != "" else title
			addLink(title, photo, {'mode': 'playVideo', 'url': canonical, 'transmit': 'unknown', 'cineType': 'movie'}, duration=duration)
		else:
			plot = translation(30624).format(title, str(duration)) if duration != '0' else title
			addDir(title, photo, {'mode': 'playCompilation', 'url': canonical, 'transmit': transmit}, plot)
	try:
		nextPG = DATA['nextPageURL']
		debug_MS("(navigator.musicVideos) NEXTPAGE FOUND : {0}".format(nextPG))
		return musicVideos(nextPG, transmit)
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playCompilation(url):
	debug_MS("(navigator.playCompilation) ------------------------------------------------ START = playCompilation -----------------------------------------------")
	debug_MS("(navigator.playCompilation) ### URL : {0} ###".format(url))
	COMBI_VIDEO = []
	PL = xbmc.PlayList(1)
	PL.clear()
	pos_LISTE = 0
	content_1 = makeREQUEST(url)
	soup = BeautifulSoup(content_1, 'html.parser')
	feedURL = soup.find('div', id='t1_lc_promo1')['data-tffeed']
	debug_MS("(navigator.playCompilation) no.01 ### feedURL : {0} ###".format(feedURL))
	content_2 = makeREQUEST(feedURL)
	if '{"envelope":{"version":"1.0","name":"entertainment-standard-json"},"status":{"text":"OK","code":100},"result":{"brand":"mtv"' in content_2:
		DATA = json.loads(content_2, object_pairs_hook=OrderedDict)
		for item in DATA['result']['data']['items']:
			artist, photo = ("" for _ in range(2))
			canonical = cleaning(item['canonicalURL'])
			plot = get_Description(item)
			duration = get_Seconds(item['duration'])
			IDD = str(item['id'])
			videoURL, subFOUND, subNAME = getVideo(canonical, IDD)
			if videoURL == '00': continue
			pos_LISTE += 1
			song = cleaning(item['title'])
			if item.get('artist', ''):
				artist = cleaning(item['artist'])
			title = song+' - '+artist if artist != "" else song
			if 'images' in item and len(item['images']) > 0:
				photo = item['images']['url']
			COMBI_VIDEO.append([title, videoURL, photo, plot, duration, pos_LISTE])
		for title, videoURL, photo, plot, duration, pos_LISTE in COMBI_VIDEO:
			debug_MS("(navigator.playCompilation) ##### TITLE = {0} || videoURL = {1} || FOTO = {2} #####".format(str(title), videoURL, photo))
			NRS_title = '[COLOR chartreuse]'+str(pos_LISTE).zfill(2)+' •  [/COLOR]'+title
			listitem = xbmcgui.ListItem(title)
			listitem.setInfo(type='Video', infoLabels={'Title': NRS_title, 'Plot': plot, 'Duration': duration, 'Mediatype': 'video'})
			listitem.setArt({'icon': icon, 'thumb': photo, 'poster': photo})
			listitem.setProperty('IsPlayable', 'true')
			xbmc.sleep(50)
			PL.add(url=videoURL, listitem=listitem, index=pos_LISTE)
		xbmc.Player().play(PL)
	else: return dialog.notification(translation(30521).format('PLAYLIST'), translation(30526), icon, 8000)

def listAlphabet():
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	for letter in (('0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')):
		addDir(letter, alppic+letter+'.jpg', {'mode': 'listArtists', 'url': BASE_URL+'/kuenstler/'+letter.lower()+'/1'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listArtists(url):
	debug_MS("(navigator.listArtists) ------------------------------------------------ START = listArtists -----------------------------------------------")
	debug_MS("(navigator.listArtists) ### URL : {0} ###".format(url))
	content = makeREQUEST(url)
	soup = BeautifulSoup(content, 'html.parser')
	artists = soup.find('div', class_='artists').find_all('li')
	for entries in artists:
		elem = str(entries)
		newURL = re.findall('"@id":"([^"]+?)"', elem, re.S)[0]
		name = re.findall('"name":"([^"]+?)"', elem, re.S)[0]
		name = name.replace('\\/', '/').encode().decode('unicode_escape', 'ignore') # special-encoding for json-characters like = \u00f6 to  Umlaut "ö" ...
		try: photo = re.findall('"image":"([^"]+?)"', elem, re.S)[0]
		except: photo = ""
		debug_MS("(navigator.listArtists) ##### NAME = {0} || newURL = {1} || FOTO = {2} #####".format(cleaning(name), newURL, photo))
		addDir(cleaning(name), photo, {'mode': 'artistPart', 'url': newURL, 'extras': cleaning(name)})
	try:
		nextPG = soup.find('a', class_='page next link')['href']
		debug_MS("(navigator.listArtists) NEXTPAGE FOUND : {0}".format(nextPG))
		addDir(translation(30625), artpic+'nextpage.png', {'mode': 'listArtists', 'url': nextPG})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def artistPart(url, SECTOR):
	firstURL = 'http://www.mtv.de/feeds/triforce/manifest/v8?url='+quote_plus(url)
	debug_MS("(navigator.artistPart) ### URL-1 : {0} ###".format(firstURL))
	content = makeREQUEST(firstURL, XMLH=True)
	secondURL = json.loads(content)['manifest']['zones']['t4_lc_promo1']['feed']
	return artistVideos(secondURL, SECTOR)

def artistVideos(url, SECTOR):
	debug_MS("(navigator.artistVideos) ------------------------------------------------ START = artistVideos -----------------------------------------------")
	debug_MS("(navigator.artistVideos) ### URL : {0} ### NAME : {1} ###".format(url, SECTOR))
	COMBI_VIDEO = []
	UNIKAT = set()
	pos1 = 0
	pageNUMBER = 1
	total = 1
	while (total > 0):
		newURL = url+'/'+str(pageNUMBER)
		content = makeREQUEST(newURL, XMLH=True)
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		if 'result' in DATA and 'data' in DATA['result'] and 'items' in DATA['result']['data'] and len(DATA['result']['data']['items']) > 0:
			if (SECTOR == 'MTV Buzz' and pageNUMBER < 5) or (SECTOR != 'MTV Buzz' and pageNUMBER < 16):
				for item in DATA['result']['data']['items']:
					debug_MS("(navigator.artistVideos) no.01 XXXXX VIDEO : {0} XXXXX".format(str(item)))
					Note_1, photo = ("" for _ in range(2))
					startTIMES = None
					IDD = str(item['id'])
					if IDD in UNIKAT:
						continue
					UNIKAT.add(IDD)
					if str(item.get('airDate', '')).isdigit():
						startDATES = datetime(1970, 1, 1) + timedelta(seconds=int(item['airDate']))
						startTIMES = startDATES.strftime('%d{0}%m{0}%Y').format('-')
					if startTIMES and not '1970' in startTIMES: Note_1 = '[COLOR chartreuse]'+str(startTIMES)+'[/COLOR][CR]'
					canonical = cleaning(item['canonicalURL'])
					plot = Note_1+get_Description(item)
					duration = get_Seconds(item['duration'])
					if duration == '0': continue
					pos1 += 1
					title = cleaning(item['contentLabel'])
					if not 'Episode' in item['title'] and not 'Folge' in item['title'] and not item['title'] in item['contentLabel']:
						title += ' - '+cleaning(item['title'])
					if 'images' in item and len(item['images']) > 0:
						photo = item['images']['url']
					COMBI_VIDEO.append([pageNUMBER, title, photo, canonical, IDD, plot, duration, pos1])
			else: total = 0
		else: total = 0
		try:
			nextPG = DATA['result']['nextPageURL']
			numIT = DATA['result']['totItems']
			debug_MS("+++++++++++++++++++++++++")
			debug_MS("(navigator.artistVideos) NEXTPAGE FOUND : {0}".format(nextPG))
		except: total = 0
		pageNUMBER += 1
	if COMBI_VIDEO:
		debug_MS("~~~~~~~~~~~~~~~~~~~~~~~~~")
		COMBI_VIDEO = sorted(COMBI_VIDEO, key=lambda k: (k[0], k[7]), reverse=False)
		for pageNUMBER, title, photo, canonical, IDD, plot, duration, pos1 in COMBI_VIDEO:
			debug_MS("(navigator.artistVideos) no.02 ##### TITLE = {0} || canonicalURL = {1} || FOTO = {2} #####".format(str(title), canonical, photo))
			addLink(title, photo, {'mode': 'playVideo', 'url': canonical, 'transmit': IDD, 'cineType': 'movie'}, plot, duration)
	else:
		return dialog.notification(translation(30522).format('Einträge'), translation(30525).format(SECTOR), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def getVideo(url, transmit):
	if xbmcvfs.exists(tempSF) and os.path.isdir(tempSF):
		shutil.rmtree(tempSF, ignore_errors=True)
		xbmc.sleep(500)
	xbmcvfs.mkdirs(tempSF)
	subSOURCE = False
	subFOUND = False
	if transmit == 'unknown':
		content = getUrl(url)
		transmit = re.compile('"itemId":"(.+?)"', re.DOTALL).findall(content)[0]
	firstURL = 'http://media.mtvnservices.com/pmt/e1/access/index.html?uri=mgid:arc:episode:mtv.de:'+transmit+'&configtype=edge'
	content_1 = getUrl(firstURL, 'GET', url)
	debug_MS("+++++++++++++++++++++++++")
	debug_MS("(navigator.getVideo) XXXXX CONTENT-01 : {0} XXXXX".format(str(content_1)))
	debug_MS("+++++++++++++++++++++++++")
	DATA_1 = json.loads(content_1, object_pairs_hook=OrderedDict)
	try: guid = DATA_1['feed']['items'][0]['guid']
	except: guid = DATA_1['uri']
	try: subNAME = DATA_1['configURL'].split('%2f')[-1].replace('&fasLogic=true', '')
	except: subNAME = 'TemporaryVideoSub'
	mediaURL = DATA_1['mediaGen'].replace('&device={device}', '').replace('{uri}', guid)
	#https://media-utils.mtvnservices.com/services/MediaGenerator/mgid:arc:video:mtv.de:837234d4-7002-11e9-a442-0e40cf2fc285?arcStage=live&format=json&acceptMethods=hls&clang=de&https=true
	content_2 = getUrl(mediaURL, 'GET', url)
	debug_MS("+++++++++++++++++++++++++")
	debug_MS("(navigator.getVideo) XXXXX CONTENT-02 : {0} XXXXX".format(str(content_2)))
	debug_MS("+++++++++++++++++++++++++")
	DATA_2 = json.loads(content_2, object_pairs_hook=OrderedDict)
	try:
		subURL = DATA_2['package']['video']['item'][0]['transcript'][0]['typographic']
		for elem in subURL:
			if elem.get('format') == 'vtt' and elem.get('src', None):
				subSOURCE = elem['src']
	except: pass
	if subSOURCE and enableSUBTITLE:
		req = getUrl(subSOURCE, 'GET', stream=True)
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
	return (videoURL, subFOUND, subNAME)

def playVideo(url, transmit):
	debug_MS("(navigator.playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	debug_MS("(navigator.playVideo) ### URL : {0} ### TYPE : {1} ###".format(url, transmit))
	finalURL, subFOUND, subNAME = getVideo(url, transmit)
	subFILE = os.path.join(tempSF, subNAME+'.srt')
	if finalURL != '00':
		log("(navigator.playVideo) StreamURL : {0}".format(finalURL))
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
	else:
		failing("(navigator.playVideo) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Stream-Eintrag auf der Webseite von *mtv.de* gefunden !!! ##########".format(url))
		return dialog.notification(translation(30521).format('VIDEO'), translation(30527), icon, 8000)

def playLIVE(url):
	debug_MS("(navigator.playLIVE) ------------------------------------------------ START = playLIVE -----------------------------------------------")
	liveURL, subFOUND, subNAME = getVideo(url, 'unknown')
	if liveURL != '00':
		newM3U8 = getUrl(liveURL)
		M3U8_Url = re.compile('(https?://.*?.m3u8)', re.DOTALL).findall(newM3U8)[-1]
		log("(navigator.playLIVE) LIVEurl : {0}".format(M3U8_Url))
		listitem = xbmcgui.ListItem(path=M3U8_Url, label=translation(30626))
		listitem.setMimeType('application/vnd.apple.mpegurl')
		xbmc.Player().play(item=M3U8_Url, listitem=listitem)
	else:
		failing("(navigator.playLIVE) ##### Abspielen des Live-Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Live-Stream-Eintrag auf der Webseite von *mtv.de* gefunden !!! ##########".format(url))
		return dialog.notification(translation(30521).format('LIVE'), translation(30527), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot=None, duration=None, seriesname=None, season=None, episode=None, year=None, artist=[], tracknumber=""):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	info = {}
	info['Season'] = season
	info['Episode'] = episode
	info['Tracknumber'] = tracknumber
	info['Artist'] = [artist]
	info['Tvshowtitle'] = seriesname
	info['Title'] = name
	info['Plot'] = plot
	info['Duration'] = duration
	info['Year'] = year
	info['Genre'] = 'Unterhaltung, Musik'
	info['Studio'] = 'MTV'
	info['Mpaa'] = None
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

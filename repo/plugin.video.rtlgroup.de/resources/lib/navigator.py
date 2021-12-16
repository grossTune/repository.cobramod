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
import _strptime
from datetime import datetime, timedelta
from collections import OrderedDict
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote, unquote  # Python 2.X
else: 
	from urllib.parse import urlencode, quote, unquote  # Python 3.X

from .common import *
from .config import Registration
from .utilities import Transmission


class Callonce(object):

	def __init__(self):
		self.config = Registration
		self.utilities = Transmission
		self.called = False

	def login_answer(self):
		if self.config().has_credentials() is True:
			USER, PWD = self.config().get_credentials()
		else:
			USER, PWD = self.config().save_credentials()
		if self.utilities().login(USER, PWD) is True:
			debug_MS("(navigator.login_answer) ##### Alles gefunden - Anmeldung Erfolg #####")
			dialog.notification(translation(30528).format('LOGIN'), translation(30529), icon, 8000)
			xbmc.executebuiltin('Container.Refresh')
			return True
		else:
			debug_MS("(navigator.login_answer) ##### NICHTS gefunden - ErrorMeldung #####")
			dialog.notification(translation(30521).format('Login'), translation(30530), icon, 12000)
		return False

	def call_registration(self, lastHM):
		debug_MS("(navigator.call_registration) #################### STARTING THE PROCESSES ####################")
		nowHM = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
		if lastHM != nowHM:
			addon.setSetting('last_starttime', nowHM+' / 02')
		if not self.called:
			addon.setSetting('verified_Account', 'false')
			self.called = True
			if START_MODUS == '0':
				choose = dialog.yesno(addon_id, translation(30502).format(addon_name), nolabel=translation(30503), yeslabel=translation(30504))
				if choose == -1: return False
				if choose:
					debug_MS("(navigator.call_registration) ### START_MODUS = NULL - eins ###")
					addon.setSetting('select_start', '0')
					if self.login_answer() is True:
						addon.setSetting('verified_Account', 'true')
						return True
				else:
					debug_MS("(navigator.call_registration) ### START_MODUS = NULL - zwei ###")
					addon.setSetting('select_start', '0')
					addon.setSetting('verified_Account', 'false')
					addon.setSetting('login_status', '0')
					addon.setSetting('liveFree', 'false')
					addon.setSetting('livePay', 'false')
					addon.setSetting('vodFree', 'false')
					addon.setSetting('vodPay', 'false')
					addon.setSetting('high_definition', 'false')
					addon.setSetting('authtoken', '0')
					return True
			if START_MODUS == '1':
				debug_MS("(navigator.call_registration) ### START_MODUS = EINS ###")
				if self.login_answer() is True:
					addon.setSetting('verified_Account', 'true')
					return True
			if START_MODUS == '2':
				debug_MS("(navigator.call_registration) ### START_MODUS = ZWEI ###")
				addon.setSetting('verified_Account', 'false')
				addon.setSetting('login_status', '0')
				addon.setSetting('liveFree', 'false')
				addon.setSetting('livePay', 'false')
				addon.setSetting('vodFree', 'false')
				addon.setSetting('vodPay', 'false')
				addon.setSetting('high_definition', 'false')
				addon.setSetting('authtoken', '0')
				return True
			return False
		xbmcplugin.endOfDirectory(ADDON_HANDLE)

if KODI_ov18:
	if kodibuild == 18:
		addon.setSetting('Notify_Select', '1')
	elif kodibuild == 19:
		addon.setSetting('Notify_Select', '2')
	elif kodibuild == 20:
		addon.setSetting('Notify_Select', '3')
	elif kodibuild >= 21:
		addon.setSetting('Notify_Select', '4')
else:
	addon.setSetting('Notify_Select', '5')

def makeREQUEST(url, method='GET', REF=None):
	content = cache.cacheFunction(Transmission().retrieveContent, url, method, REF)
	return content

def getUrl(url, method='GET', REF=None):
	content = Transmission().retrieveContent(url, method, REF)
	return content

def mainMenu():
	addDir(translation(30601), artpic+'favourites.png', {'mode': 'listShowsFavs'})
	addDir(translation(30602), icon, {'mode': 'listNewest'})
	addDir(translation(30603), icon, {'mode': 'listDates'})
	addDir(translation(30604), icon, {'mode': 'listStations'})
	addDir(translation(30605), icon, {'mode': 'listAlphabet'})
	addDir(translation(30606), icon, {'mode': 'listTopics'})
	addDir(translation(30607), icon, {'mode': 'listGenres'})
	addDir(translation(30608), icon, {'mode': 'listThemes'})
	addDir(translation(30609), artpic+'basesearch.png', {'mode': 'SearchRTLPLUS'})
	if addon.getSetting('login_status') != "" and int(addon.getSetting('login_status')) > 1:
		if (addon.getSetting('liveFree') == 'true' or addon.getSetting('livePay') == 'true'):
			addDir(translation(30610), artpic+'livestream.png', {'mode': 'listLiveTV'})
	addDir(translation(30611), artpic+'livestream.png', {'mode': 'listEventTV'})
	addDir(translation(30612).format(str(cachePERIOD)), artpic+'remove.png', {'mode': 'clearCache'}, folder=False)
	TEXTBOX = ""
	if addon.getSetting('login_status') == '2': TEXTBOX = translation(30621).format('FREE-USER')
	elif addon.getSetting('login_status') == '3': TEXTBOX = translation(30621).format(addon.getSetting('username'))
	else: TEXTBOX = translation(30622)
	if enableADJUSTMENT:
		addDir(translation(30613)+TEXTBOX, artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if ADDON_operate('inputstream.adaptive'):
			addDir(translation(30614), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	else:
		addDir(TEXTBOX, icon, {'mode': 'blankFUNC'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def unsubscribe():
	if xbmcvfs.exists(sessFile) and Transmission().logout() is True:
		debug_MS("(navigator.unsubscribe) XXXXX USER FORCE REMOVING SESSION - DELETE SESSIONFILE XXXXX")
		dialog.notification(translation(30528).format('Neue SESSION'), translation(30529), icon, 8000)
		return True
	return False

def listSeries(url):
	debug_MS("(navigator.listSeries) -------------------------------------------------- START = listSeries --------------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS("(navigator.listSeries) ### startURL : {0} ###".format(url))
	UNIKAT = set()
	pageNUMBER, position, total = (1 for _ in range(3))
	while (total > 0):
		newURL = '{0}&page={1}'.format(url, str(pageNUMBER))
		debug_MS("(navigator.listSeries) ### newURL : {0} ###".format(newURL))
		content = makeREQUEST(newURL)
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		if DATA.get('movies', '') and DATA.get('movies', {}).get('items', ''):
			elements = DATA['movies']['items']
		elif DATA.get('teaserSetInformations', '') and DATA.get('teaserSetInformations', {}).get('items', ''):
			elements = DATA['teaserSetInformations']['items']
		else: elements = DATA['items']
		for serie in elements:
			debug_MS("(navigator.listSeries) ##### seriesITEM : {0} #####".format(str(serie)))
			station, seoUrl, logo, genre, category, freeEP = ("" for _ in range(6))
			if 'format' in serie and 'teasersets/' in url:
				if serie.get('format', ''):
					serie = serie['format']
				else: continue
			seriesID = (str(serie.get('id', '')) or "")
			if seriesID in UNIKAT:
				continue
			UNIKAT.add(seriesID)
			if serie.get('title', ''):
				name, seriesNAME = cleaning(serie['title']), cleaning(serie['title'])
			else: continue
			station = (serie.get('station', '').upper() or "")
			seoUrl = (serie.get('seoUrl', '') or "")
			if 'format' in serie and not 'teasersets/' in url:
				serie = serie['format']
			logo = (cleanPhoto(serie.get('formatimageMoviecover169', '')) or cleanPhoto(serie.get('formatimageArtwork', '')) or IMG_series.replace('{FID}', seriesID))
			genre = (cleaning(serie.get('genre1', '') or ""))
			category = (serie.get('categoryId', '') or "")
			plot = get_Description(serie, 'Series')
			freeEP = (serie.get('hasFreeEpisodes', '') or "")
			addType = 1
			if xbmcvfs.exists(channelFavsFile):
				with open(channelFavsFile, 'r') as fp:
					watch = json.load(fp)
					for item in watch.get('items', []):
						if item.get('url') == seriesID: addType = 2
			cineType = 'episode'
			if category == 'film':
				cineType = 'movie'
				#addType=3
				name = '[I]'+name+'[/I]' if markMOVIES else name
			debug_MS("(navigator.listSeries) ### TITLE = {0} || IDD = {1} || PHOTO = {2} || addType = {3} ###".format(seriesNAME, seriesID, logo, str(addType)))
			addDir(name, logo, {'mode': 'listSeasons', 'url': seriesID, 'origSERIE': seriesNAME, 'photo': logo, 'extras': extras, 'type': cineType}, plot, genre=genre, studio=station, addType=addType)
			position += 1
		debug_MS("(navigator.listSeries) Anzahl-in-Liste : {0}".format(str(int(position)-1)))
		try:
			debug_MS("(navigator.listSeries) Anzahl-auf-Webseite : {0}".format(str(DATA['total'])))
			total = DATA['total'] - position
		except: total = 0
		pageNUMBER += 1
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSeasons(SERIES_idd, SERIES_img):
	debug_MS("(navigator.listSeasons) -------------------------------------------------- START = listSeasons --------------------------------------------------")
	COMBI_SEASON = []
	url = API_URL+'/formats/'+str(SERIES_idd)+'?fields=[%22id%22,%22title%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22seoText%22,%22tabSeason%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22genres%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22,%22onlineDate%22,%22annualNavigation%22,%22seasonNavigation%22]'
	try:
		content = makeREQUEST(url)
		debug_MS("(navigator.listSeasons) ##### CONTENT : {0} #####".format(str(content)))
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		seriesNAME = cleaning(DATA['title'])
	except: return dialog.notification(translation(30522).format(str(SERIES_idd)), translation(30523), icon, 12000)
	seasonID = str(DATA['id'])
	showSEA = (DATA.get('tabSeason', False) or False)
	seasonIMG = cleanPhoto(SERIES_img)
	if ((prefCONTENT == '0' or showSEA is False) and DATA.get('annualNavigation', '') and DATA.get('annualNavigation', {}).get('total', '') == 1) or ((prefCONTENT == '1' and showSEA is True) and DATA.get('seasonNavigation', '') and DATA.get('seasonNavigation', {}).get('total', '') == 1):
		debug_MS("(navigator.listSeasons) no.1 ### SERIE = {0} || seasonID = {1} || PHOTO = {2} ###".format(seriesNAME, seasonID, str(seasonIMG)))
		listEpisodes(seasonID, 'special')
	else:
		if (prefCONTENT == '0' or showSEA is False) and DATA.get('annualNavigation', '') and DATA.get('annualNavigation', {}).get('items', []):
			for each in DATA.get('annualNavigation', {}).get('items', []):
				PREFIX = 'Jahr '
				number = str(each['year'])
				debug_MS("(navigator.listSeasons) no.2 ### SERIE = {0} || seasonID = {1} || PHOTO = {2} || JAHR = {3} ###".format(seriesNAME, seasonID, str(seasonIMG), number))
				COMBI_SEASON.append([seasonID, PREFIX, number, seasonIMG, seriesNAME])
		elif (prefCONTENT == '1' and showSEA is True) and DATA.get('seasonNavigation', '') and DATA.get('seasonNavigation', {}).get('items', []):
			for each in DATA.get('seasonNavigation', {}).get('items', []):
				PREFIX = 'Staffel '
				number = str(each['season'])
				debug_MS("(navigator.listSeasons) no.3 ### SERIE = {0} || seasonID = {1} || PHOTO = {2} || STAFFEL = {3} ###".format(seriesNAME, seasonID, str(seasonIMG), number))
				COMBI_SEASON.append([seasonID, PREFIX, number, seasonIMG, seriesNAME])
	if COMBI_SEASON:
		COURSE = True if SORTING == '0' else False
		for seasonID, PREFIX, number, seasonIMG, seriesNAME in sorted(COMBI_SEASON, key=lambda n:n[2].zfill(2), reverse=COURSE):
			name = translation(30623) if number == '0' else PREFIX+number
			addDir(name, seasonIMG, {'mode': 'listEpisodes', 'url': seasonID, 'origSERIE': seriesNAME, 'extras': PREFIX+number}, addType=2)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listEpisodes(SEASON_idd, SEASON_plus):
	debug_MS("(navigator.listEpisodes) -------------------------------------------------- START = listEpisodes --------------------------------------------------")
	ACCESS_TOKEN = AUTH_Token if AUTH_Token.startswith('eyJ') else '0'
	COMBI_EPISODE = []
	REAR = False
	if SEASON_plus not in ['standard', 'special']:
		if 'Jahr ' in SEASON_plus:
			startURL = API_URL+'/movies?filter={%22BroadcastStartDate%22:{%22between%22:{%22start%22:%22'+SEASON_plus.split('Jahr ')[1]+'-01-01%2000:00:00%22,%22end%22:%22'+SEASON_plus.split('Jahr ')[1]+'-12-31%2023:59:59%22}},%22FormatId%22:'+SEASON_idd+'}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=500&order=BroadcastStartDate%20asc'
		elif 'Staffel ' in SEASON_plus:
			startURL = API_URL+'/movies?filter={%22Season%22:'+SEASON_plus.split('Staffel ')[1]+',%22FormatId%22:'+SEASON_idd+'}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=500&order=BroadcastStartDate%20asc'
	elif SEASON_plus == 'special':
		startURL = API_URL+'/movies?filter={%22FormatId%22:'+SEASON_idd+'}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=500&order=BroadcastStartDate%20asc'
	else:
		startURL = SEASON_idd
	debug_MS("(navigator.listEpisodes) ### startURL : {0} ###".format(startURL))
	content = makeREQUEST(startURL)
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	if DATA.get('movies', '') and DATA.get('movies', {}).get('items', ''):
		elements = DATA['movies']['items']
	else: 
		elements = DATA['items']
	for vid in elements:
		debug_MS("(navigator.listEpisodes) ##### FOLGE : {0} #####".format(str(vid)))
		episID, tagline, Note_1, Note_2, Note_3, Note_4, Note_5, Note_6, background, station, genre, category = ("" for _ in range(12))
		season, episode, duration, videoURL = ('0' for _ in range(4))
		spezTIMES, normTIMES, begins, mpaa, year = (None for _ in range(5))
		genreLIST = []
		try:
			broadcast = datetime(*(time.strptime(vid['broadcastStartDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
			spezTIMES = broadcast.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':').replace('Mon', translation(32101)).replace('Tue', translation(32102)).replace('Wed', translation(32103)).replace('Thu', translation(32104)).replace('Fri', translation(32105)).replace('Sat', translation(32106)).replace('Sun', translation(32107))
			normTIMES = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			begins = broadcast.strftime('%d{0}%m{0}%Y').format('.')
		except: pass
		protect = (vid.get('isDrm', False) or False)
		episID = (str(vid.get('id', '')) or "")
		title = cleaning(vid['title'])
		try: seriesname = cleaning(vid['format']['title'])
		except: 
			try: seriesname = cleaning(vid['format']['seoUrl']).replace('-', ' ').title()
			except: continue
		season = (str(vid.get('season', '0')) or '0')
		episode = (str(vid.get('episode', '0')) or '0')
		if vid.get('duration', ''):
			duration = get_Time(vid['duration'])
		tagline = (cleaning(vid.get('teaserText', '') or ""))
		description = get_Description(vid)
		if seriesname !="": Note_1 = seriesname
		if season != '0' and episode != '0': Note_3 = translation(30624).format(season, episode)
		if spezTIMES: Note_4 = translation(30625).format(str(spezTIMES))
		if showDATE and normTIMES:
			Note_5 = translation(30626).format(str(normTIMES))
		if str(vid.get('fsk')).isdigit():
			mpaa = translation(30627).format(str(vid['fsk'])) if str(vid.get('fsk')) != '0' else translation(30628)
		if str(vid.get('productionYear'))[:4].isdigit() and str(vid.get('productionYear'))[:4] not in ['0', '1970']:
			year = str(vid['productionYear'])[:4]
		PayType = (vid.get('payed', True) or vid.get('free', True))
		if vid.get('manifest', ''):
			if STATUS == 3:
				if vid.get('manifest', {}).get('dash', '') and vodPremium is True: # Normal-Play with Pay-Account
					videoURL = vid['manifest']['dash'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net')
				if vid.get('manifest', {}).get('dashhd', '') and vodPremium is True and selectionHD: # HD-Play with Pay-Account
					videoURL = vid['manifest']['dashhd'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net').split('.mpd')[0]+'.mpd'
			elif STATUS < 3 and vid.get('manifest', {}).get('dash', ''):
				if PayType is True: # Normal-Play without Pay-Account
					videoURL = vid['manifest']['dash'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net')
		try: deeplink = 'https://www.tvnow.de/'+vid['format']['formatType'].replace('show', 'shows').replace('serie', 'serien').replace('film', 'filme')+'/'+cleaning(vid['format']['seoUrl'])+'-'+str(vid['format']['id'])
		except: deeplink =""
		# BILD_1 = https://aistvnow-a.akamaihd.net/tvnow/movie/1454577/960x0/image.jpg
		# BILD_2 = https://ais.tvnow.de/tvnow/movie/1454577/960x0/image.jpg
		image = IMG_movies.replace('{MID}', episID)
		if vodPremium is False and PayType is False and STATUS < 3: episID = '0'
		if vid.get('format', ''):
			background = (cleanPhoto(vid.get('format', {}).get('formatImageClear', '')) or cleanPhoto(vid.get('format', {}).get('formatimageArtwork', '')) or cleanPhoto(vid.get('format', {}).get('defaultImage169Logo', '')) or "")
			station = (vid.get('format', {}).get('station', '').upper() or "")
			if vid.get('format', {}).get('genres', ''):
				genreLIST = [cleaning(item) for item in vid.get('format', {}).get('genres', '')]
				if genreLIST: genre = ' / '.join(sorted(genreLIST))
			if genre =="" and vid.get('format', {}).get('genre1', ''):
				genre = cleaning(vid['format']['genre1'])
			category = (vid.get('format', {}).get('categoryId', '') or "")
		cineType = 'movie' if category == 'film' else 'episode'
		if (not KODI_ov18 and protect is True and PayType is False):
			Note_2 = '   [COLOR skyblue](premium|[/COLOR][COLOR orangered]DRM)[/COLOR]'
			Note_6 = '     [COLOR deepskyblue](premium|[/COLOR][COLOR orangered]DRM)[/COLOR]'
		elif (not KODI_ov18 and protect is True and PayType is True):
			Note_2 = '   [COLOR orangered](DRM)[/COLOR]'
			Note_6 = '     [COLOR orangered](DRM)[/COLOR]'
		elif (KODI_17 or KODI_ov18) and PayType is False and STATUS < 3:
			Note_2 = '   [COLOR skyblue](premium)[/COLOR]'
			Note_6 = '     [COLOR deepskyblue](premium)[/COLOR]'
		plot = Note_1+Note_2+'[CR]'+Note_3+Note_4+'[CR][CR]'+description
		title1 = title
		title2 = title+Note_5+Note_6
		COMBI_EPISODE.append([episID, videoURL, background, image, title1, title2, plot, tagline, duration, seriesname, season, episode, genre, mpaa, year, begins, station, cineType, deeplink, protect, ACCESS_TOKEN, PayType])
	if COMBI_EPISODE:
		SEND = {}
		SEND['videos'] = []
		for episID, videoURL, background, image, title1, title2, plot, tagline, duration, seriesname, season, episode, genre, mpaa, year, begins, station, cineType, deeplink, protect, ACCESS_TOKEN, PayType in COMBI_EPISODE:
			for method in getSorting():
				xbmcplugin.addSortMethod(ADDON_HANDLE, method)
			listitem = xbmcgui.ListItem(title2, path=HOST_AND_PATH+'?IDENTiTY='+episID+'&mode=playCODE')
			info = {}
			info['Season'] = season
			if episode != '0':
				info['Episode'] = episode
			info['Tvshowtitle'] = seriesname
			info['Title'] = title2
			info['Tagline'] = tagline
			info['Plot'] = plot
			info['Duration'] = duration
			if begins is not None:
				info['Date'] = begins
			info['Year'] = year
			info['Genre'] = genre
			info['Director'] = None
			info['Writer'] = None
			info['Studio'] = station
			info['Mpaa'] = mpaa
			info['Mediatype'] = cineType
			listitem.setInfo(type='Video', infoLabels=info)
			listitem.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
			if useSerieAsFanart and background != "":
				listitem.setArt({'fanart': background})
				REAR = True
			if not REAR and image and image != icon and not artpic in image:
				listitem.setArt({'fanart': image})
			listitem.addStreamInfo('Video', {'Duration':duration})
			listitem.setProperty('IsPlayable', 'true')
			listitem.setContentLookup(False)
			listitem.addContextMenuItems([(translation(30654), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)')])
			xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=HOST_AND_PATH+'?IDENTiTY='+episID+'&mode=playCODE', listitem=listitem)
			SEND['videos'].append({'url': videoURL, 'tvshow': seriesname, 'filter': episID, 'name': title2, 'pict': image, 'season': season, 'episode': episode, 'deep': deeplink, 'protected': protect, 'token': ACCESS_TOKEN, 'payed': PayType})
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listNewest():
	debug_MS("(navigator.listNewest) ------------------------------------------------ START = listNewest -----------------------------------------------")
	BEFORE = (datetime.now() - timedelta(days=2)).strftime('%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))
	NOW = datetime.now().strftime('%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))
	newURL = API_URL+'/movies?filter={%22BroadcastStartDate%22:{%22between%22:{%22start%22:%22'+BEFORE.replace('T', '%20')+'%22,%22end%22:%22'+NOW.replace('T', '%20')+'%22}}}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=500&order=BroadcastStartDate%20desc'
	listEpisodes(newURL, 'standard')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listDates():
	debug_MS("(navigator.listDates) ------------------------------------------------ START = listDates -----------------------------------------------")
	i = -7
	while i <= 7:
		WU = (datetime.now() - timedelta(days=i)).strftime('%Y{0}%m{0}%d'.format('-'))
		WT = (datetime.now() - timedelta(days=i)).strftime('%a{0}%d{1} %b'.format('~', '.'))
		MD = WT.split('~')[0].replace('Mon', translation(32101)).replace('Tue', translation(32102)).replace('Wed', translation(32103)).replace('Thu', translation(32104)).replace('Fri', translation(32105)).replace('Sat', translation(32106)).replace('Sun', translation(32107))
		MM = WT.split('~')[1].replace('Mar', translation(32201)).replace('May', translation(32202)).replace('Oct', translation(32203)).replace('Dec', translation(32204))
		newURL = API_URL+'/movies?filter={%22BroadcastStartDate%22:{%22between%22:{%22start%22:%22'+WU+'%2000:00:01%22,%22end%22:%22'+WU+'%2023:59:59%22}}}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=300&order=BroadcastStartDate%20asc'
		if i == 0: addDir("[COLOR lime]"+MM+" | "+MD+"[/COLOR]", icon, {'mode': 'listEpisodes', 'url': newURL})
		else: addDir(MM+" | "+MD, icon, {'mode': 'listEpisodes', 'url': newURL})
		i += 1
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listStations():
	debug_MS("(navigator.listStations) -------------------------------------------------- START = listStations --------------------------------------------------")
	COMBI_CHANNEL = []
	MORE_TV = [{'stationID': 'tvnow', 'name': 'TVNOW'}, {'stationID': 'tvnowkids', 'name': 'TVNOW Kids'}, {'stationID': 'watchbox', 'name': 'WATCHBOX'}]
	content = makeREQUEST('https://bff.apigw.tvnow.de/teaserrow/stations') # NEU: https://bff.apigw.tvnow.de/livestream/soccer
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for chan in DATA['items']:
		COMBI_CHANNEL.append({'stationID': str(chan['ecommerce']['teaserName']), 'name': cleaning(chan['label'])})
	COMBI_CHANNEL.extend(MORE_TV)
	for elem in COMBI_CHANNEL:
		newURL = API_URL+'/formats?filter={%22Disabled%22:%220%22,%22Station%22:%22'+elem['stationID']+'%22}&fields=[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22seoText%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22]&maxPerPage=500&order=NameLong%20asc'
		addDir(elem['name'], stapic+elem['stationID']+'.png', {'mode': 'listSeries', 'url': newURL})
		debug_MS("(navigator.listStations) ### stationNAME = {0} || stationID = {1} || LOGO = {2} ###".format(elem['name'], elem['stationID'], str(stapic+elem['stationID']+'.png')))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet():
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	for letter in (('0-9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')):
		newURL = API_URL+'/formats?filter={%22Disabled%22:%220%22,%22TitleGroup%22:%22'+letter+'%22}&fields=[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22seoText%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22]&maxPerPage=500&order=NameLong%20asc'
		addDir(letter, alppic+letter+'.jpg', {'mode': 'listSeries', 'url': newURL})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listTopics():
	debug_MS("(navigator.listTopics) -------------------------------------------------- START = listTopics --------------------------------------------------")
	UN_Supported = ['12924', '11649', '12616', '13183', '13757', '11652', '11650', '13793', '12775', '13084', '11994', '13175', '11759', '13044', '11734', '13411'] # these lists are empty or not compatible
	content = makeREQUEST(API_URL+'/pages/nowtv/home-v1?fields=teaserSets.headline,teaserSets.id')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for top in DATA['teaserSets']['items']:
		topicID = str(top['id'])
		name = cleaning(top['headline'])
		debug_MS("(navigator.listTopics) ### IDD = {0} || NAME = {1} ###".format(topicID, name))
		if not any(x in topicID for x in UN_Supported):
			newURL = API_URL+'/teasersets/'+topicID+'?fields=[%22teaserSetInformations%22,[%22format%22,[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22seoText%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22]]]&maxPerPage=100&order=NameLong%20asc'
			addDir(name, icon, {'mode': 'listSeries', 'url': newURL})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listGenres():
	debug_MS("(navigator.listGenres) -------------------------------------------------- START = listGenres --------------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	content = makeREQUEST(API_URL+'/genres?maxPerPage=100')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for genre in DATA['items']:
		name = cleaning(genre['name'])
		seoUrl = genre['seoUrl']
		plot = cleaning(genre['description'])
		newURL = API_URL+'/formats/genre/'+seoUrl.replace('-','%20')+'?filter={%22station%22:%22none%22}&fields=[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22seoText%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22]&maxPerPage=500&order=NameLong%20asc'
		debug_MS("(navigator.listGenres) ### genreITEM = {0} || newURL = {1} ###".format(name, str(newURL)))
		logo = genpic+name+'.png' if xbmcvfs.exists(genpic+name+'.png') else icon
		if not 'magazine' in seoUrl:
			addDir(name, logo, {'mode': 'listSeries', 'url': newURL}, plot, tagline=plot)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listThemes():
	debug_MS("(navigator.listThemes) -------------------------------------------------- START = listThemes --------------------------------------------------")
	# https://api.tvnow.de/v3/channels/station/rtl?fields=*&filter=%7B%22Active%22:true%7D&maxPerPage=500&page=1
	content = makeREQUEST(API_URL+'/channels/station/rtl?fields=*&filter={%22Active%22:true}&maxPerPage=100')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for theme in DATA['items']:
		themeID = str(theme['id'])
		name = cleaning(theme['title'])
		logo = 'https://aistvnow-a.akamaihd.net/tvnow/cms/'+theme['portraitImage']+'/image.jpg'
		newURL = API_URL+'/channels/'+themeID+'/movies?filter={%22station%22:%22none%22}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=100'
		debug_MS("(navigator.listThemes) ### IDD = {0} || NAME = {1} || PHOTO = {2} ###".format(themeID, name, logo))
		addDir(name, logo, {'mode': 'listEpisodes', 'url': newURL})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def SearchRTLPLUS():
	debug_MS("(navigator.SearchRTLPLUS) ------------------------------------------------ START = SearchRTLPLUS -----------------------------------------------")
	keyword = None
	if xbmcvfs.exists(searchHackFile):
		with open(searchHackFile, 'r') as look:
			keyword = look.read()
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(heading=translation(30629), type=xbmcgui.INPUT_ALPHANUM, autoclose=10000)
		if keyword:
			keyword = quote(keyword)
			with open(searchHackFile, 'w') as record:
				record.write(keyword)
	if keyword: return listSearch(keyword)
	return None

def listSearch(TERM):
	debug_MS("(navigator.listSearch) -------------------------------------------------- START = Searching --------------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	url = API_URL+'/formats?fields=[%22id%22,%22title%22,%22titleGroup%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22categoryId%22,%22searchAliasName%22,%22metaTags%22,%22infoText%22,%22infoTextLong%22]&maxPerPage=500'
	pageNUMBER, position, total = (1 for _ in range(3))
	QUERY = unquote(TERM)
	FOUND = False
	while (total > 0):
		newURL = '{0}&page={1}'.format(url, str(pageNUMBER))
		debug_MS("(navigator.listSearch) ### newURL : {0} ###".format(newURL))
		content = makeREQUEST(newURL)
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		for search in DATA['items']:
			station, seoUrl, logo, genre, category, freeEP = ("" for _ in range(6))
			COMBIstring = cleaning(search['metaTags'].lower().replace('video,', '').replace('videos,', '').replace('online sehen,', '').replace('internet tv,', '').replace('fernsehen,', '').replace('video on demand,', '').replace('tv now,', '').replace('TVNOW,', ''))
			COMBIstring += cleaning(search['searchAliasName'].lower().replace(';', ','))
			COMBIstring += cleaning(search['title'].lower())
			seriesID = str(search['id'])
			name, seriesNAME = cleaning(search['title']), cleaning(search['title'])
			station = (search.get('station', '').upper() or "")
			seoUrl = (search.get('seoUrl', '') or "")
			logo = (cleanPhoto(search.get('formatimageMoviecover169', '')) or cleanPhoto(search.get('formatimageArtwork', '')) or IMG_series.replace('{FID}', seriesID))
			genre = (cleaning(search.get('genre1', '') or ""))
			category = (search.get('categoryId', '') or "")
			plot = get_Description(search, 'Search')
			freeEP = (search.get('hasFreeEpisodes', '') or "")
			addType = 1
			if xbmcvfs.exists(channelFavsFile):
				with open(channelFavsFile, 'r') as fp:
					watch = json.load(fp)
					for item in watch.get('items', []):
						if item.get('url') == seriesID: addType = 2
			cineType = 'episode'
			if category == 'film':
				cineType = 'movie'
				#addType = 3
				name = '[I]'+name+'[/I]' if markMOVIES else name
			if QUERY.lower() in str(COMBIstring):
				FOUND = True
				debug_MS("(navigator.listSearch) ### Found in SEARCH = TITLE : {0} ###".format(seriesNAME))
				debug_MS("(navigator.listSearch) ### Found in SEARCH = STRING : {0} ###".format(str(COMBIstring)))
				addDir(name, logo, {'mode': 'listSeasons', 'url': seriesID, 'origSERIE': seriesNAME, 'photo': logo, 'extras': extras, 'type': cineType}, plot, genre=genre, studio=station, addType=addType)
			position += 1
		debug_MS("(navigator.listSearch) Anzahl-in-Liste : {0}".format(str(int(position)-1)))
		try:
			debug_MS("(navigator.listSearch) Anzahl-auf-Webseite : {0}".format(str(DATA['total'])))
			total = DATA['total'] - position
		except: total = 0
		pageNUMBER += 1
	if not FOUND:
		return dialog.notification(translation(30524).format('Ergebnisse'), translation(30526), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listLiveTV():
	debug_MS("(navigator.listLiveTV) -------------------------------------------------- START = listLiveTV --------------------------------------------------")
	if liveGratis is False and livePremium is False:
		failing("(navigator.listLiveTV) ##### Sie haben KEINE Berechtigung : Für LIVE-TV ist ein Premium-Account Voraussetzung !!! #####")
		return dialog.notification(translation(30531), translation(30532), icon, 8000)
	content = getUrl(API_URL+'/epgs/movies/nownext?fields=nowNextEpgMovies.*')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for channel in DATA['items']:
		debug_MS("(navigator.listLiveTV) ##### channelITEM : {0} #####".format(str(channel)))
		title, subTitle, title_2, subTitle_2, plot = ("" for _ in range(5))
		START, START_2, END, END_2 = (None for _ in range(4))
		SHORT = channel['nowNextEpgMovies']['items'][0]
		station = cleaning(SHORT['station']).upper().replace('RTLPLUS', 'RTLUP')
		deeplink = 'https://www.tvnow.de/live-tv/'+station.lower()
		liveID = str(SHORT['id'])
		title = (cleaning(SHORT.get('title', '')) or "")
		subTitle = (cleaning(SHORT.get('subTitle', '')) or "")
		if title == "" and subTitle != "":
			title = subTitle
		elif title != "" and subTitle != "":
			title = '{0} - {1}'.format(title, subTitle)
		if str(SHORT.get('startDate'))[:4].isdigit():
			startDT = datetime(*(time.strptime(SHORT['startDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
			START = startDT.strftime('{0}%H{1}%M').format('(', ':')
		if str(SHORT.get('endDate'))[:4].isdigit():
			endDT = datetime(*(time.strptime(SHORT['endDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
			END = endDT.strftime(' {0} %H{1}%M{2}').format('-', ':', ')')
		normSD, highHD = SHORT['manifest']['dash'], SHORT['manifest']['dashhd']
		photo = IMG_tvepg.replace('{EID}', liveID)
		if END: plot = translation(30630).format(END.replace('-', '').replace(')', '').strip())
		if channel.get('nowNextEpgMovies', {}).get('total', '') == 2:
			BRIEF = channel['nowNextEpgMovies']['items'][1]
			title_2 = (cleaning(BRIEF.get('title', '')) or "")
			subTitle_2 = (cleaning(BRIEF.get('subTitle', '')) or "")
			if title_2 == "" and subTitle_2 != "":
				title_2 = subTitle_2
			elif title_2 != "" and subTitle_2 != "":
				title_2 = '{0} - {1}'.format(title_2, subTitle_2)
			if str(BRIEF.get('startDate'))[:4].isdigit():
				startDT_2 = datetime(*(time.strptime(BRIEF['startDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
				START_2 = startDT_2.strftime('%H{0}%M').format(':')
			if str(BRIEF.get('endDate'))[:4].isdigit():
				endDT_2 = datetime(*(time.strptime(BRIEF['endDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
				END_2 = endDT_2.strftime('%H{0}%M').format(':')
			if START_2 and END_2:
				plot += translation(30631).format(title_2, START_2, END_2)
		name = translation(30632).format(station, title)
		special = translation(30632).format(station, title)
		if START and END:
			name = translation(30633).format(station, title, START+END)
		vidURL = highHD if selectionHD and livePremium is True else normSD
		listitem = xbmcgui.ListItem(name, path=vidURL)
		listitem.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Studio': station})
		listitem.setArt({'icon': icon, 'thumb': photo, 'poster': photo, 'fanart': photo})
		xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url='{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playDash', 'action': 'LIVE', 'xhighHD': vidURL, 'xlink': deeplink, 'xdrm': True})), listitem=listitem)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)

def listEventTV():
	debug_MS("(navigator.listEventTV) -------------------------------------------------- START = listEventTV --------------------------------------------------")
	COMBI_SPECIAL = []
	content_1 = getUrl('https://bff.apigw.tvnow.de/livestream/soccer')
	DATA = json.loads(content_1, object_pairs_hook=OrderedDict)
	for channel in DATA['events']:
		debug_MS("(navigator.eventTV) ##### channelITEM : {0} #####".format(str(channel)))
		Note_1, Note_2, Note_3, station, deeplink, vidURL, Note_4, plot = ("" for _ in range(8))
		START, END, mpaa = (None for _ in range(3))
		eventID = str(channel['id'])
		name = (cleaning(channel.get('headline', '')) or "")
		if channel.get('isPremium', '') is True and livePremium is False: continue
		if str(channel.get('startsAt')).isdigit():
			LOCALstart = get_Local_DT(datetime(1970, 1, 1) + timedelta(milliseconds=channel.get('startsAt', ''))) # 1631805300000
			START = LOCALstart.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
		if str(channel.get('endsAt')).isdigit():
			LOCALend = get_Local_DT(datetime(1970, 1, 1) + timedelta(milliseconds=channel.get('endsAt', ''))) # 1631819700000
			END = LOCALend.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
		Note_1 = (cleaning(channel.get('title', ''))+'[CR]' or "")
		if START and END: Note_2 = translation(30634).format(str(START), str(END))
		elif START and END is None: Note_1 = translation(30635).format(str(START))
		content_2 = getUrl('https://bff.apigw.tvnow.de/player/live/'+eventID+'?version=v6')
		debug_MS("(navigator.eventTV) ##### streamITEM : {0} #####".format(str(content_2)))
		STREAM = json.loads(content_2, object_pairs_hook=OrderedDict)
		if STREAM.get('videoConfig', '') and STREAM.get('videoConfig', {}).get('meta', ''):
			SHORT = STREAM['videoConfig']['meta']
			if SHORT.get('title', ''):
				name = cleaning(SHORT['title'])
			if SHORT.get('description', ''):
				Note_3 = cleaning(SHORT['description'])+'[CR]'
			if str(SHORT.get('fsk', '')).isdigit():
				mpaa = translation(30627).format(str(SHORT['fsk'])) if str(SHORT.get('fsk', '')) != '0' else translation(30628)
			if SHORT.get('station', ''):
				station = cleaning(SHORT['station']).upper()
				deeplink = 'https://www.tvnow.de/events/'+station.lower()
			vidURL = (STREAM.get('videoConfig', []).get('sources', {}).get('dashFallbackUrl', '') or STREAM.get('videoConfig', []).get('sources', {}).get('dashUrl', ''))
		photo = icon
		if channel.get('image', '') and channel.get('image', {}).get('path', ''):
			photo = cleanPhoto(channel['image']['path'])
		Note_4 = (cleaning(channel.get('additionalInfo', '')) or "")
		plot = Note_1+Note_2+Note_3+Note_4
		COMBI_SPECIAL.append([vidURL, eventID, deeplink, name, photo, plot, station, mpaa])
	if COMBI_SPECIAL:
		for vidURL, eventID, deeplink, name, photo, plot, station, mpaa in COMBI_SPECIAL:
			listitem = xbmcgui.ListItem(name, path=vidURL)
			listitem.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Studio': station, 'Mpaa': mpaa})
			listitem.setArt({'icon': icon, 'thumb': photo, 'poster': photo, 'fanart': photo})
			xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url='{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playDash', 'action': 'EVENT', 'xhighHD': vidURL, 'xcode': eventID, 'xlink': deeplink, 'xdrm': True})), listitem=listitem)
	else:
		if STATUS == 3:
			debug_MS("(navigator.listEventTV) Leider gibt es in der Rubrik : EVENTSTREAMS - zurzeit überhaupt KEINE verfügbaren Videos !")
			return dialog.notification(translation(30524).format('Einträge'), translation(30527).format('EVENTSTREAMS'), icon, 8000)
		else:
			debug_MS("(navigator.listEventTV) Leider gibt es in der Rubrik : EVENTSTREAMS - zurzeit KEINE 'Gratis Videos' !")
			return dialog.notification(translation(30524).format("'Gratis Videos'"), translation(30527).format('EVENTSTREAMS'), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE, cacheToDisc=False)

def playDash(*args):
	debug_MS("(navigator.playDash) -------------------------------------------------- START = playDash --------------------------------------------------")
	ACCESS_TOKEN = AUTH_Token if AUTH_Token.startswith('eyJ') else '0'
	UAG = 'User-Agent={0}&Referer={1}'.format(get_userAgent(), xlink) if xlink else 'User-Agent={0}'.format(get_userAgent())
	streamURL = False
	FOUND = 0
	if xbmc.Player().isPlaying():
		xbmc.Player().stop()
	if action == 'LIVE' and xhighHD:
		FOUND, streamURL = 1, xhighHD
	elif action == 'EVENT' and xhighHD and xcode:
		FOUND, streamURL = 1, xhighHD
	elif action == 'IPTV' and xhighHD:
		if liveGratis is False and livePremium is False:
			failing("(navigator.playDash) ##### Sie haben KEINE Berechtigung : Für LIVE-TV ist ein Premium-Account Voraussetzung !!! #####")
			return dialog.notification(translation(30531), translation(30532), icon, 8000)
		else:
			FOUND, streamURL = 1, xhighHD
	elif action == 'DEFAULT' and xnormSD and xhighHD and xcode and xdrm and xstat:
		if (vodPremium is True and STATUS == 3 and selectionHD and ACCESS_TOKEN != '0'):
			FOUND, streamURL = 1, xhighHD
		elif (vodPremium is True and STATUS == 3 and not selectionHD and ACCESS_TOKEN != '0') or (vodPremium is False and xstat == 'True'):
			FOUND, streamURL = 1, xnormSD
		else:
			failing("(navigator.playDash) ##### Sie haben KEINE Berechtigung : Für dieses Video ist ein Premium-Account Voraussetzung !!! #####")
			return dialog.ok(addon_id, translation(30506))
	debug_MS("(navigator.playDash) ### ACTION : {0} || xnormSD : {1} || xhighHD : {2} ###".format(str(action), str(xnormSD), str(xhighHD)))
	debug_MS("(navigator.playDash) ### XCODE : {0} || XLINK : {1} || XDRM : {2} || XSTAT : {3} ###".format(str(xcode), str(xlink), str(xdrm), str(xstat)))
	debug_MS("(navigator.playDash) ### streamURL : {0} || FOUND : {1} || selectionHD : {2} ###".format(str(streamURL), str(FOUND), str(selectionHD)))
	if FOUND == 1 and streamURL:
		debug_MS("--------------------------------------------------------------------------- Gefunden ---------------------------------------------------------------------------------")
		liz = xbmcgui.ListItem(path=streamURL+'|'+UAG)
		log("(navigator.playDash) StreamURL : {0}|{1}".format(streamURL, UAG))
		liz.setMimeType('application/dash+xml')
		liz.setProperty(INPUT_APP, 'inputstream.adaptive')
		liz.setProperty('inputstream.adaptive.manifest_type', 'mpd')
		liz.setProperty('inputstream.adaptive.stream_headers', 'User-Agent={0}'.format(get_userAgent()))
		if KODI_ov18 and xdrm == 'True':
			if ACCESS_TOKEN == '0':
				specification = 'eventURL' if action == 'EVENT' else 'standardURL'
				ACCESS_TOKEN = Transmission().get_FreeToken(xcode, specification)
			debug_MS("(navigator.playDash) ### TOKEN : {0} ###".format(str(ACCESS_TOKEN)))
			if ACCESS_TOKEN != '0':
				new_LICENSE = LICENSE_URL.replace('/proxy', '/license') if action in ['LIVE', 'EVENT', 'IPTV'] else LICENSE_URL
				liz.setProperty('inputstream.adaptive.license_key', new_LICENSE.format(UAG, ACCESS_TOKEN, 'R{SSM}'))
				debug_MS("(navigator.playDash) LICENSE : {0}".format(new_LICENSE.format(UAG, ACCESS_TOKEN, 'R{SSM}')))
				liz.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
				if action in ['LIVE', 'EVENT', 'IPTV']:
					liz.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
					station = xlink.split('/')[-1].upper()
					liz.setInfo(type='Video', infoLabels={'Title': 'Livestream - '+station, 'Studio': station})
					if action in ['LIVE', 'EVENT']:
						xbmc.Player().play(item=streamURL, listitem=liz)
					elif action == 'IPTV':
						xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, liz)
					xbmc.sleep(3000)
					if not xbmc.getCondVisibility('Window.IsVisible(fullscreenvideo)') and not xbmc.Player().isPlaying():
						return dialog.notification(translation(30531), translation(30533), icon, 8000)
		if action == 'DEFAULT':
			xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, liz)
	else:
		failing("(navigator.playDash) ##### Der übertragene *Dash-Abspiel-Link* ist leider FEHLERHAFT !!! #####")
		return dialog.notification(translation(30521).format('DASH - URL'), translation(30534), icon, 8000)

def playCODE(IDD):
	debug_MS("(navigator.playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	finalURL = '0'
	with open(WORKFILE, 'r') as wok:
		ARRIVE = json.load(wok)
		for elem in ARRIVE['videos']:
			if elem['filter'] == IDD:
				finalURL = elem['url']
				seriesname = py2_enc(elem['tvshow'])
				name = py2_enc(elem['name'])
				image = cleanPhoto(elem['pict'])
				season = elem['season']
				episode = elem['episode']
				deeplink = py2_enc(elem['deep'])
				protected = elem['protected']
				security = elem['token']
				payed = elem['payed']
	if IDD != '0' and finalURL != '0':
		debug_MS("--------------------------------------------------------------------------- Gefunden ---------------------------------------------------------------------------------")
		debug_MS("(navigator.playCODE) ### STREAM : {0} || DRM : {1} || PAYED : {2} ###".format(str(finalURL), str(protected), str(payed)))
		UAG = 'User-Agent={0}&Referer={1}'.format(get_userAgent(), deeplink) if deeplink != "" else 'User-Agent={0}'.format(get_userAgent())
		liz = xbmcgui.ListItem(path=finalURL+'|'+UAG)
		log("(navigator.playCODE) StreamURL : {0}|{1}".format(finalURL, UAG))
		liz.setMimeType('application/dash+xml')
		liz.setProperty(INPUT_APP, 'inputstream.adaptive')
		liz.setProperty('inputstream.adaptive.manifest_type', 'mpd')
		liz.setProperty('inputstream.adaptive.stream_headers', 'User-Agent={0}'.format(get_userAgent()))
		if KODI_ov18 and protected is True:
			if security == '0':
				security = Transmission().get_FreeToken(IDD, extras)
			debug_MS("(navigator.playCODE) ### TOKEN : {0} ###".format(str(security)))
			if security != '0':
				liz.setProperty('inputstream.adaptive.license_key', LICENSE_URL.format(UAG, security, 'R{SSM}'))
				debug_MS("(navigator.playCODE) LICENSE : {0}".format(LICENSE_URL.format(UAG, security, 'R{SSM}')))
				liz.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, liz)
	else:
		if payed is False and security == '0':
			failing("(navigator.playCODE) ##### Sie haben KEINE Berechtigung : Für dieses Video ist ein Premium-Account Voraussetzung !!! #####")
			return dialog.notification(translation(30531), translation(30533), icon, 8000)
		else:
			failing("(navigator.playCODE) ##### Die angeforderte Video-Url wurde leider NICHT gefunden !!! #####")
			return dialog.notification(translation(30521).format('VIDEO'), translation(30535), icon, 8000)

def listShowsFavs():
	debug_MS("(navigator.listShowsFavs) ------------------------------------------------ START = listShowsFavs -----------------------------------------------")
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as fp:
			watch = json.load(fp)
			for item in watch.get('items', []):
				title = '[I]'+cleaning(item.get('name'))+'[/I]' if markMOVIES and item.get('type') == 'movie' else cleaning(item.get('name'))
				logo = icon if item.get('pict', 'None') == 'None' else cleanPhoto(item.get('pict'))
				desc = None if item.get('plot', 'None') == 'None' else cleaning(item.get('plot'))
				debug_MS("(navigator.listShowsFavs) ### NAME : {0} || URL : {1} || IMAGE : {2} || cineType : {3} ###".format(title, item.get('url'), logo, item.get('type')))
				addDir(title, logo, {'mode': 'listSeasons', 'url': item.get('url'), 'origSERIE': cleaning(item.get('name')), 'photo': logo, 'type': item.get('type')}, desc, FAVclear=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def favs(*args):
	TOPS = {}
	TOPS['items'] = []
	if xbmcvfs.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as output:
			TOPS = json.load(output)
	if action == 'ADD':
		TOPS['items'].append({'name': name, 'pict': pict, 'url': url, 'plot': plot, 'type': type})
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.sleep(500)
		dialog.notification(translation(30536), translation(30537).format(name), icon, 8000)
	elif action == 'DEL':
		TOPS['items'] = [obj for obj in TOPS['items'] if obj.get('url') != url]
		with open(channelFavsFile, 'w') as input:
			json.dump(TOPS, input, indent=4, sort_keys=True)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		dialog.notification(translation(30536), translation(30538).format(name), icon, 8000)

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, tagline=None, genre=None, mpaa=None, year=None, studio=None, addType=0, FAVclear=False, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Tvshowtitle': params.get('origSERIE'), 'Title': name, 'Plot': plot, 'Tagline': tagline, 'Genre': genre, 'Mpaa': mpaa, 'Year': year, 'Studio': studio, 'Mediatype': 'video'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	entries = []
	if addType == 1 and FAVclear is False:
		entries.append([translation(30651), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'ADD', 'name': params.get('origSERIE'), 'pict': 'None' if image == icon else image, 'url': params.get('url'),
			'plot': 'None' if plot is None else plot.replace('\n', '[CR]'), 'type': params.get('type')}))])
	if addType in [1, 2] and enableLIBRARY:
		entries.append([translation(30653), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'preparefiles', 'url': params.get('url'), 'name': params.get('origSERIE'), 'extras': params.get('extras'), 'cycle': libraryPERIOD}))])
	if FAVclear is True:
		entries.append([translation(30652), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'DEL', 'name': name, 'pict': image, 'url': params.get('url'), 'plot': plot, 'type': params.get('type')}))])
	liz.addContextMenuItems(entries, replaceItems=False)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

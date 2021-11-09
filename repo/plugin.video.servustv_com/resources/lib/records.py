# -*- coding: utf-8 -*-

import sys
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs

from .common import *


def get_ListItem(info, category, phrase, extras, aback, addType=1, folder=True, STOCK=False):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	cineType, tvshow, tagline, description, Note_1, origSERIE = ("" for _ in range(6))
	duration, season, episode = ('0' for _ in range(3))
	title_long, DIGS, uv, startTIMES, endTIMES, genre = (None for _ in range(6))
	### Codeübersetzungen = e2fda2e1-58ff-4474-a49a-a2df01309998 = Neues aus Österreich / 9878c650-06dc-403e-9389-3ad738eca2ae = Talks & Meinungen / e440011b-c6f6-447f-97e3-3f7d2853689d = Ab in die Natur ###
	acronym = ['discover-featured', 'episode-topic', 'latest-videos', 'e2fda2e1-58ff-4474-a49a-a2df01309998', '9878c650-06dc-403e-9389-3ad738eca2ae', 'e440011b-c6f6-447f-97e3-3f7d2853689d']
	title_short = py2_enc(info.get('title')) if info.get('title', '') else py2_enc(info.get('label'))
	liz = xbmcgui.ListItem()
	entries = []
	ilabels = {}
	eid = info.get('id', '')
	if info.get('content_type', ''):
		cineType = py2_enc(info.get('content_type')).replace('show', 'tvshow').replace('clip', 'tvshow').replace('film', 'movie')
	elif aback.get('content_type', ''):
		cineType = py2_enc(aback.get('content_type')).replace('show', 'tvshow').replace('clip', 'tvshow').replace('film', 'movie')
	if info.get('subheading', ''):
		if cineType in ['episode', 'tvshow']: tvshow = py2_enc(info.get('subheading'))
		elif cineType == 'movie': tagline = py2_enc(info.get('subheading'))
	cineType = cineType if cineType in ['episode', 'movie', 'tvshow', 'video'] else 'movie'
	if 'long_description' in info or 'long_description' in aback:
		if 'long_description' in info and info['long_description'] and len(info['long_description']) > 10:
			DIGS = py2_enc(info.get('long_description'))
		if DIGS is None and 'long_description' in aback and aback['long_description'] and len(aback['long_description']) > 10:
			DIGS = py2_enc(aback.get('long_description'))
	if DIGS is None and 'short_description' in info or 'short_description' in aback:
		if 'short_description' in info and info['short_description'] and len(info['short_description']) > 10:
			DIGS = py2_enc(info.get('short_description'))
		if DIGS is None and 'short_description' in aback and aback['short_description'] and len(aback['short_description']) > 10:
			DIGS = py2_enc(aback.get('short_description'))
	if DIGS: description = DIGS
	stepUP = info.get('status', {}) if info.get('status', '') else info # Datumseinträge gibt es sowohl unter diesem Level als auch unter einem Level eine Stufe höher
	if str(stepUP.get('start_time'))[:4] not in ['None', '0', '1970']: # 2021-03-28T10:00:00.000+02:00
		LOCALstart = get_Local_DT(stepUP['start_time'][:19])
		startTIMES = LOCALstart.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
	if str(stepUP.get('end_time'))[:4] not in ['None', '0', '1970']: # 2021-03-28T10:30:00.000+02:00
		LOCALend = get_Local_DT(stepUP['end_time'][:19])
		endTIMES = LOCALend.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
	if info.get('season', ''):
		matchSE = re.findall('([0-9]+)', info.get('season'), re.S) # Staffel 1
		if matchSE: season = int(matchSE[0])
	if info.get('chapter', ''):
		matchEP = re.findall('([0-9]+)', info.get('chapter'), re.S) # Episode 6 - Infrastruktur
		if matchEP: episode = int(matchEP[0])
	if 'content_color' in info and info['content_color'] and len(info['content_color']) > 0:
		genre = py2_enc(info.get('content_color')[0])
	if info.get('playable', '') is True or info.get('action', '') == 'play':
		uv = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playVideo', 'url': eid}))
		liz.setProperty('IsPlayable', 'true')
		folder = False
		if info.get('duration', ''):
			duration = info.get('duration') / 1000
			ilabels['Duration'] = duration
			liz.addStreamInfo('Video', {'Duration': duration})
	elif category == 'COLLECTION':
		uv = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'listGeneralFull', 'url': eid, 'phrase': 'collections'}))
	elif category == 'PRODUCT':
		uv = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'listGeneralFull', 'url': eid, 'phrase': 'products'}))
	elif category == 'PLAYLIST':
		uv = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'listGeneralFull', 'url': eid, 'phrase': 'playlists'}))
	elif category == 'THEME':
		uv = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'listThemes', 'url': eid, 'phrase': 'products'}))
	if startTIMES and endTIMES: Note_1 = translation(32101).format(str(startTIMES), str(endTIMES))
	elif startTIMES and endTIMES is None: Note_1 = translation(32102).format(str(startTIMES))
	if tvshow != ""and Note_1 != "":
		origSERIE = tvshow+'[CR]'
	elif tvshow != ""and Note_1 == "":
		origSERIE = tvshow+'[CR][CR]'
	name = title_short if (not any(x in aback.get('id', '') for x in acronym) and aback.get('item_type', '') in ['mixed', 'video']) or tvshow == "" else title_short+' - '+tvshow
	liz.setLabel(name)
	ilabels['Season'] = season
	ilabels['Episode'] = episode
	ilabels['Tvshowtitle'] = tvshow
	ilabels['Title'] = name
	ilabels['Tagline'] = tagline
	ilabels['Plot'] = origSERIE+Note_1+description
	ilabels['Year'] = None
	ilabels['Genre'] = genre
	ilabels['Director'] = None
	ilabels['Writer'] = None
	ilabels['Studio'] = 'ServusTV'
	ilabels['Mpaa'] = None
	ilabels['Mediatype'] = cineType # mediatype  = "video", "movie", "tvshow", "season", "episode" , "musicvideo"
	liz.setInfo(type='Video', infoLabels=ilabels)
	liz.setArt({'icon': icon, 'thumb': icon, 'fanart': defaultFanart})
	if 'resources' in info or 'resources' in aback and aback.get('id', '') not in ['discover', 'calendar']:
		if info.get('resources', ''):
			num, resources, STOCK = info.get('id', ''), info.get('resources', []), True
		if not STOCK and aback.get('resources', ''):
			num, resources, STOCK = aback.get('id', ''), aback.get('resources', []), True
		if STOCK:
			liz.setArt({'fanart': get_Picture(num, resources, 'landscape')})
			liz.setArt({'landscape': get_Picture(num, resources, 'landscape')})
			liz.setArt({'banner': get_Picture(num, resources, 'banner')})
			liz.setArt({'poster': get_Picture(num, resources, 'portrait')})
			liz.setArt({'thumb': get_Picture(num, resources, 'square')})
	if 'all_episodes' in eid:
		if xbmcvfs.exists(channelFavsFile):
			with open(channelFavsFile, 'r') as fp:
				watch = json.load(fp)
				for item in watch.get('items', []):
					if item.get('url') == eid: addType = 2
		if addType == 1:
			entries.append([translation(30651), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': 'favs', 'action': 'ADD', 'name': py2_enc(aback.get('title')) if aback.get('title', '') else title_short,
				'pict': str(get_Picture(num, resources, 'square')), 'url': eid, 'plot': description.replace('\n', '[CR]') if DIGS else 'None', 'wallpaper': str(get_Picture(num, resources, 'landscape')), 'cineType': cineType}))])
	if not folder:
		entries.append([translation(30654), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)'])
	liz.addContextMenuItems(entries, replaceItems=False)
	if extras:
		debug_MS(extras+" ### TITLE = {0} || CINETYPE = {1} ###".format(name, cineType))
		debug_MS(extras+" ### EID = {0} || is FOLDER = {1} || DURATION = {2} ###".format(eid, str(folder), str(duration)))
		if STOCK: debug_MS(extras+" ### THUMB = {0} ###".format(str(get_Picture(num, resources, 'square'))))
	return (uv, liz, folder)

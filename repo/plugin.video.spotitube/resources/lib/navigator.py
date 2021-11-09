# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import random
import time
import datetime
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote_plus, unquote_plus  # Python 2.X
else:
	from urllib.parse import urlencode, quote_plus, unquote_plus  # Python 3.X

from .common import *


if itunesForceCountry and itunesCountry:
	iTunesRegion = itunesCountry
else:
	iTunesRegion = region

if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

if myTOKEN == 'AIzaSy.................................':
	xbmc.executebuiltin('addon.openSettings({0})'.format(addon_id))

if os.path.isdir(tempCAPA):
	for root, dirs, files in os.walk(tempCAPA):
		for name in files:
			filename = os.path.join(root, name).encode('utf-8').decode('utf-8')
			try:
				if os.path.exists(filename):
					if os.path.getmtime(filename) < time.time() - (60*60*cacheHours): # Check if CACHE-File exists and remove CACHE-File after defined cacheHours
						os.unlink(filename)
			except: pass


def mainMenu():
	addDir(translation(30601), artpic+'deepsearch.gif', {'mode': 'SearchDeezer'})
	addDir(translation(30602), artpic+'beatport.png', {'mode': 'beatportMain', 'url': 'https://pro.beatport.com'})
	addDir(translation(30603), artpic+'billboard.png', {'mode': 'billboardMain'})
	addDir(translation(30604), artpic+'ddp-international.png', {'mode': 'ddpMain', 'url': BASE_URL_DDP+'DDP-Charts/'})
	addDir(translation(30605), artpic+'hypem.png', {'mode': 'hypemMain'})
	addDir(translation(30606), artpic+'itunes.png', {'mode': 'itunesMain'})
	addDir(translation(30607), artpic+'official.png', {'mode': 'ocMain'})
	addDir(translation(30608), artpic+'spotify.png', {'mode': 'spotifyMain'})
	if enableADJUSTMENT:
		addDir(translation(30609), artpic+'settings.png', {'mode': 'aSettings'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def beatportMain(url):
	content = getCache(url)
	content = content[content.find('<div class="mobile-menu-body">')+1:]
	content = content[:content.find('<!-- End Mobile Touch Menu -->')]
	match = re.compile('<a href="(.*?)" class="(.*?)" data-name=".+?">(.*?)</a>', re.DOTALL).findall(content)
	addAutoPlayDir(translation(30620), artpic+'beatport.png', {'mode': 'listBeatportVideos', 'url': BASE_URL_BP+'/top-100'})
	for genreURL, genreTYPE, genreTITLE in match:
		topUrl = BASE_URL_BP+genreURL+'/top-100'
		title = cleaning(genreTITLE)
		addAutoPlayDir(title, artpic+'beatport.png', {'mode': 'listBeatportVideos', 'url': topUrl})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listBeatportVideos(url, type, limit):
	musicVideos = []
	count = 0
	playlist = cleanPlaylist() if type == 'play' else None
	content = getCache(url)
	spl = content.split('bucket-item ec-item track')
	for i in range(1,len(spl),1):
		entry = spl[i]
		artist = re.compile('data-artist=".+?">(.*?)</a>', re.DOTALL).findall(entry)[0]
		artist = cleaning(artist)
		song = re.compile('<span class="buk-track-primary-title" title=".+?">(.*?)</span>', re.DOTALL).findall(entry)[0]
		remix = re.compile('<span class="buk-track-remixed">(.*?)</span>', re.DOTALL).findall(entry)
		if '(original mix)' in song.lower():
			song = song.lower().split('(original mix)')[0]
		song = cleaning(song)
		if '(feat.' in song.lower() and ' feat.' in song.lower():
			song = song.split(')')[0]+')'
		elif not '(feat.' in song.lower() and ' feat.' in song.lower():
			firstSong = song.lower().split(' feat.')[0]
			secondSong = song.lower().split(' feat.')[1]
			song = firstSong+' (feat.'+secondSong+')'
		if remix and not 'original' in remix[0].lower():
			newRemix = remix[0].replace('[', '').replace(']', '')
			song += ' ['+cleaning(newRemix)+']'
		firstTitle = artist+" - "+song
		try:
			oldDate = re.compile('<p class="buk-track-released">(.*?)</p>', re.DOTALL).findall(entry)[0]
			convert = time.strptime(oldDate,'%Y-%m-%d')
			newDate = time.strftime('%d.%m.%Y',convert)
			completeTitle = firstTitle+'   [COLOR deepskyblue]['+str(newDate)+'][/COLOR]'
		except: completeTitle = firstTitle
		try:
			thumb = re.compile('data-src="(http.*?.jpg)"', re.DOTALL).findall(entry)[0]
			thumb = thumb.split('image_size')[0]+'image/'+thumb.split('/')[-1]
			#thumb = thumb.replace('/30x30/','/500x500/').replace('/60x60/','/500x500/').replace('/95x95/','/500x500/').replace('/250x250/','/500x500/')
		except: thumb = artpic+'noimage.png'
		filtered = False
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				filtered = True
		if filtered: continue
		musicVideos.append([firstTitle, completeTitle, thumb])
	if type == 'browse':
		for firstTitle, completeTitle, thumb in musicVideos:
			count += 1
			name = '[COLOR chartreuse]'+str(count)+' •  [/COLOR]'+completeTitle
			addLink(name, thumb, {'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')})
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(limit) > 0:
			musicVideos = musicVideos[:int(limit)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			playlist.add(endUrl, listitem)
		xbmc.Player().play(playlist)

def billboardMain():
	addAutoPlayDir(translation(30630), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/hot-100'})
	addAutoPlayDir(translation(30631), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/billboard-200'})
	addDir(translation(30632), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'genre'})
	addDir(translation(30633), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'country'})
	addDir(translation(30634), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'other'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBillboardCharts(type):
	if type == 'genre':
		addAutoPlayDir('Alternative', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/alternative-songs'})
		addAutoPlayDir('Country', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/country-songs'})
		addAutoPlayDir('Dance/Club', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/dance-club-play-songs'})
		addAutoPlayDir('Dance/Electronic', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/dance-electronic-songs'})
		addAutoPlayDir('Gospel', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/gospel-songs'})
		addAutoPlayDir('Latin', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/latin-songs'})
		addAutoPlayDir('Pop', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/pop-songs'})
		addAutoPlayDir('Rap', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/rap-song'})
		addAutoPlayDir('R&B', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/r-and-b-songs'})
		addAutoPlayDir('R&B/Hip-Hop', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/r-b-hip-hop-songs'})
		addAutoPlayDir('Rhythmic', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/rhythmic-40'})
		addAutoPlayDir('Rock', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/rock-songs'})
		addAutoPlayDir('Smooth Jazz', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/jazz-songs'})
		addAutoPlayDir('Soundtracks', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/soundtracks'})
		addAutoPlayDir('Tropical', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/latin-tropical-airplay'})
	elif type == 'country':
		addAutoPlayDir('Argentina Hot-100', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/billboard-argentina-hot-100'})
		addAutoPlayDir('Canada Hot-100', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/canadian-hot-100'})
		addAutoPlayDir('Australia - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/australia-digital-song-sales'})
		addAutoPlayDir('Canadian - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/hot-canada-digital-song-sales'})
		addAutoPlayDir('Euro - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/euro-digital-song-sales'})
		addAutoPlayDir('France - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/france-digital-song-sales'})
		addAutoPlayDir('Germany - Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/germany-songs'})
		addAutoPlayDir('Italy - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/italy-digital-song-sales'})
		addAutoPlayDir('Spain - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/spain-digital-song-sales'})
		addAutoPlayDir('Switzerland - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/switzerland-digital-song-sales'})
		addAutoPlayDir('U.K. - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/uk-digital-song-sales'})
		addAutoPlayDir('World - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/world-digital-song-sales'})
	elif type == 'other':
		addAutoPlayDir('Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/digital-song-sales'})
		addAutoPlayDir('On-Demand Streaming Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/on-demand-songs'})
		addAutoPlayDir('Radio Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/radio-songs'})
		addAutoPlayDir('TOP Songs of the ’90s', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-billboards-top-songs-90s'})
		addAutoPlayDir('TOP Songs of the ’80s', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-billboards-top-songs-80s'})
		addAutoPlayDir('All Time Hot 100 Singles', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-hot-100-singles'})
		addAutoPlayDir('All Time Greatest Alternative Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-alternative-songs'})
		addAutoPlayDir('All Time Greatest Country Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-country-songs'})
		addAutoPlayDir('All Time Greatest Latin Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-hot-latin-songs'})
		addAutoPlayDir('All Time Greatest Pop Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-of-all-time-pop-songs'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listBillboardVideos(url, type, limit):
	musicVideos = []
	startURL = url
	count = 0
	playlist = cleanPlaylist() if type == 'play' else None
	content = getCache(url)
	if 'data-charts=' in content:
		response = re.compile(r'data-charts="(.+?)".*? data-icons=', re.DOTALL).findall(content)[0].replace("&quot;", "\"").replace("&Quot;", "\"").replace('\/', '/')
		DATA = json.loads(response)
		for item in DATA:
			artist = cleaning(item['artist_name'])
			song = cleaning(item['title'])
			firstTitle = artist+" - "+song
			completeTitle = firstTitle
			if not 'charts/greatest-' in startURL:
				try:
					LW = item['history']['last_week']
					twoW = item['history']['two_weeks']
					weeksChart = item['history']['weeks_on_chart']
					completeTitle = firstTitle+'   [COLOR deepskyblue][LW: '+str(LW).replace('None', '~')+'|2W: '+str(twoW).replace('None', '~')+'|inChart: '+str(weeksChart)+'W][/COLOR]'
				except: pass
			try:
				max_res = max(item['title_images']['sizes'].items(), key=lambda ele:ele[1]['Width'])
				for key, val in dict([max_res]).items():
					imgURL = val.get('Name', '')
				thumb = 'https://charts-static.billboard.com'+imgURL if imgURL[:4] != 'http' else imgURL
			except: thumb = artpic+'noimage.png'
			filtered = False
			for snippet in blackList:
				if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
					filtered = True
			if filtered: continue
			musicVideos.append([firstTitle, completeTitle, thumb])
	else:
		spl = content.split('class="chart-list-item__image-wrapper">')
		for i in range(1,len(spl),1):
			entry = spl[i]
			artist = re.compile('<div class="chart-list-item__artist">(.*?)</div>', re.DOTALL).findall(entry)[0]
			artist = re.sub(r'\<.*?>', '', artist)
			artist = cleaning(artist)
			song = re.compile('<span class="chart-list-item__title-text">(.*?)</span>', re.DOTALL).findall(entry)[0]
			song = re.sub(r'\<.*?>', '', song)
			song = cleaning(song)
			firstTitle = artist+" - "+song
			completeTitle = firstTitle
			if not 'charts/greatest-' in startURL:
				try:
					LW = re.compile('<div class="chart-list-item__last-week">(.*?)</div>', re.DOTALL).findall(entry)[0]
					twoW = re.compile('<div class="chart-list-item__last-week">(.*?)</div>', re.DOTALL).findall(entry)[1]
					weeksChart = re.compile('<div class="chart-list-item__weeks-on-chart">(.*?)</div>', re.DOTALL).findall(entry)[0]
					completeTitle = firstTitle+'   [COLOR deepskyblue][LW: '+str(LW).replace('-', '~')+'|2W: '+str(twoW).replace('-', '~')+'|inChart: '+str(weeksChart)+'W][/COLOR]'
				except: pass
			try:
				img = re.compile(r'(?:<img src="|data-srcset=")(https?://charts-static.billboard.com.+?(?:\.jpg|\.jpeg|\.png))', re.DOTALL).findall(entry)[0]
				thumb = img.replace('-53x53', '-480x480').replace('-87x87', '-480x480').replace('-106x106', '-480x480').replace('-174x174', '-480x480').replace('-240x240', '-480x480').strip()+'?1'
			except: thumb = artpic+'noimage.png'
			filtered = False
			for snippet in blackList:
				if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
					filtered = True
			if filtered: continue
			musicVideos.append([firstTitle, completeTitle, thumb])
	if type == 'browse':
		for firstTitle, completeTitle, thumb in musicVideos:
			count += 1
			name = '[COLOR chartreuse]'+str(count)+' •  [/COLOR]'+completeTitle
			addLink(name, thumb, {'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')})
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(limit) > 0:
			musicVideos = musicVideos[:int(limit)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			playlist.add(endUrl, listitem)
		xbmc.Player().play(playlist)

def ddpMain(url):
	content = getCache(url)
	content = content[content.find('<div class="ddp_subnavigation_top ddp">')+1:]
	content = content[:content.find('<div class="contentbox">')]
	addDir('[COLOR deepskyblue]'+translation(30640)+'[/COLOR]', artpic+'ddp-international.png', {'mode': 'ddpMain', 'url': url})
	addAutoPlayDir('..... AKTUELLE VIDEOS TOP 30', artpic+'ddp-international.png', {'mode': 'listDdpVideos', 'url': BASE_URL_DDP+'DDP-Videochart/'})
	match = re.compile('<li><a href="(.*?)">(.*?)</a></li>', re.DOTALL).findall(content)
	for url2, title2 in match:
		url2 = url2.split('/?')[0]
		title2 = cleaning(title2)
		if title2.lower() not in ['archiv', 'ddp', 'highscores']:
			if not 'schlager' in url2.lower():
				if title2.lower() in ['top 100','hot 50', 'neueinsteiger']:
					addAutoPlayDir('..... '+title2, artpic+'ddp-international.png', {'mode': 'listDdpVideos', 'url': url2})
				elif 'jahrescharts' in title2.lower():
					addDir('..... '+title2, artpic+'ddp-international.png', {'mode': 'listDdpYearCharts', 'url': url2})
	addDir('[COLOR deepskyblue]'+translation(30641)+'[/COLOR]', artpic+'ddp-schlager.png', {'mode': 'ddpMain', 'url': url})
	for url2, title2 in match:
		url2 = url2.split('/?')[0]
		title2 = cleaning(title2)
		if title2.lower() not in ['archiv', 'ddp', 'highscores']:
			if 'schlager' in url2.lower():
				if title2.lower() in ['top 100','hot 50', 'neueinsteiger']:
					addAutoPlayDir('..... '+title2, artpic+'ddp-schlager.png', {'mode': 'listDdpVideos', 'url': url2})
				elif 'jahrescharts' in title2.lower():
					addDir('..... '+title2, artpic+'ddp-schlager.png', {'mode': 'listDdpYearCharts', 'url': url2})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listDdpYearCharts(url):
	musicVideos = []
	content = getCache(url)
	content = content[content.find('<div class="contentbox">')+1:]
	content = content[:content.find('</p>')]
	match = re.compile('<a href="(.*?)" alt="(.*?)">', re.DOTALL).findall(content)
	for url2, title in match:
		if 'schlager' in url.lower():
			newUrl = BASE_URL_DDP+'DDP-Schlager-Jahrescharts/?'+url2.split('/?')[1]
			thumb = artpic+'ddp-schlager.png'
		elif not 'schlager' in url.lower():
			newUrl = BASE_URL_DDP+'DDP-Jahrescharts/?'+url2.split('/?')[1]
			thumb = artpic+'ddp-international.png'
		musicVideos.append([title, newUrl, thumb])
	musicVideos = sorted(musicVideos, key=lambda d:d[0], reverse=True)
	for title, newUrl, thumb in musicVideos:
		addAutoPlayDir(cleaning(title), thumb, {'mode': 'listDdpVideos', 'url': newUrl})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listDdpVideos(url, type, limit):
	musicVideos = []
	musicIsolated = set()
	playlist = cleanPlaylist() if type == 'play' else None
	content = getCache(url)
	content = content[content.find('<div class="eintrag" id="charthead">')+1:]
	content = content[:content.find('<div id="banner_fuss">')]
	spl = content.split('<div class="eintrag">')
	for i in range(1,len(spl),1):
		entry = spl[i]
		rank = re.compile('<div class="platz">(.*?)</div>', re.DOTALL).findall(entry)[0]
		artist = re.compile('<div class="interpret">(.*?)</div>', re.DOTALL).findall(entry)[0]
		song = re.compile('<div class="titel">(.*?)</div>', re.DOTALL).findall(entry)[0]
		if song == "" or artist == "":
			continue
		artist = py2_uni(artist).title()
		artist = cleaning(artist)
		song = py2_uni(song).title()
		song = cleaning(song)
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated:
			continue
		musicIsolated.add(firstTitle)
		try:
			newRE = re.compile('<div class="platz">(.*?)</div>', re.DOTALL).findall(entry)[1]
			LW = re.compile('<div class="platz">(.*?)</div>', re.DOTALL).findall(entry)[2]
			twoW = re.compile('<div class="platz">(.*?)</div>', re.DOTALL).findall(entry)[3]
			threeW = re.compile('<div class="platz">(.*?)</div>', re.DOTALL).findall(entry)[4]
			if ('RE' in newRE or 'NEU' in newRE) and not 'images' in newRE:
				completeTitle = firstTitle+'   [COLOR deepskyblue]['+str(newRE)+'][/COLOR]'
			else:
				completeTitle = firstTitle+'   [COLOR deepskyblue][AW: '+str(LW)+'|2W: '+str(twoW)+'|3W: '+str(threeW)+'][/COLOR]'
		except: completeTitle = firstTitle
		try:
			thumb = re.findall('style="background.+?//poolposition.mp3(.*?);"',entry,re.S)[0]
			thumb = 'https://poolposition.mp3'+thumb.split('&amp;width')[0]
		except: thumb = artpic+'noimage.png'
		filtered = False
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				filtered = True
		if filtered: continue
		musicVideos.append([int(rank), firstTitle, completeTitle, thumb])
	musicVideos = sorted(musicVideos, key=lambda d:d[0], reverse=False)
	if type == 'browse':
		for rank, firstTitle, completeTitle, thumb in musicVideos:
			name = '[COLOR chartreuse]'+str(rank)+' •  [/COLOR]'+completeTitle
			addLink(name, thumb, {'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')})
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(limit) > 0:
			musicVideos = musicVideos[:int(limit)]
		random.shuffle(musicVideos)
		for rank, firstTitle, completeTitle, thumb in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			playlist.add(endUrl, listitem)
		xbmc.Player().play(playlist)

def hypemMain():
	addAutoPlayDir(translation(30650), artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': BASE_URL_HM+'/popular?ax=1&sortby=shuffle'})
	addAutoPlayDir(translation(30651), artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': BASE_URL_HM+'/popular/lastweek?ax=1&sortby=shuffle'})
	addDir(translation(30652), artpic+'hypem.png', {'mode': 'listHypemMachine'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listHypemMachine():
	for i in range(1, 201, 1):
		dt = datetime.date.today()
		while dt.weekday() != 0:
			dt -= datetime.timedelta(days=1)
		dt -= datetime.timedelta(weeks=i)
		months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		month = months[int(dt.strftime('%m')) - 1]
		addAutoPlayDir(dt.strftime('%d. %b - %Y').replace('Mar', translation(30653)).replace('May', translation(30654)).replace('Oct', translation(30655)).replace('Dec', translation(30656)), artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': BASE_URL_HM+'/popular/week:'+month+'-'+dt.strftime('%d-%Y')+'?ax=1&sortby=shuffle'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listHypemVideos(url, type, limit):
	musicVideos = []
	musicIsolated = set()
	count = 0
	playlist = cleanPlaylist() if type == 'play' else None
	content = getCache(url)
	response = re.compile('id="displayList-data">(.*?)</', re.DOTALL).findall(content)[0]
	DATA = json.loads(response)
	for item in DATA['tracks']:
		artist = cleaning(item['artist'])
		song = cleaning(item['song'])
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated or artist == "":
			continue
		musicIsolated.add(firstTitle)
		match = re.compile('href="/track/'+item['id']+'/.+?background:url\\((.+?)\\)', re.DOTALL).findall(content)
		thumb = match[0] if match else "" #.replace('_320.jpg)', '_500.jpg')
		filtered = False
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				filtered = True
		if filtered: continue
		musicVideos.append([firstTitle, thumb])
	if type == 'browse':
		for firstTitle, thumb in musicVideos:
			count += 1
			name = '[COLOR chartreuse]'+str(count)+' •  [/COLOR]'+firstTitle
			addLink(name, thumb, {'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')})
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(limit) > 0:
			musicVideos = musicVideos[:int(limit)]
		random.shuffle(musicVideos)
		for firstTitle, thumb in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			playlist.add(endUrl, listitem)
		xbmc.Player().play(playlist)

def itunesMain():
	content = getCache('https://itunes.apple.com/{0}/genre/music/id34'.format(iTunesRegion))
	content = content[content.find('id="genre-nav"'):]
	content = content[:content.find('</div>')]
	match = re.compile('<li><a href="https?://(?:itunes.|music.)apple.com/.+?/genre/.+?/id(.*?)"(.*?)title=".+?">(.*?)</a>', re.DOTALL).findall(content)
	addAutoPlayDir(translation(30660), artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': '0'})
	for genreID, genreTYPE, genreTITLE in match:
		title = cleaning(genreTITLE)
		if 'class="top-level-genre"' in genreTYPE:
			if itunesShowSubGenres:
				title = '[COLOR deepskyblue]'+title+'[/COLOR]'
			addAutoPlayDir(title, artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': genreID})
		elif itunesShowSubGenres:
			addAutoPlayDir('..... '+title, artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': genreID})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listItunesVideos(genreID, type, limit):
	musicVideos = []
	musicIsolated = set()
	count = 0
	playlist = cleanPlaylist() if type == 'play' else None
	url = 'https://itunes.apple.com/{0}/rss/topsongs/limit=100'.format(iTunesRegion)
	if genreID != '0':
		url += '/genre='+genreID
	url += '/explicit=true/json'
	content = getCache(url)
	response = json.loads(content)
	for item in response['feed']['entry']:
		artist = cleaning(item['im:artist']['label'])
		song = cleaning(item['im:name']['label'])
		title = artist+" - "+song
		newTitle = song.lower()
		if newTitle in musicIsolated:
			continue
		musicIsolated.add(newTitle)
		if len(artist) > 30:
			artist = artist[:30]
		if len(song) > 30:
			song = song[:30]
		ShortForUrl = artist+" - "+song
		try: thumb = item['im:image'][2]['label'].replace('/170x170bb.png', '/512x512bb.jpg').replace('/170x170bb.jpg', '/512x512bb.jpg')
		except: thumb = artpic+'noimage.png'
		try: aired = item['im:releaseDate']['attributes']['label']
		except: aired = '0'
		filtered = False
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in title.lower():
				filtered = True
		if filtered: continue
		musicVideos.append([title, ShortForUrl, aired, thumb])
	if type == 'browse':
		for title, ShortForUrl, aired, thumb in musicVideos:
			count += 1
			name = '[COLOR chartreuse]'+str(count)+' •  [/COLOR]'+title
			if aired != '0': name += '   [COLOR deepskyblue]['+str(aired)+'][/COLOR]'
			addLink(name, thumb, {'mode': 'playYTByTitle', 'url': ShortForUrl.replace(' - ', ' ')})
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(limit) > 0:
			musicVideos = musicVideos[:int(limit)]
		random.shuffle(musicVideos)
		for title, ShortForUrl, aired, thumb in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playYTByTitle', 'url': ShortForUrl.replace(' - ', ' ')}))
			listitem = xbmcgui.ListItem(title)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			playlist.add(endUrl, listitem)
		xbmc.Player().play(playlist)

def ocMain():
	addAutoPlayDir(translation(30670), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/singles-chart/'})
	addAutoPlayDir(translation(30671), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/uk-top-40-singles-chart/'})
	addAutoPlayDir(translation(30672), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/singles-chart-update/'})
	addAutoPlayDir(translation(30673), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/singles-downloads-chart/'})
	addAutoPlayDir(translation(30674), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/singles-sales-chart/'})
	addAutoPlayDir(translation(30675), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/audio-streaming-chart/'})
	addAutoPlayDir(translation(30676), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/dance-singles-chart/'})
	addAutoPlayDir(translation(30677), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/classical-singles-chart/'})
	addAutoPlayDir(translation(30678), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/r-and-b-singles-chart/'})
	addAutoPlayDir(translation(30679), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/rock-and-metal-singles-chart/'})
	addAutoPlayDir(translation(30680), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/irish-singles-chart/'})
	addAutoPlayDir(translation(30681), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/scottish-singles-chart/'})
	addAutoPlayDir(translation(30682), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/end-of-year-singles-chart/'})
	addAutoPlayDir(translation(30683), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/physical-singles-chart/'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listOcVideos(url, type, limit):
	musicVideos = []
	musicIsolated = set()
	count = 0
	playlist = cleanPlaylist() if type == 'play' else None
	content = getCache(url)
	match = re.findall(r'<div class=["\']track["\']>(.*?)<div class=["\']actions["\']>', content, re.DOTALL)
	for video in match:
		photo = re.compile(r'<img src=["\'](.*?)["\']', re.DOTALL).findall(video)[0]
		if 'amazon.com' in photo or 'coverartarchive.org' in photo:
			thumb = photo.split('img/small?url=')[1].replace('http://ecx.images-amazon.com', 'https://m.media-amazon.com').replace('L._SL75_', 'L')
		elif '/img/small?url=/images/artwork/' in photo:
			thumb = photo.replace('/img/small?url=', '')
		else:
			thumb = artpic+'noimage.png'
		song = re.compile(r'<a href=["\'].+?["\']>(.*?)</a>', re.DOTALL).findall(video)[0]
		artist = re.compile(r'<a href=["\'].+?["\']>(.*?)</a>', re.DOTALL).findall(video)[1]
		artist = artist.split('/')[0] if '/' in artist else artist
		song = cleaning(song)
		song = TitleCase(song)
		artist = cleaning(artist)
		artist = TitleCase(artist)
		firstTitle = artist+" - "+song
		filtered = False
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				filtered = True
		if filtered: continue
		musicVideos.append([firstTitle, thumb])
	if type == 'browse':
		for firstTitle, thumb in musicVideos:
			count += 1
			name = '[COLOR chartreuse]'+str(count)+' •  [/COLOR]'+firstTitle
			addLink(name, thumb, {'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')})
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(limit) > 0:
			musicVideos = musicVideos[:int(limit)]
		random.shuffle(musicVideos)
		for firstTitle, thumb in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			playlist.add(endUrl, listitem)
		xbmc.Player().play(playlist)

def spotifyMain():
	addDir(translation(30690), artpic+'spotify.png', {'mode': 'listSpotifyCC_Countries', 'url': 'viraldaily'})
	addDir(translation(30691), artpic+'spotify.png', {'mode': 'listSpotifyCC_Countries', 'url': 'viralweekly'})
	addDir(translation(30692), artpic+'spotify.png', {'mode': 'listSpotifyCC_Countries', 'url': 'topdaily'})
	addDir(translation(30693), artpic+'spotify.png', {'mode': 'listSpotifyCC_Countries', 'url': 'topweekly'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSpotifyCC_Countries(type):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	musicIsolated = set()
	UN_Supported = ['andorra', 'bulgaria', 'cyprus', 'hong kong', 'israel', 'japan', 'monaco', 'malta', 'nicaragua', 'singapore', 'thailand', 'taiwan'] # these lists are empty or signs are not readable
	content = getCache(BASE_URL_SCC+'regional')
	content = content[content.find('<div class="responsive-select" data-type="country">')+1:]
	content = content[:content.find('<div class="responsive-select" data-type="recurrence">')]
	match = re.compile('<li data-value="(.*?)" class=.+?>(.*?)</li>', re.DOTALL).findall(content)
	for url2, toptitle in match:
		if any(x in toptitle.strip().lower() for x in UN_Supported):
			continue
		if toptitle.strip() in musicIsolated:
			continue
		musicIsolated.add(toptitle)
		if type == 'viraldaily':
			addAutoPlayDir(cleaning(toptitle), artpic+'spotify.png', {'mode': 'listSpotifyCC_Videos', 'url': BASE_URL_SCC+'viral/'+url2+'/daily/latest'})
		elif type == 'viralweekly':
			addAutoPlayDir(cleaning(toptitle), artpic+'spotify.png', {'mode': 'listSpotifyCC_Videos', 'url': BASE_URL_SCC+'viral/'+url2+'/weekly/latest'})
		elif type == 'topdaily':
			addAutoPlayDir(cleaning(toptitle), artpic+'spotify.png', {'mode': 'listSpotifyCC_Videos', 'url': BASE_URL_SCC+'regional/'+url2+'/daily/latest'})
		elif type == 'topweekly':
			addAutoPlayDir(cleaning(toptitle), artpic+'spotify.png', {'mode': 'listSpotifyCC_Videos', 'url': BASE_URL_SCC+'regional/'+url2+'/weekly/latest'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listSpotifyCC_Videos(url, type, limit):
	musicVideos = []
	musicIsolated = set()
	count = 0
	playlist = cleanPlaylist() if type == 'play' else None
	content = getCache(url)
	content = content[content.find('<tbody>')+1:]
	content = content[:content.find('</tbody>')]
	spl = content.split('<tr>')
	for i in range(1,len(spl),1):
		entry = spl[i]
		song = re.compile('<strong>(.*?)</strong>', re.DOTALL).findall(entry)[0]
		song = cleaning(song)
		artist = re.compile('<span>(.*?)</span>', re.DOTALL).findall(entry)[0]
		artist = cleaning(artist)
		if '(remix)' in song.lower():
			song = song.lower().replace('(remix)', '')
		if ' - ' in song:
			firstSong = song[:song.rfind(' - ')]
			secondSong = song[song.rfind(' - ')+3:]
			song = firstSong+' ['+secondSong+']'
		if artist.lower().startswith('by', 0, 2):
			artist = artist.lower().split('by ')[1]
		if artist.islower():
			artist = TitleCase(artist)
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated or artist == "":
			continue
		musicIsolated.add(firstTitle)
		try:
			thumb = re.compile('<img src="(.*?)">', re.DOTALL).findall(entry)[0].replace('ab67616d00004851', 'ab67616d0000b273')
			thumb = 'https://i.scdn.co/image/'+thumb if thumb[:4] != 'http' else thumb
			#thumb = 'https://u.scdn.co/images/pl/default/'+thumb
		except: thumb = artpic+'noimage.png'
		try:
			streams = re.compile('<td class="chart-table-streams">(.*?)</td>', re.DOTALL).findall(entry)[0]
		except: streams = '0'
		filtered = False
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				filtered = True
		if filtered: continue
		musicVideos.append([firstTitle, streams, thumb])
	if type == 'browse':
		for firstTitle, streams, thumb in musicVideos:
			count += 1
			name = '[COLOR chartreuse]'+str(count)+' •  [/COLOR]'+firstTitle
			if streams != '0': name = '[COLOR chartreuse]'+str(count)+' •  [/COLOR]'+firstTitle+'   [COLOR deepskyblue][DL: '+str(streams).replace(',', '.')+'][/COLOR]'
			addLink(name, thumb, {'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')})
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(limit) > 0:
			musicVideos = musicVideos[:int(limit)]
		random.shuffle(musicVideos)
		for firstTitle, streams, thumb in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			playlist.add(endUrl, listitem)
		xbmc.Player().play(playlist)

def SearchDeezer():
	someReceived = False
	word = dialog.input(translation(30801), type=xbmcgui.INPUT_ALPHANUM)
	word = quote_plus(word, safe='')
	if word == "": return
	artistSEARCH = getCache('{0}/artist?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, word, deezerSearchDisplay))
	trackSEARCH = getCache('{0}/track?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, word, deezerSearchDisplay))
	albumSEARCH = getCache('{0}/album?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, word, deezerSearchDisplay))
	playlistSEARCH = getCache('{0}/playlist?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, word, deezerSearchDisplay))
	userlistSEARCH = getCache('{0}/user?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, word, deezerSearchDisplay))
	strukturARTIST = json.loads(artistSEARCH)
	if strukturARTIST['total'] != 0:
		addDir('[B][COLOR orangered] •  •  •  [/COLOR]ARTIST[COLOR orangered]  •  •  •[/COLOR][/B]', artpic+'searchartists.png', {'mode': 'listDeezerArtists', 'url': word})
		someReceived = True
	strukturTRACK = json.loads(trackSEARCH)
	if strukturTRACK['total'] != 0:
		addDir('[B][COLOR orangered] •  •  •  [/COLOR]SONG[COLOR orangered]     •  •  •[/COLOR][/B]', artpic+'searchsongs.png', {'mode': 'listDeezerTracks', 'url': word})
		someReceived = True
	strukturALBUM = json.loads(albumSEARCH)
	if strukturALBUM['total'] != 0:
		addDir('[B][COLOR orangered] •  •  •  [/COLOR]ALBUM[COLOR orangered]  •  •  •[/COLOR][/B]', artpic+'searchalbums.png', {'mode': 'listDeezerAlbums', 'url': word})
		someReceived = True
	strukturPLAYLIST = json.loads(playlistSEARCH)
	if strukturPLAYLIST['total'] != 0:
		addDir('[B][COLOR orangered] •  •  •  [/COLOR]PLAYLIST[COLOR orangered]  •  •  •[/COLOR][/B]', artpic+'searchplaylists.png', {'mode': 'listDeezerPlaylists', 'url': word})
		someReceived = True
	strukturUSERLIST = json.loads(userlistSEARCH)
	if strukturUSERLIST['total'] != 0:
		addDir('[B][COLOR orangered] •  •  •  [/COLOR]USER[COLOR orangered]     •  •  •[/COLOR][/B]', artpic+'searchuserlists.png', {'mode': 'listDeezerUserlists', 'url': word})
		someReceived = True
	if not someReceived:
		addDir(translation(30802), artpic+'noresults.png', {'mode': 'root', 'url': word})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listDeezerArtists(url):
	musicVideos = []
	musicIsolated = set()
	if url.startswith(BASE_URL_DZ):
		Forward = getCache(url)
		response = json.loads(Forward)
	else:
		Original = getCache('{0}/artist?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, url, deezerSearchDisplay))
		response = json.loads(Original)
	for item in response['data']:
		artist = cleaning(item['name'])
		if artist.strip().lower() in musicIsolated or artist == "":
			continue
		musicIsolated.add(artist)
		try:
			thumb = item['picture_big']
			if thumb.endswith('artist//500x500-000000-80-0-0.jpg'):
				thumb = artpic+'noavatar.gif'
		except: thumb = artpic+'noavatar.gif'
		liked = str(item['nb_fan'])
		tracksUrl = item['tracklist'].split('top?limit=')[0]+'top?limit={0}&index=0'.format(deezerVideosDisplay)
		musicVideos.append([int(liked), artist, tracksUrl, thumb])
	musicVideos = sorted(musicVideos, key=lambda d:d[0], reverse=True)
	for liked, artist, tracksUrl, thumb in musicVideos:
		name = artist+'   [COLOR FFFFA500][Fans: '+str(liked)+'][/COLOR]'
		addAutoPlayDir(name, thumb, {'mode': 'listDeezerVideos', 'url': tracksUrl, 'extras': thumb})
	try:
		nextPage = response['next']
		if BASE_URL_DZ in nextPage:
			addDir(translation(30803), artpic+'nextpage.png', {'mode': 'listDeezerArtists', 'url': nextPage})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listDeezerTracks(url):
	musicIsolated = set()
	if url.startswith(BASE_URL_DZ):
		Forward = getCache(url)
		response = json.loads(Forward)
	else:
		Original = getCache('{0}/track?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, url, deezerSearchDisplay))
		response = json.loads(Original)
	for item in response['data']:
		artist = cleaning(item['artist']['name'])
		song = cleaning(item['title'])
		title = artist+" - "+song
		if title in musicIsolated or artist == "":
			continue
		musicIsolated.add(title)
		album = cleaning(item['album']['title'])
		try: thumb = item['album']['cover_big']
		except: thumb = artpic+'noimage.png'
		filtered = False
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in title.lower():
				filtered = True
		if filtered: continue
		name = title+'   [COLOR deepskyblue][Album: '+album+'][/COLOR]'
		addLink(name, thumb, {'mode': 'playYTByTitle', 'url': title.replace(' - ', ' ')})
	try:
		nextPage = response['next']
		if BASE_URL_DZ in nextPage:
			addDir(translation(30803), artpic+'nextpage.png', {'mode': 'listDeezerTracks', 'url': nextPage})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listDeezerAlbums(url):
	musicIsolated = set()
	if url.startswith(BASE_URL_DZ):
		Forward = getCache(url)
		response = json.loads(Forward)
	else:
		Original = getCache('{0}/album?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, url, deezerSearchDisplay))
		response = json.loads(Original)
	for item in response['data']:
		artist = cleaning(item['artist']['name'])
		album = cleaning(item['title'])
		title = artist+" - "+album
		if title in musicIsolated or artist == "":
			continue
		musicIsolated.add(title)
		try: thumb = item['cover_big']
		except: thumb = artpic+'noimage.png'
		numbers = str(item['nb_tracks'])
		tracksUrl = item['tracklist']+'?limit={0}&index=0'.format(deezerVideosDisplay)
		version = cleaning(item['record_type']).title()
		name = title+'   [COLOR deepskyblue]['+version+'[/COLOR] - [COLOR FFFFA500]Tracks: '+numbers+'][/COLOR]'
		addAutoPlayDir(name, thumb, {'mode': 'listDeezerVideos', 'url': tracksUrl, 'extras': thumb})
	try:
		nextPage = response['next']
		if BASE_URL_DZ in nextPage:
			addDir(translation(30803), artpic+'nextpage.png', {'mode': 'listDeezerAlbums', 'url': nextPage})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listDeezerPlaylists(url):
	musicIsolated = set()
	if url.startswith(BASE_URL_DZ):
		Forward = getCache(url)
		response = json.loads(Forward)
	else:
		Original = getCache('{0}/playlist?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, url, deezerSearchDisplay))
		response = json.loads(Original)
	for item in response['data']:
		artist = py2_uni(item['title']).title()
		artist = cleaning(artist)
		try: thumb = item['picture_big']
		except: thumb = artpic+'noimage.png'
		numbers = str(item['nb_tracks'])
		tracksUrl = item['tracklist']+'?limit={0}&index=0'.format(deezerVideosDisplay)
		user = py2_uni(item['user']['name']).title()
		user = cleaning(user)
		name = artist+'   [COLOR deepskyblue][User: '+user+'[/COLOR] - [COLOR FFFFA500]Tracks: '+numbers+'][/COLOR]'
		special = artist+" - "+user
		if special in musicIsolated or artist == "":
			continue
		musicIsolated.add(special)
		addAutoPlayDir(name, thumb, {'mode': 'listDeezerVideos', 'url': tracksUrl, 'extras': thumb})
	try:
		nextPage = response['next']
		if BASE_URL_DZ in nextPage:
			addDir(translation(30803), artpic+'nextpage.png', {'mode': 'listDeezerPlaylists', 'url': nextPage})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listDeezerUserlists(url):
	musicIsolated = set()
	if url.startswith(BASE_URL_DZ):
		Forward = getCache(url)
		response = json.loads(Forward)
	else:
		Original = getCache('{0}/user?q={1}&limit={2}&strict=on&output=json&index=0'.format(BASE_URL_DZ, url, deezerSearchDisplay))
		response = json.loads(Original)
	for item in response['data']:
		user = cleaning(item['name'])
		try:
			thumb = item['picture_big']
			if thumb.endswith('user//500x500-000000-80-0-0.jpg'):
				thumb = artpic+'noavatar.gif'
		except: thumb = artpic+'noavatar.gif'
		tracksUrl = item['tracklist']+'?limit={0}&index=0'.format(deezerVideosDisplay)
		name = TitleCase(user)
		if name in musicIsolated or user == "":
			continue
		musicIsolated.add(name)
		addAutoPlayDir(name, thumb, {'mode': 'listDeezerVideos', 'url': tracksUrl, 'extras': thumb})
	try:
		nextPage = response['next']
		if BASE_URL_DZ in nextPage:
			addDir(translation(30803), artpic+'nextpage.png', {'mode': 'listDeezerUserlists', 'url': nextPage})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listDeezerVideos(url, type, limit, photo):
	musicVideos = []
	musicIsolated = set()
	count = 0
	playlist = cleanPlaylist() if type == 'play' else None
	if not '&index=0' in url:
		Forward = getCache(url)
		response = json.loads(Forward)
	else:
		Original = getCache(url)
		response = json.loads(Original)
	for item in response['data']:
		artist = cleaning(item['artist']['name'])
		song = cleaning(item['title'])
		if song.isupper():
			song = TitleCase(song)
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated or artist == "":
			continue
		musicIsolated.add(firstTitle)
		filtered = False
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				filtered = True
		if filtered: continue
		musicVideos.append([firstTitle, photo])
	if type == 'browse':
		for firstTitle, photo in musicVideos:
			count += 1
			name = '[COLOR chartreuse]'+str(count)+' •  [/COLOR]'+firstTitle
			addLink(name, photo, {'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')})
		try:
			nextPage = response['next']
			if 'https://api.deezer.com/' in nextPage:
				addAutoPlayDir(translation(30803), artpic+'nextpage.png', {'mode': 'listDeezerVideos', 'url': nextPage, 'extras': photo})
		except: pass
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(limit) > 0:
			musicVideos = musicVideos[:int(limit)]
		random.shuffle(musicVideos)
		for firstTitle, photo in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playYTByTitle', 'url': firstTitle.replace(' - ', ' ')}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': photo, 'poster': photo})
			listitem.setProperty('IsPlayable', 'true')
			playlist.add(endUrl, listitem)
		xbmc.Player().play(playlist)

def getYoutubeId(query):
	query = quote_plus(query.lower()).replace('%5B', '').replace('%5D', '').replace('%28', '').replace('%29', '').replace('%2F', '')
	VIDEOexAUDIO = False
	COMBI_VIDEO = []
	content = getCache('https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=5&order=relevance&q={0}&key={1}'.format(query, myTOKEN))
	response = json.loads(content)
	for item in response['items']:
		if item.get('id', {}).get('kind', '') == 'youtube#video':
			title = cleaning(item['snippet']['title'])
			IDD = str(item['id']['videoId'])
			COMBI_VIDEO.append([title, IDD])
	if COMBI_VIDEO:
		parts = COMBI_VIDEO[:]
		matching = [s for s in parts if not 'audio' in s[0].lower()]
		if matching:
			VIDEOexAUDIO = matching[0][1]
		else:
			VIDEOexAUDIO = parts[0][1]
	else:
		return dialog.notification(translation(30521).format('VIDEO'), translation(30525), icon, 8000)
	return VIDEOexAUDIO

def playYTByTitle(title):
	youtubeID = getYoutubeId('official '+title)
	finalURL = 'plugin://plugin.video.youtube/play/?video_id='+youtubeID
	xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=finalURL))
	xbmc.sleep(1000)
	if addon.getSetting('showInfo') == 'true': infoMessage()

def infoMessage():
	count = 0
	while not xbmc.Player().isPlaying():
		xbmc.sleep(200)
		if count == 50:
			break
		count += 1
	xbmc.sleep(infoDelay*1000)
	if xbmc.Player().isPlaying() and infoType == '0':
		xbmc.sleep(1500)
		xbmc.executebuiltin('ActivateWindow(12901)')
		xbmc.sleep(infoDuration*1000)
		xbmc.executebuiltin('ActivateWindow(12005)')
		xbmc.sleep(500)
		xbmc.executebuiltin('Action(Back)')
	elif xbmc.Player().isPlaying() and infoType == '1':
		xbmc.getInfoLabel('Player.Title')
		xbmc.getInfoLabel('Player.Duration')
		xbmc.getInfoLabel('Player.Art(thumb)')
		xbmc.sleep(500)
		title = xbmc.getInfoLabel('Player.Title')
		relTitle = cleaning(title)
		if relTitle.isupper() or relTitle.islower():
			relTitle = TitleCase(relTitle)
		runTime = xbmc.getInfoLabel('Player.Duration')
		photo = xbmc.getInfoLabel('Player.Art(thumb)')
		xbmc.sleep(1000)
		dialog.notification(translation(30804), relTitle+'[COLOR blue]  * '+runTime+' *[/COLOR]', photo, infoDuration*1000)
	else: pass

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=True)

def addAutoPlayDir(name, image, params={}):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Mediatype': 'musicvideo'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	entries = []
	entries.append([translation(30831), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play'}))])
	entries.append([translation(30832), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '10'}))])
	entries.append([translation(30833), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '20'}))])
	entries.append([translation(30834), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '30'}))])
	entries.append([translation(30835), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '40'}))])
	entries.append([translation(30836), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '50'}))])
	liz.addContextMenuItems(entries, replaceItems=False)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=True)

def addLink(name, image, params={}, plot=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Mediatype': 'musicvideo'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	liz.setProperty('IsPlayable', 'true')
	liz.addContextMenuItems([(translation(30805), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)')])
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)

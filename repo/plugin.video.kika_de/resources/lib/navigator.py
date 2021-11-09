# -*- coding: utf-8 -*-

import sys
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import hashlib
import time
import _strptime
from datetime import datetime, timedelta
import threading
import traceback
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode  # Python 2.X
	from urllib2 import urlopen  # Python 2.X
else: 
	from urllib.parse import urlencode  # Python 3.X
	from urllib.request import urlopen  # Python 3.X
	from functools import reduce  # Python 3.X

from .common import *


if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def mainMenu():
	if Newest: addDir(translation(30601), icon, {'mode': 'listEpisodes', 'url': BASE_API+'/api/videos?offset=0&limit=100&orderBy=appearDate&orderDirection=desc', 'extras': 'experimental'})
	if Mostviewed: addDir(translation(30602), icon, {'mode': 'listEpisodes', 'url': BASE_API+'/api/videos?offset=0&limit=100&orderBy=viewCount&orderDirection=desc', 'extras': 'experimental'})
	if kikaninchen: addDir(translation(30603), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/kikaninchen/sendungen/videos-kikaninchen-100.html'})
	if sesamstrasse: addDir(translation(30604), icon, {'mode': 'listEpisodes', 'url': BASE_URL+'/sesamstrasse/sendungen/videos-sesamstrasse-100.html'})
	if since03: addDir(translation(30605), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/abdrei/videos-ab-drei-buendel100.html'})
	if since06: addDir(translation(30606), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/absechs/videosabsechs-buendel100.html'})
	if since10: addDir(translation(30607), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/abzehn/videosabzehn-buendel102.html'})
	if sinceAll: addDir(translation(30608), icon, {'mode': 'listAlphabet', 'url': BASE_URL+'/videos/allevideos/allevideos-buendelgruppen100.html'})
	addDir(translation(30609), artpic+'livestream.png', {'mode': 'playLIVE', 'url': BASE_URL+'/videos/livestream/msl4/hls-livestream-100.xml'}, folder=False)
	if enableADJUSTMENT:
		addDir(translation(30610), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive'):
			addDir(translation(30611), artpic+'settings.png', {'mode': 'iConfigs'}, folder=False)
	if not ADDON_operate('inputstream.adaptive'):
		addon.setSetting('useInputstream', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listAlphabet(url):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS("(navigator.listAlphabet) ------------------------------------------------ START = listAlphabet -----------------------------------------------")
	debug_MS("(navigator.listAlphabet) ### URL : {0} ###".format(url))
	content = getUrl(url, 'GET', url)
	result = re.findall(r'class="bundleNaviWrapper"(.+?)class="modCon"', content, re.S)[0]
	match = re.findall(r'<a href="([^"]+)" class="pageItem".*?>(.+?)</a>', result, re.S)
	for endURL, title in match:
		endURL = BASE_URL+endURL if endURL[:4] != "http" else endURL
		if title == '...': title = '#'
		debug_MS("(navigator.listAlphabet) XXX TITLE = {0} || endURL = {1} XXX".format(str(title), endURL))
		if '/kikaninchen/' in url:
			addDir(title, alppic+title.title()+'.png', {'mode': 'listEpisodes', 'url': endURL})
		else:
			addDir(title, alppic+title.title()+'.png', {'mode': 'listShows', 'url': endURL})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDAlphabet+')')

def listShows(url):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS("(navigator.listShows) ------------------------------------------------ START = listShows -----------------------------------------------")
	debug_MS("(navigator.listShows) ### URL : {0} ###".format(url))
	COMBI_FIRST, COMBI_LINKS, COMBI_SECOND = ([] for _ in range(3))
	counter = 0
	content = getUrl(url, 'GET', url)
	part = content.split('class="teaser teaserStandard  teaserMultigroup')
	for i in range(1, len(part), 1):
		entry = part[i]
		counter += 1
		img = re.findall(r"data-ctrl-image=.*?'urlScheme':'(.+?)'}", entry, re.S)[0].split('-resimage_v-')[0]+"-resimage_v-tlarge169_w-1280.jpg"
		img = BASE_URL+img if img[:4] != "http" else img
		match = re.findall(r'<h4 class="headline">.*?href="([^"]+)" title=.*?>([^<]+)</a>', entry, re.S)
		url2 = BASE_URL+match[0][0] if match[0][0][:4] != "http" else match[0][0]
		if BASE_URL+'/sendungen/' in url2.lower(): continue
		title = cleaning(match[0][1])
		if 'kikaninchen' in title.lower(): continue
		COMBI_FIRST.append([int(counter), title, img, url2])
		COMBI_LINKS.append(str(counter)+'@@'+url2)
	if COMBI_FIRST:
		debug_MS("(navigator.listShows) no.01 ### COMBI_FIRST = {0} ###".format(str(COMBI_FIRST)))
		COMBI_SECOND = getMultiData(COMBI_LINKS, 'SERIES')
		if COMBI_SECOND:
			RESULT = [a + [b[0]] + [b[1]] + [b[2]] for a in COMBI_FIRST for b in COMBI_SECOND if a[0] == b[0]]
			for da in sorted(RESULT, key=lambda k: k[0], reverse=False):
				NUM1, TITLE1, IMG1, LINK1, NUM2, SHORT2, LINK2 = da[0], da[1], da[2], da[3], da[4], da[5], da[6]
				debug_MS("(navigator.listShows) no.02 ### TITLE = {0} || endURL = {1} || PHOTO = {2} ###".format(str(TITLE1), LINK2, IMG1))
				addDir(TITLE1, IMG1, {'mode': 'listEpisodes', 'url': LINK2}, seriesname=TITLE1)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDShows+')')

def listEpisodes(url, extras):
	debug_MS("(navigator.listEpisodes) ------------------------------------------------ START = listEpisodes -----------------------------------------------")
	debug_MS("(navigator.listEpisodes) ### URL : {0} ###".format(url))
	COMBI_PAGES, COMBI_EPISODE = ([] for _ in range(2))
	Isolated = set()
	SingleENTRY = set()
	if extras == 'experimental':
		pos1 = 1
		pos2, pos3, pos4 = (0 for _ in range(3))
		html = getUrl(url, 'GET')
		DATA = json.loads(html)
		for item in DATA['_embedded']['items']:
			debug_MS("(navigator.listEpisodes) no.01 ### ITEM : {0} ###".format(str(item)))
			startTIMES, views = (None for _ in range(2))
			canPlay = 'true'
			seriesname = ""
			origTITLE, name = cleaning(item['title']), cleaning(item['title'])
			if '_embedded' in item and 'brand' in item['_embedded'] and item['_embedded']['brand'] != "" and item['_embedded']['brand'] != None:
				name, seriesname = cleaning(item['_embedded']['brand']['title']) + ' - ' + name, cleaning(item['_embedded']['brand']['title'])
			endURL = '{0}/api/videos/{1}/player-assets'.format(BASE_API, str(item['id']))
			photo = (item.get('largeTeaserImageUrl', '') or icon)
			plot = '[COLOR yellow]'+seriesname+'[/COLOR][CR]'
			views = item.get('viewCount', None)
			if item.get('appearDate', None): # 2020-05-08T07:45:00+02:00
				startDates = datetime(*(time.strptime(item['appearDate'][:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-13T13:30:00Z
				startTIMES = startDates.strftime('%d{0}%m{0}%Y {1} %H{2}%M').format('.', '•', ':')
			if startTIMES and views: plot += translation(30621).format(str(startTIMES), str(views))
			elif startTIMES and views is None: plot += translation(30622).format(str(startTIMES))
			plot += '[CR]'+cleaning(item['description'])
			duration = (item.get('duration', '0') or '0')
			episode = (item.get('episodeNumber', '0') or '0')
			pos4 += 1
			COMBI_EPISODE.append([pos1, episode, endURL, photo, canPlay, origTITLE, name, plot, duration, seriesname, pos2, pos3, pos4])
	else:
		pos1 = 0
		html = getUrl(url, 'GET', url)
		if '<div class="bundleNaviItem' in html and not 'kikaninchen' in url:
			NaviItem = re.findall(r'<div class="bundleNaviItem.*?href="([^"]+)" class="pageItem" title=.*?>([^<]+)</a>', html, re.S)
			for link, name in NaviItem:
				if link in Isolated:
					continue
				Isolated.add(link)
				pos1 += 1
				link = BASE_URL+link if link[:4] != "http" else link
				debug_MS("(navigator.listEpisodes) FIRST XXX POS = {0} || URL-2 = {1} XXX".format(str(pos1), link))
				if pos1 == Pagination: break
				COMBI_PAGES.append(str(pos1)+'@@'+link)
		else:
			pos1 += 1
			link = url
			debug_MS("(navigator.listEpisodes) SECOND XXX POS = {0} || URL-2 = {1} XXX".format(str(pos1), link))
			COMBI_PAGES.append(str(pos1)+'@@'+link)
		if COMBI_PAGES:
			COMBI_EPISODE = getMultiData(COMBI_PAGES, 'VIDEOS')
	if COMBI_EPISODE:
		playMARKER = ""
		SEND = {}
		SEND['videos'] = []
		if extras != 'experimental':
			for sign in COMBI_EPISODE:
				if sign[12] <= 5:
					COMBI_EPISODE = sorted(COMBI_EPISODE, key=lambda k: k[1], reverse=True)
				else:
					COMBI_EPISODE = sorted(COMBI_EPISODE, key=lambda k: (k[0], k[10]), reverse=False)
		for da in COMBI_EPISODE:
			NUM, EPIS, VID, PICT, CANPLAY, TITLE, NAME, DESC, DUR, SERIE, NUM2, NUM3, NUM4 = da[0], da[1], da[2], da[3], da[4], da[5], da[6], da[7], da[8], da[9], da[10], da[11], da[12]
			HLnom = hashlib.md5(py2_uni(VID).encode('utf-8')).hexdigest()
			if HLnom in SingleENTRY:
				continue
			SingleENTRY.add(HLnom)
			if CANPLAY == 'false' and Masking:
				continue
			elif not Masking: 
				playMARKER = '[COLOR lime]> [/COLOR]' if CANPLAY == 'true' else '[COLOR orangered]¤ [/COLOR]'
			listitem = xbmcgui.ListItem(playMARKER+NAME, path=HOST_AND_PATH+'?IDENTiTY='+HLnom+'&mode=playCODE')
			infos = {}
			infos['Episode'] = EPIS
			infos['Tvshowtitle'] = SERIE
			infos['Title'] = playMARKER+NAME
			infos['Tagline'] = None
			infos['Plot'] = DESC
			infos['Duration'] = DUR
			infos['Year'] = None
			infos['Genre'] = 'Kinder'
			infos['Director'] = None
			infos['Writer'] = None
			infos['Studio'] = 'KiKA'
			infos['Mpaa'] = None
			infos['Mediatype'] = 'episode'
			listitem.setInfo(type='Video', infoLabels=infos)
			listitem.setArt({'icon': icon, 'thumb': PICT, 'poster': PICT, 'fanart': defaultFanart})
			if PICT and useThumbAsFanart and PICT != icon and not artpic in PICT:
				listitem.setArt({'fanart': PICT})
			listitem.addStreamInfo('Video', {'Duration': DUR})
			listitem.setProperty('IsPlayable', 'true')
			listitem.addContextMenuItems([(translation(30654), 'RunPlugin('+HOST_AND_PATH+'?mode=AddToQueue)')])
			xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=HOST_AND_PATH+'?IDENTiTY='+HLnom+'&mode=playCODE', listitem=listitem)
			SEND['videos'].append({'url': VID, 'tvshow': SERIE, 'filter': HLnom, 'name': NAME, 'pict': PICT, 'cycle': DUR, 'episode': EPIS})
		with open(WORKFILE, 'w') as ground:
			json.dump(SEND, ground, indent=4, sort_keys=True)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')

def getXmlUrlForEpisode(url):
	debug_MS("(navigator.getXmlUrlForEpisode) ### EPISODE-URL = {0} ###".format(url))
	content = '0'
	chtml = getUrl(url, 'GET', url)
	testBLOCK = re.compile(r'<div class="section sectionA sectionAfterContent">(.+?)<div class="mediaInfo">', re.S).findall(chtml)
	if testBLOCK:
		data = re.search('dataURL:\'(https?://.*?.xml)', testBLOCK[0], re.S)
		if data:
			debug_MS("(navigator.getXmlUrlForEpisode) ### [XML] xmlUrl : {0} ###".format(data.group(1)))
			content = getUrl(data.group(1), 'GET', data.group(1))
	return content

def playCODE(IDD):
	debug_MS("(navigator.playCODE) ------------------------------------------------ START = playCODE -----------------------------------------------")
	debug_MS("(navigator.playCODE) ### IDD : {0} ###".format(str(IDD)))
	Xml_QUALITIES = ['1920x1080', '1280x720', '1024x576', '960x540', '852x480', '720x576', '640x360', '512x288', '480x272', '480x270', '320x180', '320x176']
	All_QUALITIES = [4, 3, 2, 1, 0, 'hd', 'veryhigh', 'high', 'med', 'low', '1920x1080', '1280x720', '1024x576', '960x540', '852x480', '720x576', '640x360', '512x288', '480x272', '480x270', '320x180', '320x176']
	BestLISTING, M3U8_Url, newPLOT = ("" for _ in range(3))
	convToNumbers = resToAutoSelect.replace('HIGH', '3').replace('GOOD', '2').replace('MEDIUM', '1').replace('LOW', '0')
	convToNames = resToAutoSelect.replace('HIGH', 'veryhigh').replace('GOOD', 'high').replace('MEDIUM', 'med').replace('LOW', 'low')
	MEDIAS = []
	finalURL = False
	with open(WORKFILE, 'r') as wok:
		ARRIVE = json.load(wok)
		for elem in ARRIVE['videos']:
			if elem['filter'] == IDD:
				endURL = elem['url']
				seriesname = py2_enc(elem['tvshow'])
				name = py2_enc(elem['name'])
				image = elem['pict']
				duration = elem['cycle']
				episode = elem['episode']
	if 'api/videos' in endURL:
		debug_MS("(navigator.playCODE) ### [API] apiUrl : {0} ###".format(endURL))
		content = getUrl(endURL, 'GET')
		DATA = json.loads(content)
		for entry in DATA['assets']:
			if entry.get('quality').lower() == 'auto' and 'm3u8' in entry.get('url'):
				M3U8_Url = entry.get('url')
		for item in DATA['hbbtvAssets']:
			MP4 = item['url']
			TYPE = (item.get('delivery', 'Unknown') or 'Unknown')
			try: QUAL = item.get('quality').split('|')[-1].strip()
			except: QUAL = item.get('quality')
			MEDIAS.append({'url': MP4, 'delivery': TYPE, 'quality': QUAL, 'document': 'API_URL'})
	else:
		xmlUrl = getXmlUrlForEpisode(endURL)
		if xmlUrl != '0':
			TVS = re.compile(r'<topline>([^<]+)</topline>', re.S).findall(xmlUrl)
			TTL = re.compile(r'<title>([^<]+)</title>', re.S).findall(xmlUrl)
			if TVS and TTL: newPLOT = '[COLOR yellow]'+cleaning(TVS[0])+'[CR]'+cleaning(TTL[0])+'[/COLOR][CR][CR]'
			DESC = re.compile(r'<teaserText>([^<]+)</teaserText>', re.S).findall(xmlUrl)
			if DESC: newPLOT += cleaning(DESC[0])
			M3U8_Url = re.findall(r'<asset>.*?<adaptiveHttpStreamingRedirectorUrl>([^<]+)</adaptiveHttpStreaming.*?</asset>', xmlUrl, re.S)[-1]
			part = xmlUrl.split('<asset>')
			for i in range(1, len(part), 1):
				entry = part[i]
				PROFIL = py2_enc(re.findall(r'<profileName>([^<]+)</profileName>', entry, re.S)[0])
				try: PROFIL = PROFIL.split('|')[-1].replace('quality =', '').strip()
				except: PROFIL = PROFIL
				MP4 = re.findall(r'<progressiveDownloadUrl>([^<]+)</progressive', entry, re.S)[0]
				MEDIAS.append({'url': MP4, 'delivery': 'progressive', 'quality': PROFIL, 'document': 'XML_URL'})
	if MEDIAS:
		debug_MS("(navigator.playCODE) ORIGINAL_TV['media'] ### unsorted_LIST : {0} ###".format(str(MEDIAS)))
		order_dict = {qual: index for index, qual in enumerate(All_QUALITIES)}
		BestLISTING = sorted(MEDIAS, key=lambda x: order_dict.get(x['quality'], float('inf')))
		debug_MS("(navigator.playCODE) SORTED_BestLISTING ### sorted_LIST : {0} ###".format(str(BestLISTING)))
	if (prefSTREAM == '0' or enableINPUTSTREAM) and M3U8_Url != "":
		debug_MS("(navigator.playCODE) no.01 ~~~~~ FIRST TRY TO GET THE FINALURL (m3u8) ~~~~~")
		finalURL = M3U8_Url
	if not finalURL and BestLISTING != "" and resToAutoSelect != 'BESTEVER':
		debug_MS("(navigator.playCODE) no.02 ~~~~~ SECOND TRY TO GET THE FINALURL (mp4) ~~~~~")
		for elem in BestLISTING:
			convQuality = str(elem['quality']).replace('1920x1080', 'HIGH').replace('1280x720', 'HIGH').replace('1024x576', 'GOOD').replace('960x540', 'GOOD').replace('852x480', 'MEDIUM').replace('720x576', 'MEDIUM').replace('640x360', 'LOW').replace('512x288', 'LOW')
			if ((resToAutoSelect == convQuality) or (convToNumbers == str(elem['quality'])) or (convToNames == str(elem['quality']))):
				MP4_Url = elem.get('url')
				MP4_Url = 'https:'+MP4_Url if MP4_Url[:4] != "http" else MP4_Url
				debug_MS("(navigator.playCODE) XXX [{0}] Quality-Title = {1} || bevorzugte-URL = {2} XXX".format(elem['document'], str(elem['quality']), elem['url']))
				finalURL = VideoBEST(MP4_Url) if resToAutoSelect == 'HIGH' else MP4_Url # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	if not finalURL and BestLISTING != "":
		debug_MS("(navigator.playCODE) no.03 ~~~~~ THIRD TRY TO GET THE FINALURL (mp4) ~~~~~")
		MP4_Url = BestLISTING[0]['url']
		MP4_Url = 'https:'+MP4_Url if MP4_Url[:4] != "http" else MP4_Url
		debug_MS("(navigator.playCODE) XXX [{0}] Highest-Quality = {1} || Highest-URL = {2} XXX".format(BestLISTING[0]['document'], str(BestLISTING[0]['quality']), MP4_Url))
		finalURL = VideoBEST(MP4_Url) # *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	if finalURL:
		log("(navigator.playCODE) StreamURL : {0}".format(finalURL))
		listitem = xbmcgui.ListItem(path=finalURL)
		if newPLOT != "":
			newEPIS = episode if episode != '0' else ""
			listitem.setInfo(type='Video', infoLabels={'Title': name, 'Tvshowtitle': seriesname, 'Plot': newPLOT, 'Episode': newEPIS, 'Duration': duration, 'Studio': 'KiKA', 'Mediatype': 'episode'})
			listitem.setArt({'icon': icon, 'thumb': image, 'poster': image})
		if enableINPUTSTREAM and ADDON_operate('inputstream.adaptive') and 'm3u8' in finalURL:
			listitem.setProperty(INPUT_APP, 'inputstream.adaptive')
			listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
			listitem.setMimeType('application/vnd.apple.mpegurl')
		xbmcplugin.setResolvedUrl(ADDON_HANDLE,True, listitem)
	else:
		failing("(navigator.playCODE) ##### Abspielen des Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Stream-Eintrag auf der Webseite von *kika.de* gefunden !!! ##########".format(endURL))
		return dialog.notification(translation(30521).format('STREAM'), translation(30523), icon, 8000)

def playLIVE(url):
	debug_MS("(navigator.playLIVE) ------------------------------------------------ START = playLIVE -----------------------------------------------")
	liveURL = False
	MEDIAS = []
	content = getUrl(url, 'GET', url)
	part = content.split('<asset>')
	for i in range(1, len(part), 1):
		entry = part[i]
		if '<geoZone>DE</geoZone>' in entry:
			liveURL = re.findall(r'<adaptiveHttpStreamingRedirectorUrl>([^<]+)</adaptive', entry, re.S)
	if liveURL:
		firstRESULT = re.sub(r'(?:chunklist.m3u8|playlist.m3u8|index.m3u8|master.m3u8)', '', liveURL[0])
		STREAMTEXT = getUrl(liveURL[0], 'GET')
		STREAMS = STREAMTEXT.splitlines()
		for i in range(0, len(STREAMS)):
			infoSTREAM = STREAMS[i]
			if 'INF:BANDWIDTH=' in infoSTREAM:
				try: 	the_Bandwith = re.findall(r'AVERAGE-BANDWIDTH=([0-9]+),', infoSTREAM, re.S)[0]
				except: the_Bandwith = re.findall(r'INF:BANDWIDTH=([0-9]+),', infoSTREAM, re.S)[0]
				converted_BW = int(the_Bandwith)/1024
				onlyLeft_BW = "{0:.0f}".format(converted_BW).zfill(5)
				newSTREAM = STREAMS[i + 1]
				MEDIAS.append({'url': newSTREAM, 'bandwith': str(onlyLeft_BW), 'type': 'hls-m3u8'})
		debug_MS("(navigator.playLIVE) MEDIAS ### unsorted_LIST = {0} ###".format(str(MEDIAS)))
		MEDIAS = sorted(MEDIAS, key=lambda k: k['bandwith'], reverse=True)
		finalURL = firstRESULT+MEDIAS[0]['url']
		log("(navigator.playLIVE) liveURL : {0}".format(finalURL))
		listitem = xbmcgui.ListItem(path=finalURL, label=translation(30609))
		listitem.setMimeType('application/vnd.apple.mpegurl')
		xbmc.Player().play(item=finalURL, listitem=listitem)
	else:
		failing("(navigator.playLIVE) ##### Abspielen des Live-Streams NICHT möglich ##### URL : {0} #####\n   ########## KEINEN Live-Stream-Eintrag auf der Webseite von *kika.de* gefunden !!! ##########".format(url))
		return dialog.notification(translation(30521).format('LIVE'), translation(30524), icon, 8000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def VideoBEST(best_url):
	standards = [best_url, "", ""]
	first_repls = (('808k_p11v15', '2360k_p35v15'), ('1628k_p13v15', '2360k_p35v15'), ('1456k_p13v12', '2328k_p35v12'), ('1496k_p13v13', '2328k_p35v13'), ('1496k_p13v14', '2328k_p35v14'),
							('2256k_p14v11', '2328k_p35v11'), ('2256k_p14v12', '2328k_p35v12'), ('2296k_p14v13', '2328k_p35v13'), ('2296k_p14v14', '2328k_p35v14'))
	second_repls = (('2328k_p35v12', '3328k_p36v12'), ('2328k_p35v13', '3328k_p36v13'), ('2328k_p35v14', '3328k_p36v14'), ('2360k_p35v15', '3360k_p36v15'))
	standards[1] = reduce(lambda a, kv: a.replace(*kv), first_repls, standards[0])
	standards[2] = reduce(lambda b, kv: b.replace(*kv), second_repls, standards[1])
	for element in reversed(standards):
		if len(element) > 0:
			try:
				code = urlopen(element).getcode()
				if str(code) == "200":
					return element
			except: pass
	return best_url

COMBI_OUTPUT = []
pill2kill = threading.Event()
def listSubstances(parts, pill2kill, course):
	num = parts.split('@@')[0]
	elem = parts.split('@@')[1]
	if not pill2kill.is_set():
		try:
			if course == 'SERIES':
				endURL = elem
				shorten = 'NOT WANTED URL-ELEMENT'
				if '/sendungen/videos' in elem:
					shorten = elem.split('/sendungen/videos')[0]+'/index.html'
					testing = getUrl(shorten, 'GET', elem)
					buendel = re.search(r'<a href=.*?(/[a-z-]+/buendelgruppe[0-9]+.html)" title=', testing, re.S)
					if buendel:
						endURL = BASE_URL+buendel.group(1) if buendel.group(1)[:4] != "http" else buendel.group(1)
				COMBI_OUTPUT.append([int(num), shorten, endURL])
			elif course == 'VIDEOS':
				pos2, pos3, pos4 = (0 for _ in range(3))
				startURL = elem
				result = getUrl(elem, 'GET', elem)
				if not 'index' in startURL:
					content = re.findall(r'<!--Header Area for the Multigroup -->(.+?)<!--The bottom navigation -->', result, re.S)[0]
				else:
					content = re.findall(r'<h2 class="conHeadline">Neue Videos</h2>(.+?)<span class="linktext">Alle Videos</span>', result, re.S)[0]
				part = content.split('class="teaser teaserStandard')
				for i in range(1, len(part), 1):
					entry = part[i]
					debug_MS("(navigator.listSubstances) no.01 ### ENTRY : {0} ###".format(str(entry)))
					photo, plot, seriesname = ("" for _ in range(3))
					season, episode, duration = ('0' for _ in range(3))
					canPlay = 'true'
					image = re.compile(r"data-ctrl-image=.*?'urlScheme':'(.+?)'}", re.S).findall(entry)
					if image:
						photo = image[0].split('-resimage_v-')[0]+'-resimage_v-tlarge169_w-1280.jpg'
						photo = BASE_URL+photo if photo[:4] != "http" else photo
					playSYMBOL = re.compile(r'<span class="icon-font">(.+?)</span>', re.S).findall(entry)
					if playSYMBOL:
						canPlay = playSYMBOL[0].replace('&#xf01d;', 'true').replace('&#xe008;', 'false')
					endURL = re.compile(r'<h4 class="headline">.*?href="([^"]+)"', re.S).findall(entry)[0].replace('sendereihe', 'buendelgruppe')
					endURL = BASE_URL+endURL if endURL[:4] != "http" else endURL
					try: duration = get_Seconds(re.compile('<span class="icon-duration">(.+?)</span>', re.S).findall(entry)[0])
					except: pass
					if not 'index' in startURL:
						origSERIE = re.compile('<meta property="og:title" content="(.+?)"/>', re.S).findall(result)
						if origSERIE:
							plot = '[COLOR yellow]'+cleaning(origSERIE[0])+'[/COLOR]'
							seriesname = cleaning(origSERIE[0]) if not 'Filme' in origSERIE[0] else 'Filme'
					first = re.compile(r'(?:class="linkAll js-broadcast-link"|class="linkAll") title="([^"]+)"', re.S).findall(entry)
					second= re.compile(r'<p class="dachzeile">.*?title=.*?>([^<]+)</a>',re.S).findall(entry)
					text = re.compile(r'<img title=.*?alt="([^"]+?)"', re.S).findall(entry)
					if first and not second:
						origTITLE, name = cleaning(first[0]), cleaning(first[0])
					elif first and second:
						origTITLE = cleaning(first[0])
						if not 'index' in startURL:
							name = cleaning(first[0])
							if Dating and ('Folge' in second[0] or 'buendelgruppe' in startURL):
								name = cleaning(first[0])+'   [COLOR deepskyblue]('+cleaning(second[0]).split(',')[0]+')[/COLOR]'
						else:
							name = cleaning(second[0])+' - '+cleaning(first[0])
							seriesname = cleaning(second[0]) if not 'Filme' in second[0] else 'Filme'
							plot = '[COLOR yellow]'+cleaning(second[0])+'[/COLOR]'
					if text:
						if not 'index' in startURL:
							plot += '[CR][CR]'+cleaning(text[0])
						elif 'index' in startURL and second:
							plot = '[COLOR yellow]'+cleaning(second[0])+'[/COLOR][CR][CR]'+cleaning(text[0])
					pos2 += 1
					if origTITLE[:1].isdigit() or 'Folge ' in origTITLE:
						try:
							episode = re.findall('([0-9]+)', origTITLE, re.S)[0].strip().zfill(4)
							pos3 += 1
						except: pass
					else: pos4 += 1
					COMBI_OUTPUT.append([int(num), episode, endURL, photo, canPlay, origTITLE, name, plot, duration, seriesname, pos2, pos3, pos4])
		except:
			stopping()
			formatted_lines = traceback.format_exc().splitlines()
			failing("(navigator.listSubstances) ERROR - ERROR - ERROR :\n{0} \n{1} \n{2}".format(formatted_lines[1], formatted_lines[2], formatted_lines[3]))

def stopping():
	pill2kill.set()

def getMultiData(simultan, event='VIDEOS'):
	debug_MS("(navigator.getMultiData) ------------------------------------------------ START = getMultiData -----------------------------------------------")
	threads = []
	debug_MS("(navigator.getMultiData) ganze LISTE XXXXX {0} XXXXX".format(' || '.join(simultan)))
	for article in simultan:
		th = threading.Thread(target=listSubstances, args=[article, pill2kill, event])
		if hasattr(th, 'daemon'): th.daemon = True
		else: th.setDaemon()
		threads.append(th)
	[th.start() for th in threads]
	threading.Timer(25, after_timeout, [threads, pill2kill]).start()
	[th.join(3) for th in threads]
	if COMBI_OUTPUT:
		debug_MS("(navigator.listSubstances) Ergebnis XXXXX COMBI_OUTPUT = {0} XXXXX".format(str(COMBI_OUTPUT)))
	return COMBI_OUTPUT

def after_timeout(threads, pill2kill):
	position = 0
	for th in threads:
		if th.is_alive() and position == 0:
			position += 1
			failing("(navigator.after_timeout) TIMEOUT ##### !!! DIE MAX. ZEIT FÜR THREADS IST ABGELAUFEN - KILLING THEM ALL !!! #####")
			stopping()
	return

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, seriesname="", folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Tvshowtitle': seriesname, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image and useThumbAsFanart and image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

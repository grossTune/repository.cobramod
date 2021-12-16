# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import json
import xbmcvfs
import shutil
import time
import _strptime
from datetime import datetime, timedelta
import requests
import io
import threading
from collections import OrderedDict
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote_plus  # Python 2.X
else: 
	from urllib.parse import urlencode, quote_plus  # Python 3.X
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .common import *


def getHTML(url, cookies=None, allow_redirects=True, stream=None, data=None, json=None):
	simple = requests.Session()
	try:
		response = simple.get(url, headers={'User-Agent': get_userAgent()}, allow_redirects=allow_redirects, verify=verify_ssl_connect, stream=stream, timeout=30).text
		response = py2_enc(response)
	except requests.exceptions.RequestException as e:
		failure = str(e)
		failing("(mediatools.getHTML) ERROR - ERROR - ERROR : ##### {0} === {1} #####".format(url, failure))
		dialog.notification(translation(30521).format('URL'), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
		return sys.exit(0)
	return response

def preparefiles(url, name, XTRA, rotation):
	debug_MS("(mediatools.preparefiles) -------------------------------------------------- START = tolibrary --------------------------------------------------")
	if mediaPath =="":
		return dialog.ok(addon_id, translation(30508))
	elif mediaPath !="" and ADDON_operate('service.cron.autobiblio'):
		title = name
		if XTRA != 'standard':
			title += '  ('+XTRA+')'
			url = url+'@@'+XTRA.replace('Jahr ', '')
			newSOURCE = quote_plus(mediaPath+fixPathSymbols(name)+os.sep+XTRA)
		else:
			title += '  (Serie)'
			newSOURCE = quote_plus(mediaPath+fixPathSymbols(name))
		newURL = '{0}?mode=generatefiles&url={1}&name={2}'.format(sys.argv[0], url, name)
		newNAME, newURL = quote_plus(name), quote_plus(newURL)
		debug_MS("(mediatools.preparefiles) ### newNAME : {0} ###".format(str(newNAME)))
		debug_MS("(mediatools.preparefiles) ### newURL : {0} ###".format(str(newURL)))
		debug_MS("(mediatools.preparefiles) ### newSOURCE : {0} ###".format(str(newSOURCE)))
		xbmc.executebuiltin('RunPlugin(plugin://service.cron.autobiblio/?mode=adddata&name={0}&stunden={1}&url={2}&source={3})'.format(newNAME, rotation, newURL, newSOURCE))
		return dialog.notification(translation(30571), translation(30572).format(title, str(rotation)), icon, 15000)

def generatefiles(url, name):
	debug_MS("(mediatools.generatefiles) -------------------------------------------------- START = generatefiles --------------------------------------------------")
	th = threading.Thread(target=LIBRARY_Worker, args=(url, name))
	th.daemon = True
	th.start()

def LIBRARY_Worker(BroadCast_Idd, BroadCast_Name):
	debug_MS("(mediatools.LIBRARY_Worker) ### BroadCast_Idd = {0} ### BroadCast_Name = {1} ###".format(BroadCast_Idd, BroadCast_Name))
	if not enableLIBRARY or mediaPath =="":
		return
	COMBINATION = []
	pos_ESP = 0
	elem_IDD = BroadCast_Idd
	if '@@' in BroadCast_Idd: elem_IDD = BroadCast_Idd.split('@@')[0]
	url_1 = API_URL+'/formats/'+str(elem_IDD)+'?fields=[%22id%22,%22title%22,%22station%22,%22hasFreeEpisodes%22,%22seoUrl%22,%22seoText%22,%22tabSeason%22,%22formatimageArtwork%22,%22formatimageMoviecover169%22,%22genre1%22,%22genres%22,%22categoryId%22,%22infoText%22,%22infoTextLong%22,%22onlineDate%22,%22annualNavigation%22,%22seasonNavigation%22]'
	debug_MS("(mediatools.LIBRARY_Worker) ##### URL-01 : {0} #####".format(str(url_1)))
	TVS_Path = os.path.join(py2_uni(mediaPath), py2_uni(fixPathSymbols(BroadCast_Name)))
	if '@@' in BroadCast_Idd: 
		suffixPath = BroadCast_Idd.split('@@')[1]
		EP_Path = os.path.join(py2_uni(mediaPath), py2_uni(fixPathSymbols(BroadCast_Name)), str(suffixPath))
	else:
		EP_Path = os.path.join(py2_uni(mediaPath), py2_uni(fixPathSymbols(BroadCast_Name)))
	debug_MS("(mediatools.LIBRARY_Worker) ### EP_Path = {0} ###".format(str(EP_Path)))
	if os.path.isdir(EP_Path):
		shutil.rmtree(EP_Path, ignore_errors=True)
		xbmc.sleep(500)
	if xbmcvfs.exists(os.path.join(TVS_Path, 'tvshow.nfo')):
		xbmcvfs.delete(os.path.join(TVS_Path, 'tvshow.nfo'))
		xbmc.sleep(500)
	xbmcvfs.mkdirs(EP_Path)
	try:
		content_1 = getHTML(url_1)
		SHOW_DATA = json.loads(content_1, object_pairs_hook=OrderedDict)
		TVS_name = cleaning(SHOW_DATA['title'])
	except: return
	SERIES_IDD = str(SHOW_DATA['id'])
	TVS_studio, TVS_image, TVS_airdate = ("" for _ in range(3))
	TVS_studio = (SHOW_DATA.get('station', '').upper() or "")
	TVS_image = (cleanPhoto(SHOW_DATA.get('formatimageMoviecover169', '')) or cleanPhoto(SHOW_DATA.get('formatimageArtwork', '')) or IMG_series.replace('{FID}', SERIES_IDD))
	TVS_plot = get_Description(SHOW_DATA, 'TVS')
	if str(SHOW_DATA.get('onlineDate'))[:4] not in ['', 'None', '0', '1970']:
		TVS_airdate = str(SHOW_DATA['onlineDate'])[:10]
	EP_PAGE, EP_position, EP_total = (1 for _ in range(3))
	if '@@' in BroadCast_Idd:
		elem_SUFFIX = BroadCast_Idd.split('@@')[1]
		if len(elem_SUFFIX) == 4:
			url_2 = API_URL+'/movies?filter={%22BroadcastStartDate%22:{%22between%22:{%22start%22:%22'+elem_SUFFIX+'-01-01%2000:00:00%22,%22end%22:%22'+elem_SUFFIX+'-12-31%2023:59:59%22}},%22FormatId%22:'+SERIES_IDD+'}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=200'
		elif 'Staffel ' in elem_SUFFIX:
			url_2 = API_URL+'/movies?filter={%22Season%22:'+elem_SUFFIX.split('Staffel ')[1]+',%22FormatId%22:'+SERIES_IDD+'}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=200'
	else:
		url_2 = API_URL+'/movies?filter={%22FormatId%22:'+SERIES_IDD+'}&fields=[%22id%22,%22title%22,%22broadcastStartDate%22,%22articleShort%22,%22articleLong%22,%22teaserText%22,%22seoUrl%22,%22season%22,%22episode%22,%22duration%22,%22isDrm%22,%22free%22,%22payed%22,%22fsk%22,%22productionYear%22,%22format%22,[%22id%22,%22title%22,%22station%22,%22seoUrl%22,%22formatImageClear%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22,%22formatType%22],%22manifest%22,[%22dash%22,%22dashhd%22]]&maxPerPage=200'
	debug_MS("(mediatools.LIBRARY_Worker) ##### URL-02 : {0} #####".format(str(url_2)))
	while (EP_total > 0):
		newURL = url_2+'&page='+str(EP_PAGE)
		debug_MS("(mediatools.LIBRARY_Worker) ### newURL : {0} ###".format(newURL))
		content_2 = getHTML(newURL)
		EPIS_DATA = json.loads(content_2, object_pairs_hook=OrderedDict)
		if EPIS_DATA.get('movies', '') and EPIS_DATA.get('movies', {}).get('items', ''):
			items = EPIS_DATA['movies']['items']
		else: items = EPIS_DATA['items']
		for vid in items:
			debug_MS("(mediatools.LIBRARY_Worker) ##### VIDEO-Item : {0} #####".format(str(vid)))
			EP_tagline, Note_1, Note_2, Note_3, Note_4, Note_5, Note_6, EP_fsk, EP_yeardate, videoFREE, videoHD, EP_studio, EP_airdate = ("" for _ in range(13))
			EP_season, EP_episode, EP_duration = ('0' for _ in range(3))
			spezTIMES, normTIMES = (None for _ in range(2))
			EP_genreLIST = []
			try:
				broadcast = datetime(*(time.strptime(vid['broadcastStartDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
				spezTIMES = broadcast.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':').replace('Mon', translation(32101)).replace('Tue', translation(32102)).replace('Wed', translation(32103)).replace('Thu', translation(32104)).replace('Fri', translation(32105)).replace('Sat', translation(32106)).replace('Sun', translation(32107))
				normTIMES = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			except: pass
			EP_protect = (vid.get('isDrm', False) or False)
			EP_idd = str(vid['id'])
			try: TVS_title = cleaning(vid['format']['title'])
			except: 
				try: TVS_title = cleaning(vid['format']['seoUrl']).replace('-', ' ').title()
				except: continue
			EP_title1 = cleaning(vid['title'])
			pos_ESP += 1
			if vid.get('season', ''):
				EP_season = str(vid['season']).zfill(2)
			if vid.get('episode', ''):
				EP_episode = str(vid['episode']).replace('P', '').zfill(2)
			if vid.get('duration', ''):
				EP_duration = get_Time(vid['duration'], 'MINUTES')
			EP_tagline = (cleaning(vid.get('teaserText', '') or ""))
			EP_description = get_Description(vid)
			if TVS_title !="": Note_1 = TVS_title
			if EP_season != '0' and EP_episode != '0': Note_3 = translation(30624).format(EP_season, EP_episode)
			if spezTIMES: Note_4 = translation(30625).format(str(spezTIMES))
			if showDATE and normTIMES:
				Note_5 = translation(30626).format(str(normTIMES))
			if str(vid.get('fsk')).isdigit():
				EP_fsk = translation(30627).format(str(vid['fsk'])) if str(vid.get('fsk')) != '0' else translation(30628)
			if str(vid.get('productionYear'))[:4].isdigit() and str(vid.get('productionYear'))[:4] not in ['0', '1970']:
				EP_yeardate = str(vid['productionYear'])[:4]
			EP_payed = (vid.get('payed', True) or vid.get('free', True))
			if vid.get('manifest', ''):
				if vid.get('manifest', {}).get('dash', ''): # Normal-Play
					videoFREE = vid['manifest']['dash'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net')
				if vid.get('manifest', {}).get('dashhd', ''): # HD-Play
					videoHD = vid['manifest']['dashhd'].replace('dash.secure.footprint.net', 'dash-a.akamaihd.net').split('.mpd')[0]+'.mpd'
			try: EP_deeplink = 'https://www.tvnow.de/'+vid['format']['formatType'].replace('show', 'shows').replace('serie', 'serien').replace('film', 'filme')+'/'+cleaning(vid['format']['seoUrl'])+'-'+str(vid['format']['id'])
			except: EP_deeplink =""
			EP_image = IMG_movies.replace('{MID}', EP_idd)
			if vid.get('format', ''):
				EP_studio = (vid.get('format', {}).get('station', '').upper() or "")
				if vid.get('format', {}).get('genres', ''):
					EP_genreLIST = [cleaning(item) for item in vid.get('format', {}).get('genres', '')]
					if EP_genreLIST: EP_genreLIST = sorted(EP_genreLIST)
			try: EP_genre1 = EP_genreLIST[0]
			except: EP_genre1 = ""
			try: EP_genre2 = EP_genreLIST[1]
			except: EP_genre2 = ""
			try: EP_genre3 = EP_genreLIST[2]
			except: EP_genre3 = ""
			if (not KODI_ov18 and EP_protect is True and EP_payed is False):
				Note_2 = '   [COLOR skyblue](premium|[/COLOR][COLOR orangered]DRM)[/COLOR]'
				Note_6 = '     [COLOR deepskyblue](premium|[/COLOR][COLOR orangered]DRM)[/COLOR]'
			elif (not KODI_ov18 and EP_protect is True and EP_payed is True):
				Note_2 = '   [COLOR orangered](DRM)[/COLOR]'
				Note_6 = '     [COLOR orangered](DRM)[/COLOR]'
			elif (KODI_17 or KODI_ov18) and EP_payed is False and vodPremium is False:
				Note_2 = '   [COLOR skyblue](premium)[/COLOR]'
				Note_6 = '     [COLOR deepskyblue](premium)[/COLOR]'
			EP_plot = Note_1+Note_2+'[CR]'+Note_3+Note_4+'[CR][CR]'+EP_description
			EP_title_long = EP_title1+Note_5+Note_6
			EP_airdate = (str(vid.get('broadcastStartDate', ''))[:10] or str(vid.get('broadcastPreviewStartDate', ''))[:10] or "")
			if EP_season != '0' and EP_episode != '0':
				EP_title = 'S'+EP_season+'E'+EP_episode+'_'+EP_title1
			else:
				EP_episode = str(pos_ESP).zfill(2)
				EP_title = 'S00E'+EP_episode+'_'+EP_title1
			EP_COMPLETE_EXTRAS = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playDash', 'xnormSD': videoFREE, 'xhighHD': videoHD, 'xcode': EP_idd, 'xlink': EP_deeplink, 'xdrm': EP_protect, 'xstat': EP_payed}))
			episodeFILE = py2_uni(fixPathSymbols(EP_title))
			COMBINATION.append([episodeFILE, EP_title_long, TVS_title, EP_idd, EP_season, EP_episode, EP_plot, EP_tagline, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio, EP_COMPLETE_EXTRAS])
			EP_position += 1
		debug_MS("(mediatools.LIBRARY_Worker) Anzahl-in-Liste : {0}".format(str(int(EP_position)-1)))
		try:
			debug_MS("(mediatools.LIBRARY_Worker) Anzahl-auf-Webseite : {0}".format(str(EPIS_DATA['total'])))
			EP_total = EPIS_DATA['total'] - EP_position
		except: EP_total = 0
		EP_PAGE += 1
	if not xbmcvfs.exists(EP_Path):
		xbmcvfs.mkdirs(EP_Path)
	for episodeFILE, EP_title_long, TVS_title, EP_idd, EP_season, EP_episode, EP_plot, EP_tagline, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio, EP_COMPLETE_EXTRAS in COMBINATION:
		nfo_EPISODE_string = os.path.join(EP_Path, episodeFILE+'.nfo')
		with io.open(nfo_EPISODE_string, 'w', encoding='utf-8') as textobj_EP:
			textobj_EP.write(py2_uni(
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<episodedetails>
    <title>{0}</title>
    <showtitle>{1}</showtitle>
    <season>{2}</season>
    <episode>{3}</episode>
    <plot>{4}</plot>
    <tagline>{5}</tagline>
    <runtime>{6}</runtime>
    <thumb>{7}</thumb>
    <mpaa>{8}</mpaa>
    <genre clear="true">{9}</genre>
    <genre>{10}</genre>
    <genre>{11}</genre>
    <year>{12}</year>
    <aired>{13}</aired>
    <studio clear="true">{14}</studio>
</episodedetails>'''.format(EP_title_long, TVS_title, EP_season, EP_episode, EP_plot, EP_tagline, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio)))
		streamfile = os.path.join(EP_Path, episodeFILE+'.strm')
		debug_MS("(mediatools.LIBRARY_Worker) ##### streamFILE : {0} #####".format(cleaning(streamfile)))
		file = xbmcvfs.File(streamfile, 'w')
		file.write(EP_COMPLETE_EXTRAS)
		file.close()
	nfo_SERIE_string = os.path.join(TVS_Path, 'tvshow.nfo')
	with io.open(nfo_SERIE_string, 'w', encoding='utf-8') as textobj_TVS:
		textobj_TVS.write(py2_uni(
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<tvshow>
    <title>{0}</title>
    <showtitle>{0}</showtitle>
    <season></season>
    <episode></episode>
    <plot>{1}</plot>
    <thumb aspect="landscape" type="" season="">{2}</thumb>
    <fanart url="">
        <thumb dim="1280x720" colors="" preview="{2}">{2}</thumb>
    </fanart>
    <genre clear="true">{3}</genre>
    <genre>{4}</genre>
    <genre>{5}</genre>
    <year>{6}</year>
    <aired>{7}</aired>
    <studio clear="true">{8}</studio>
</tvshow>'''.format(TVS_name, TVS_plot, TVS_image, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, TVS_airdate, TVS_studio)))
	debug_MS("(mediatools.LIBRARY_Worker) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  ENDE = LIBRARY_Worker  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

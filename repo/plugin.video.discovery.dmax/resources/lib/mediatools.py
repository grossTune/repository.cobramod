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
import io
import threading
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import quote_plus  # Python 2.X
else: 
	from urllib.parse import quote_plus  # Python 3.X

from .common import *


def preparefiles(url, name, rotation):
	debug_MS("(mediatools.preparefiles) -------------------------------------------------- START = tolibrary --------------------------------------------------")
	if mediaPath =="":
		return dialog.ok(addon_id, translation(30502))
	elif mediaPath !="" and ADDON_operate('service.cron.autobiblio'):
		newURL = '{0}?mode=generatefiles&url={1}&name={2}'.format(sys.argv[0], url, name)
		newNAME, newURL = quote_plus(name), quote_plus(newURL)
		newSOURCE = quote_plus(mediaPath+fixPathSymbols(name))
		debug_MS("(mediatools.preparefiles) ### newNAME : {0} ###".format(str(newNAME)))
		debug_MS("(mediatools.preparefiles) ### newURL : {0} ###".format(str(newURL)))
		debug_MS("(mediatools.preparefiles) ### newSOURCE : {0} ###".format(str(newSOURCE)))
		xbmc.executebuiltin('RunPlugin(plugin://service.cron.autobiblio/?mode=adddata&name={0}&stunden={1}&url={2}&source={3})'.format(newNAME, rotation, newURL, newSOURCE))
		return dialog.notification(translation(30531), translation(30532).format(name+'  (Serie)', str(rotation)), icon, 15000)

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
	EP_PAGE = 1
	url_1 = '{0}/content/shows?include=genres,images,seasons&sort=name&filter[id]={1}'.format(BASE_API, BroadCast_Idd)
	debug_MS("(mediatools.LIBRARY_Worker) ##### URL-01 : {0} #####".format(str(url_1)))
	EP_Path = os.path.join(py2_uni(mediaPath), py2_uni(fixPathSymbols(BroadCast_Name)))
	debug_MS("(mediatools.LIBRARY_Worker) ##### EP_Path : {0} #####".format(str(EP_Path)))
	if os.path.isdir(EP_Path):
		shutil.rmtree(EP_Path, ignore_errors=True)
		xbmc.sleep(500)
	xbmcvfs.mkdirs(EP_Path)
	try:
		SHOW_DATA = getUrl(url_1, 'LOAD')
		TVS_title = cleaning(SHOW_DATA['data'][0]['attributes']['name'])
	except: return
	for elem in SHOW_DATA['data']:
		TVS_season, TVS_episode, TVS_plot, TVS_image, TVS_airdate, TVS_yeardate = ("" for _ in range(6))
		TVS_photoID = None
		if elem.get('relationships', None) and elem.get('relationships').get('images', None) and elem.get('relationships').get('images').get('data', None):
			TVS_photoID = [poid.get('id', []) for poid in elem.get('relationships', {}).get('images', {}).get('data', '')][0]
		if 'attributes' in elem:
			elem = elem['attributes']
		TVS_season = (str(elem.get('seasonNumbers', '')) or "")
		TVS_episode = (str(elem.get('episodeCount', '')) or "")
		TVS_plot = (cleaning(elem.get('description', '')).replace('\n', '[CR]') or "")
		TVS_pictures  = SHOW_DATA.get('included', [])
		try: TVS_image = [img.get('attributes', '').get('src', []) for img in TVS_pictures if img.get('id') == TVS_photoID][0]
		except: pass
		TVS_airdate = (str(elem.get('latestVideo', {}).get('airDate', ''))[:10] or str(elem.get('newestEpisodePublishStart', ''))[:10] or "")
		TVS_yeardate = (str(elem.get('latestVideo', {}).get('airDate', ''))[:4] or str(elem.get('newestEpisodePublishStart', ''))[:4] or "")
	while EP_PAGE < 6:
		url_2 = '{0}/content/videos?include=images&sort=name&filter[show.id]={1}&filter[videoType]=EPISODE,STANDALONE&page[number]={2}&page[size]=100'.format(BASE_API, BroadCast_Idd, str(EP_PAGE))
		EPIS_DATA = getUrl(url_2, 'LOAD')
		if len(EPIS_DATA['data']) > 0:
			EP_PAGE += 1
		else:
			EP_PAGE += 5
		debug_MS("(mediatools.LIBRARY_Worker) ### URL-2 : {0} ### EP_PAGE : {1} ### origSERIE : {2} ###".format(url_2, str(EP_PAGE-1), str(BroadCast_Name)))
		for vid in EPIS_DATA['data']:
			EP_idd, EP_SUFFIX, EP_type, Note_1, Note_2, Note_3, EP_fsk, EP_image, EP_airdate, EP_yeardate = ("" for _ in range(10))
			EP_season, EP_episode, EP_duration = ('0' for _ in range(3))
			EP_photoID, startTIMES, endTIMES = (None for _ in range(3))
			EP_genreLIST = []
			if vid.get('relationships', None) and vid.get('relationships').get('genres', None) and vid.get('relationships').get('genres').get('data', None):
				EP_genreLIST = [convert(genid.get('id', [])) for genid in vid.get('relationships', {}).get('genres', {}).get('data', '')]
				if EP_genreLIST: EP_genreLIST = sorted(EP_genreLIST)
			if vid.get('relationships', None) and vid.get('relationships').get('images', None) and vid.get('relationships').get('images').get('data', None):
				EP_photoID = [poid.get('id', []) for poid in vid.get('relationships', {}).get('images', {}).get('data', '')][0]
			try: EP_genre1 = EP_genreLIST[0]
			except: EP_genre1 = ""
			try: EP_genre2 = EP_genreLIST[1]
			except: EP_genre2 = ""
			try: EP_genre3 = EP_genreLIST[2]
			except: EP_genre3 = ""
			EP_idd = (str(vid.get('id', '')) or "")
			if 'attributes' in vid:
				vid = vid['attributes']
			debug_MS("(mediatools.LIBRARY_Worker) ##### ELEMENT : {0} #####".format(str(vid)))
			if vid.get('name', ''):
				EP_name = cleaning(vid['name'])
			else: continue
			if vid.get('isExpiring', '') is True or vid.get('isNew', '') is True:
				EP_SUFFIX = translation(30624) if vid.get('isNew', '') is True else translation(30625)
			if vid.get('seasonNumber', ''):
				EP_season = str(vid['seasonNumber']).zfill(2)
			if vid.get('episodeNumber', ''):
				EP_episode = str(vid['episodeNumber']).zfill(2)
			EP_type = (vid.get('videoType', '') or "")
			if EP_type.upper() == 'STANDALONE' and EP_episode == '0':
				pos_ESP += 1
			if EP_season != '0' and EP_episode != '0':
				EP_name = 'S'+EP_season+'E'+EP_episode+': '+EP_name
			else:
				if EP_type.upper() == 'STANDALONE':
					EP_episode = str(pos_ESP).zfill(2)
					EP_name = 'S00E'+EP_episode+': '+EP_name
			if str(vid.get('publishStart'))[:4].isdigit() and str(vid.get('publishStart'))[:4] not in ['0', '1970']:
				LOCALstart = get_Local_DT(vid['publishStart'][:19])
				startTIMES = LOCALstart.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			if str(vid.get('publishEnd'))[:4].isdigit() and str(vid.get('publishEnd'))[:4] not in ['0', '1970']:
				LOCALend = get_Local_DT(vid['publishEnd'][:19])
				endTIMES = LOCALend.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			if startTIMES and endTIMES: Note_1 = translation(30629).format(str(startTIMES), str(endTIMES))
			elif startTIMES and endTIMES is None: Note_1 = translation(30630).format(str(startTIMES))
			if str(py2_enc(vid.get('rating'))) not in ['', 'None', '0', 'nicht definiert']:
				EP_fsk = translation(30631).format(str(py2_enc(vid.get('rating'))))
			if EP_fsk == "" and 'contentRatings' in vid and vid['contentRatings'] and len(vid['contentRatings']) > 0:
				if str(py2_enc(vid.get('contentRatings', {})[0].get('code', ''))) not in ['', 'None', '0', 'nicht definiert']:
					EP_fsk = translation(30631).format(str(py2_enc(vid.get('contentRatings', {})[0].get('code', ''))))
			if vid.get('description', ''):
				Note_2 = cleaning(vid['description']).replace('\n', '[CR]')
			EP_plot = BroadCast_Name+'[CR]'+Note_1+Note_2
			EP_protect = (vid.get('drmEnabled', False) or False)
			if vid.get('videoDuration', ''):
				EP_duration = get_Time(vid['videoDuration'], 'MINUTES')
			EP_pictures = EPIS_DATA.get('included', [])
			try: EP_image = [img.get('attributes', '').get('src', []) for img in EP_pictures if img.get('id') == EP_photoID][0]
			except: pass
			EP_airdate = (str(vid.get('airDate', ''))[:10] or str(vid.get('publishStart', ''))[:10] or "")
			EP_yeardate = (str(vid.get('airDate', ''))[:4] or str(vid.get('publishStart', ''))[:4] or "")
			episodeFILE = py2_uni(fixPathSymbols(EP_name)) # NAME=STANDARD OHNE HINWEIS (neu|endet bald) !!!
			EP_LONG_title = EP_name+EP_SUFFIX # NAME=LONVERSION MIT SUFFIX=HINWEIS (neu|endet bald) !!!
			COMBINATION.append([episodeFILE, EP_LONG_title, TVS_title, EP_idd, EP_season, EP_episode, EP_plot, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_protect])
	if not COMBINATION: return
	if not xbmcvfs.exists(EP_Path):
		xbmcvfs.mkdirs(EP_Path)
	for episodeFILE, EP_LONG_title, TVS_title, EP_idd, EP_season, EP_episode, EP_plot, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_protect in COMBINATION:
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
    <runtime>{5}</runtime>
    <thumb>{6}</thumb>
    <mpaa>{7}</mpaa>
    <genre clear="true">{8}</genre>
    <genre>{9}</genre>
    <genre>{10}</genre>
    <year>{11}</year>
    <aired>{12}</aired>
    <studio clear="true">DMAX</studio>
</episodedetails>'''.format(EP_LONG_title, TVS_title, EP_season, EP_episode, EP_plot, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate)))
		streamfile = os.path.join(EP_Path, episodeFILE+'.strm')
		debug_MS("(mediatools.LIBRARY_Worker) ##### streamFILE : {0} #####".format(cleaning(streamfile)))
		file = xbmcvfs.File(streamfile, 'w')
		file.write(HOST_AND_PATH+'?mode=playVideo&url='+str(EP_idd))
		file.close()
	nfo_SERIE_string = os.path.join(EP_Path, 'tvshow.nfo')
	with io.open(nfo_SERIE_string, 'w', encoding='utf-8') as textobj_TVS:
		textobj_TVS.write(py2_uni(
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<tvshow>
    <title>{0}</title>
    <showtitle>{0}</showtitle>
    <season>{1}</season>
    <episode>{2}</episode>
    <plot>{3}</plot>
    <thumb aspect="landscape" type="" season="">{4}</thumb>
    <fanart url="">
        <thumb dim="1280x720" colors="" preview="{4}">{4}</thumb>
    </fanart>
    <genre clear="true">{5}</genre>
    <genre>{6}</genre>
    <genre>{7}</genre>
    <year>{8}</year>
    <aired>{9}</aired>
    <studio clear="true">DMAX</studio>
</tvshow>'''.format(TVS_title, TVS_season, TVS_episode, TVS_plot, TVS_image, EP_genre1, EP_genre2, EP_genre3, TVS_yeardate, TVS_airdate)))
	debug_MS("(mediatools.LIBRARY_Worker) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  ENDE = LIBRARY_Worker  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

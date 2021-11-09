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
	from urllib import urlencode  # Python 2.X
	from urllib2 import urlopen  # Python 2.X
else: 
	from urllib.parse import urlencode  # Python 3.X
	from urllib.request import urlopen  # Python 3.X

from .common import *


def mainMenu():
	addDir(translation(30601), icon, {'mode': 'trailer'})
	addDir(translation(30602), icon, {'mode': 'kino'})
	addDir(translation(30603), icon, {'mode': 'series'})
	addDir(translation(30604), icon, {'mode': 'news'})
	if enableADJUSTMENT:
		addDir(translation(30608), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def trailer():
	addDir(translation(30620), icon, {'mode': 'listTrailer', 'url': BASE_URL+'/trailer/beliebteste.html'})
	addDir(translation(30621), icon, {'mode': 'listTrailer', 'url': BASE_URL+'/trailer/imkino/'})
	addDir(translation(30622), icon, {'mode': 'listTrailer', 'url': BASE_URL+'/trailer/bald/'})
	addDir(translation(30623), icon, {'mode': 'listTrailer', 'url': BASE_URL+'/trailer/neu/'})
	addDir(translation(30624), icon, {'mode': 'filtertrailer', 'url': BASE_URL+'/trailer/archiv/'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def kino():
	addDir(translation(30630), icon, {'mode': 'listKino_small', 'url': BASE_URL+'/filme-imkino/vorpremiere/'})
	addDir(translation(30631), icon, {'mode': 'listKino_big', 'url': BASE_URL+'/filme-imkino/kinostart/'})
	addDir(translation(30632), icon, {'mode': 'listKino_big', 'url': BASE_URL+'/filme-imkino/neu/'})
	addDir(translation(30633), icon, {'mode': 'listKino_big', 'url': BASE_URL+'/filme-imkino/besten-filme/user-wertung/'})
	addDir(translation(30634), icon, {'mode': 'selectionWeek', 'url': BASE_URL+'/filme-vorschau/de/'})
	addDir(translation(30635), icon, {'mode': 'filterkino', 'url': BASE_URL+'/filme/besten/user-wertung/'})
	addDir(translation(30636), icon, {'mode': 'filterkino', 'url': BASE_URL+'/filme/schlechtesten/user-wertung/'})
	addDir(translation(30637), icon, {'mode': 'filterkino', 'url': BASE_URL+'/filme/kinderfilme/'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def series():
	addDir(translation(30650), icon, {'mode': 'listSeries_big', 'url': BASE_URL+'/serien/top/'})
	addDir(translation(30651), icon, {'mode': 'filterserien', 'url': BASE_URL+'/serien/beste/'})
	addDir(translation(30652), icon, {'mode': 'listSeries_big', 'url': BASE_URL+'/serien/top/populaerste/'})
	addDir(translation(30653), icon, {'mode': 'listSeries_big', 'url': BASE_URL+'/serien/kommende-staffeln/meisterwartete/'})
	addDir(translation(30654), icon, {'mode': 'listSeries_big', 'url': BASE_URL+'/serien/kommende-staffeln/'})
	addDir(translation(30655), icon, {'mode': 'listSeries_big', 'url': BASE_URL+'/serien/kommende-staffeln/demnaechst/'})
	addDir(translation(30656), icon, {'mode': 'listSeries_big', 'url': BASE_URL+'/serien/neue/'})
	addDir(translation(30657), icon, {'mode': 'listTrailer', 'url': BASE_URL+'/trailer/serien/neueste/'})
	addDir(translation(30658), icon, {'mode': 'filterserien', 'url': BASE_URL+'/serien-archiv/'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def news():
	addDir(translation(30670), icon, {'mode': 'listNews', 'url': BASE_URL+'/videos/shows/funf-sterne/'})
	addDir(translation(30671), icon, {'mode': 'listNews', 'url': BASE_URL+'/videos/shows/filmstarts-fehlerteufel/'})
	addDir(translation(30672), icon, {'mode': 'listNews', 'url': BASE_URL+'/trailer/interviews/'})
	addDir(translation(30673), icon, {'mode': 'listNews', 'url': BASE_URL+'/videos/shows/meine-lieblings-filmszene/'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def filtertrailer(url):
	debug_MS("(navigator.filtertrailer) -------------------------------------------------- START = filtertrailer --------------------------------------------------")
	debug_MS("(navigator.filtertrailer) ##### URL = {0} #####".format(url))
	if not "genre-" in url:
		addDir(translation(30801), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filtertrailer', 'extras': 'Nach Genre'})
	if not "sprache-" in url:
		addDir(translation(30802), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filtertrailer', 'extras': 'Nach Sprache'})
	if not "format-" in url:
		addDir(translation(30803), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filtertrailer', 'extras': 'Nach Typ'})
	addDir(translation(30810), icon, {'mode': 'listTrailer', 'url': url})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def filterkino(url):
	debug_MS("(navigator.filterkino) -------------------------------------------------- START = filterkino --------------------------------------------------")
	debug_MS("(navigator.filterkino) ##### URL = {0} #####".format(url))
	if not "genre-" in url:
		addDir(translation(30801), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filterkino', 'extras': 'Alle Genres'})
	if not "jahrzehnt" in url:
		addDir(translation(30804), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filterkino', 'extras': 'Alle Jahre'})
	if not "produktionsland-" in url:
		addDir(translation(30805), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filterkino', 'extras': 'Alle Länder'})
	addDir(translation(30810), icon, {'mode': 'listKino_small', 'url': url})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def filterserien(url):
	debug_MS("(navigator.filterserien) -------------------------------------------------- START = filterserien --------------------------------------------------")
	debug_MS("(navigator.filterserien) ##### URL = {0} #####".format(url))
	if not "genre-" in url:
		addDir(translation(30801), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filterserien', 'extras': 'Nach Genre'})
	if not "jahrzehnt" in url:
		addDir(translation(30804), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filterserien', 'extras': 'Nach Produktionsjahr'})
	if not "produktionsland-" in url:
		addDir(translation(30805), icon, {'mode': 'selectionCategories', 'url': url, 'type': 'filterserien', 'extras': 'Nach Land'})
	addDir(translation(30810), icon, {'mode': 'listSeries_big', 'url': url})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def selectionCategories(url, type, CATEGORY):
	debug_MS("(navigator.selectionCategories) -------------------------------------------------- START = selectionCategories --------------------------------------------------")
	debug_MS("(navigator.selectionCategories) ##### URL = {0} ##### TYPE = {1} ##### CATEGORY = {2} #####".format(url, type, CATEGORY))
	LINKING = ['archiv/', 'serien/beste']
	content = getUrl(url)
	if any(d in url for d in LINKING):
		result = content[content.find('data-name="'+CATEGORY+'"')+1:]
		result = result[:result.find('</ul>')]
		part = result.split('class="filter-entity-item"')
	else:
		result = content[content.find(CATEGORY+'</span>')+1:]
		result = result[:result.find('</li></ul>')]
		part = result.split('</li><li')
	for i in range(1,len(part),1):  
		element=part[i]
		element = element.replace('<strong>', '').replace('</strong>', '')
		matchNO = re.compile(r'<span class=["\'](?:light|lighten)["\']>\(([^<]+?)\)</span>', re.S).findall(element)
		number = matchNO[0].strip() if matchNO else None
		if 'href=' in element:
			matchUN = re.compile(r'href=["\']([^"]+)["\'](?: title=.+?["\']>|>)([^<]+?)</a>', re.S).findall(element)
			link = BASE_URL+matchUN[0][0]
			name = cleaning(matchUN[0][1])
		else:
			matchH1 = re.compile(r'<span class=["\']ACr([^"]+) item-content["\'] title=.+?["\']>([^<]+?)</span>', re.S).findall(element)
			matchH2 = re.compile(r'<span class=["\']acLnk ([^"]+)["\']>([^<]+?)</span>', re.S).findall(element)
			link = BASE_URL+convert64(matchH1[0][0]) if matchH1 else BASE_URL+decodeURL(matchH2[0][0])
			name = cleaning(matchH1[0][1]) if matchH1 else cleaning(matchH2[0][1])
		if number: name += "   ("+str(number)+")"
		addDir(name, icon, {'mode': type, 'url': link})
		debug_MS("(navigator.selectionCategories) Name : {0}".format(name))
		debug_MS("(navigator.selectionCategories) Link : {0}".format(link))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def selectionWeek(url):
	debug_MS("(navigator.selectionWeek) -------------------------------------------------- START = selectionWeek --------------------------------------------------")
	debug_MS("(navigator.selectionWeek) ##### URL = {0} #####".format(url))
	content = getUrl(url)
	result = content[content.find('<div class="pagination pagination-select">')+1:]
	result = result[:result.find('<span class="txt">Nächste</span><i class="icon icon-right icon-arrow-right-a">')]
	matchUN = re.compile(r'<option value=["\']ACr([^"]+)["\']([^<]+)</option>', re.S).findall(result)
	for link, title in matchUN:
		link = convert64(link)
		xDate = str(link.replace('filme-vorschau/de/week-', '').replace('/', ''))
		title = title.replace('>', '')
		if "selected" in title:
			title = title.replace('selected', '')
			name = translation(30831).format(cleaning(title))
		else: name = cleaning(title)
		debug_MS("(navigator.selectionWeek) Name : {0}".format(name))
		debug_MS("(navigator.selectionWeek) Datum : {0}".format(xDate))
		addDir(name, icon, {'mode': 'listKino_big', 'url': BASE_URL+link, 'extras': xDate})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listTrailer(url, PAGE, POS):
	debug_MS("(navigator.listTrailer) -------------------------------------------------- START = listTrailer --------------------------------------------------")
	NEPVurl = url
	PGurl = '{}?page={}'.format(url, PAGE) if int(PAGE) > 1 else url
	debug_MS("(navigator.listTrailer) ##### URL = {0} ##### PAGE = {1} #####".format(PGurl, str(PAGE)))
	content = getUrl(PGurl)
	if int(POS) == 0:
		try:
			POS = re.compile('<a class=["\']button button-md item["\'] href=.+?page=[0-9]+["\']>([0-9]+)</a></div></nav>', re.S).findall(content)[0]
			debug_MS("(navigator.listTrailer) *FOUND-1* Pages-Maximum : {0}".format(str(POS)))
		except:
			try:
				POS = re.compile('<span class=["\']ACr.+?button-md item["\']>([0-9]+)</span></div></nav>', re.S).findall(content)[0]
				debug_MS("(navigator.listTrailer) *FOUND-2* Pages-Maximum : {0}".format(str(POS)))
			except: pass
	result = content[content.find('<main id="content-layout" class="content-layout cf">')+1:]
	result = result[:result.find('<div class="mdl-rc">')]
	part = result.split('<figure class="thumbnail ">')
	for i in range(1,len(part),1):
		element = part[i]
		element = element.replace('<strong>', '').replace('</strong>', '')
		duration = '0'
		try:
			image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.S|re.IGNORECASE).findall(element)[0]
		except:
			image = re.compile(r'["\']src["\']:["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.S|re.IGNORECASE).findall(element)[0]
		photo = enlargeIMG(image)
		RunTime = re.compile('class=["\']thumbnail-count["\']>(.+?)</span>', re.S).findall(element)
		if RunTime and ":" in RunTime[0]:
			running = re.compile('([0-9]+):([0-9]+)', re.S).findall(RunTime[0])
			duration = int(running[0][0])*60+int(running[0][1])
		elif RunTime and str(RunTime[0]).isdigit():
			duration = int(RunTime[0])
		matchUN = re.compile(r'(?:class="meta-title-link"|<a) href="([^"]+)"(?: class="layer-link">)?([^<]+)</a>', re.S).findall(element)
		link = BASE_URL+matchUN[0][0]
		name = cleaning(matchUN[0][1].replace(' >', '').replace('>', ''))
		debug_MS("(navigator.listTrailer) Name : {0} || Link : {1}".format(name, link))
		debug_MS("(navigator.listTrailer) Duration : {0} || Thumb : {1}".format(str(duration), photo))
		addLink(name, photo, {'mode': 'playVideo', 'url': link, 'extras': url}, duration=duration)
	if int(POS) > int(PAGE):
		debug_MS("(navigator.listTrailer) Now show NextPage ...")
		addDir(translation(30832), artpic+'nextpage.png', {'mode': 'listTrailer', 'url': NEPVurl, 'page': int(PAGE)+1, 'position': int(POS)})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listKino_big(url, PAGE, POS):
	debug_MS("(navigator.listKino_big) -------------------------------------------------- START = listKino_big --------------------------------------------------")
	FOUND = False
	NEPVurl = url
	PGurl = '{}?page={}'.format(url, PAGE) if int(PAGE) > 1 else url
	debug_MS("(navigator.listKino_big) ##### URL = {0} ##### PAGE = {1} #####".format(PGurl, str(PAGE)))
	content = getUrl(PGurl)
	if int(POS) == 0:
		try:
			POS = re.compile('<a class=["\']button button-md item["\'] href=.+?page=[0-9]+["\']>([0-9]+)</a></div></nav>', re.S).findall(content)[0]
			debug_MS("(navigator.listKino_big) *FOUND-1* Pages-Maximum : {0}".format(str(POS)))
		except:
			try:
				POS = re.compile('<span class=["\']ACr.+?button-md item["\']>([0-9]+)</span></div></nav>', re.S).findall(content)[0]
				debug_MS("(navigator.listKino_big) *FOUND-2* Pages-Maximum : {0}".format(str(POS)))
			except: pass
	result = content[content.find('<main id="content-layout" class="content-layout cf">')+1:]
	result = result[:result.find('<div class="mdl-rc">')]
	part = result.split('<figure class="thumbnail ">')
	for i in range(1,len(part),1):
		element=part[i]
		movieDATE, genre, director, cast, rating = (None for _ in range(5))
		genreLIST, directorLIST, castLIST = ([] for _ in range(3))
		matchUN = re.compile('class=["\']ACr([^ "]+) thumbnail-container thumbnail-link["\'] title=["\'](.+?)["\']>', re.S).findall(element)
		link = BASE_URL+convert64(matchUN[0][0])
		name = cleaning(matchUN[0][1])
		image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.S|re.IGNORECASE).findall(element)[0]
		photo = enlargeIMG(image)
		if "/serien" in PGurl:
			matchDT = re.compile('<div class=["\']meta-body-item meta-body-info["\']>([^<]+?)<span class=["\']spacer["\']>/</span>', re.S).findall(element)
		else:
			matchDT = re.compile('<span class=["\']date["\']>.*?([a-zA-Z]+ [0-9]+)</span>', re.S).findall(element)
		movieDATE = matchDT[0] if matchDT else None
		if movieDATE and "/serien" in PGurl:
			name += "   ("+str(movieDATE.replace('\n', '').replace(' - ', '~').replace('läuft seit', 'ab').strip())+")"
		elif movieDATE and "besten-filme/user-wertung" in PGurl:
			newDATE = cleanMonth(movieDATE.lower())
			name += "   ("+str(newDATE)+")"
		try: # Grab - Genres
			if '<span class="spacer">' in element:
				result_1 = re.compile('<span class=["\']spacer["\']>/</span>(.+?)</div>', re.S).findall(element)[-1]
			else:
				result_1 = re.compile('<div class=["\']meta-body-item meta-body-info["\']>(.+?)</div>', re.S).findall(element)[-1]
			matchG = re.compile('<span class=["\']ACr.*?["\']>(.+?)</span>', re.S).findall(result_1)
			for gNames in matchG:
				genreLIST.append(cleaning(gNames))
			if genreLIST: genre = ', '.join(sorted(genreLIST))
		except: pass
		try: # Grab - Directors
			result_2 = re.compile('<div class=["\']meta-body-item meta-body-direction["\']>(.+?)</div>', re.S).findall(element)[-1]
			matchD = re.compile('<span class=["\']ACr.*?["\']>(.+?)</span>', re.S).findall(result_2)
			for dNames in matchD:
				directorLIST.append(cleaning(dNames))
			if directorLIST: director = ', '.join(sorted(directorLIST))
		except: pass
		try: # Grab - Casts
			result_3 = re.compile('<div class=["\']meta-body-item meta-body-actor["\']>(.+?)</div>', re.S).findall(element)[-1]
			matchC = re.compile('<span class=["\']ACr.*?["\']>(.+?)</span>', re.S).findall(result_3)
			for cNames in matchC:
				castLIST.append(cleaning(cNames))
			if castLIST: cast = ', '.join(sorted(castLIST))
		except: pass
		try: # Grab - Plot
			desc = re.compile('<div class=["\']synopsis["\']>(.+?)</div>', re.S).findall(element)[0]
			plot = cleaning(re.sub(r'\<.*?\>', '', desc))
		except: plot=""
		try: # Grab - Rating
			result_4 = (element[element.find('User-Wertung')+1:] or element[element.find('Pressekritiken')+1:])
			rating = re.compile('class=["\']stareval-note["\']>([^<]+?)</span></div>', re.S).findall(result_4)[0].strip().replace(',', '.')
		except: pass
		matchTT = re.compile('<div class=["\']buttons-holder["\']>(.+?)</div>', re.S).findall(element)
		TRAILER = True if matchTT and ("Trailer" in matchTT[0] or "Teaser" in matchTT[0]) else False
		debug_MS("(navigator.listKino_big) Name : {0} || Link : {1}".format(name, link))
		debug_MS("(navigator.listKino_big) Genre : {0} || Thumb : {1}".format(genre, photo))
		debug_MS("(navigator.listKino_big) Regie : {0} || Cast : {1}".format(director, cast))
		if 'filme-vorschau/' in PGurl:
			FOUND = True
			addLink(name, photo, {'mode': 'playVideo', 'url': link, 'type': 'filtervorschau', 'extras': url}, plot, genre, director, cast, rating)
		else:
			FOUND = True
			if (TRAILER or '<span class="ico-play-inner"></span>' in element) and not 'button btn-disabled' in element:
				addLink(name, photo, {'mode': 'playVideo', 'url': link, 'extras': url}, plot, genre, director, cast, rating)
			else:
				addDir(translation(30835).format(name), photo, {'mode': 'blankFUNC', 'url': '00'}, plot, genre, director, cast, rating, False)
	if not FOUND:
		return dialog.notification(translation(30523), translation(30524), icon, 8000)
	if NEXT_AND_BEFORE and 'filme-vorschau/' in PGurl:
		try:
			LEFT = re.compile(r'<span class=["\']ACr([^ "]+) button button-md button-primary-full button-left["\']>.*?span class=["\']txt["\']>Vorherige</span>', re.S).findall(result)[0]
			RIGHT = re.compile(r'<span class=["\']ACr([^ "]+) button button-md button-primary-full button-right["\']>.*?span class=["\']txt["\']>Nächste</span>', re.S).findall(result)[0]
			LINK_L, LINK_R = convert64(LEFT), convert64(RIGHT)
			BeforeDAY, NextDAY = str(LINK_L.replace('filme-vorschau/de/week-', '').replace('/', '')), str(LINK_R.replace('filme-vorschau/de/week-', '').replace('/', ''))
			before, next = datetime(*(time.strptime(BeforeDAY, '%Y-%m-%d')[0:6])), datetime(*(time.strptime(NextDAY, '%Y-%m-%d')[0:6]))
			bxORG, nxORG = before.strftime('%Y-%m-%d'), next.strftime('%Y-%m-%d')
			bxNEW, nxNEW = before.strftime('%d.%m.%Y'), next.strftime('%d.%m.%Y')
			addDir(translation(30833).format(str(nxNEW)), icon, {'mode': 'listKino_big', 'url': BASE_URL+LINK_R, 'extras': nxORG})
			addDir(translation(30834).format(str(bxNEW)), icon, {'mode': 'listKino_big', 'url': BASE_URL+LINK_L, 'extras': bxORG})
		except: pass
	if int(POS) > int(PAGE) and not 'filme-vorschau/' in PGurl:
		debug_MS("(navigator.listKino_big) Now show NextPage ...")
		addDir(translation(30832), artpic+'nextpage.png', {'mode': 'listKino_big', 'url': NEPVurl, 'page': int(PAGE)+1, 'position': int(POS)})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listKino_small(url, PAGE):
	debug_MS("(navigator.listKino_small) -------------------------------------------------- START = listKino_small --------------------------------------------------")
	FOUND = False
	NEPVurl = url
	PGurl = '{}?page={}'.format(url, PAGE) if int(PAGE) > 1 else url
	debug_MS("(navigator.listKino_small) ##### URL = {0} ##### PAGE = {1} #####".format(PGurl, str(PAGE)))
	content = getUrl(PGurl)
	part = content.split('<div class="data_box">')
	for i in range(1,len(part),1):
		element=part[i]
		movieDATE, genre, director, cast, rating = (None for _ in range(5))
		genreLIST, directorLIST, castLIST = ([] for _ in range(3))
		matchH1 = re.compile('button btn-primary ["\'] href=["\']([^"]+?)["\']', re.S).findall(element)
		matchH2 = re.compile('class=["\']acLnk ([^ ]+?) button btn-primary', re.S).findall(element)
		link = BASE_URL+decodeURL(matchH2[0]) if matchH2 else BASE_URL+matchH1[0] if matchH1 else None
		image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.S|re.IGNORECASE).findall(element)[0]
		photo = enlargeIMG(image)
		title = re.compile('alt=["\'](.+?)["\'\" \' ]\s+title=', re.S).findall(element)[0]
		name = cleaning(title)
		matchDT = re.compile('<span class=["\']film_info lighten fl["\']>Starttermin(.+?)</div>', re.S).findall(element)
		movieDATE =re.sub(r'\<.*?\>', '', matchDT[0]) if matchDT else None
		if movieDATE and not "unbekannt" in movieDATE.lower():
			name += "   ("+movieDATE.replace('\n', '').replace('.', '-').strip()[0:10]+")"
		try: # Grab - Directors
			result_1 = re.compile('<span class=["\']film_info lighten fl["\']>Von </span>(.+?)</div>', re.S).findall(element)[0]
			matchD = re.compile(r'(?:<span title=|<a title=)["\'](.+?)["\'] (?:class=|href=)', re.S).findall(result_1)
			for dNames in matchD:
				directorLIST.append(cleaning(dNames))
			if directorLIST: director = ', '.join(sorted(directorLIST))
		except: pass
		try: # Grab - Casts
			result_2 = re.compile('<span class=["\']film_info lighten fl["\']>Mit </span>(.+?)</div>', re.S).findall(element)[0]
			matchC = re.compile(r'(?:<span title=|<a title=)["\'](.+?)["\'] (?:class=|href=)', re.S).findall(result_2)
			for cNames in matchC:
				castLIST.append(cleaning(cNames))
			if castLIST: cast = ', '.join(sorted(castLIST))
		except: pass
		try: # Grab - Genres
			result_3 = re.compile('<span class=["\']film_info lighten fl["\']>Genre</span>(.+?)</div>', re.S).findall(element)[0]
			matchG = re.compile('<span itemprop=["\']genre["\']>([^<]+?)</span>', re.S).findall(result_3)
			for gNames in matchG:
				genreLIST.append(cleaning(gNames))
			if genreLIST: genre = ', '.join(sorted(genreLIST))
		except: pass
		try: # Grab - Plot
			desc = re.compile("<p[^>]*>([^<]+)<", re.S).findall(element)[0]
			plot = cleaning(desc.replace('&nbsp;', ''))
		except: plot=""
		try: # Grab - Rating
			result_4 = (element[element.find('User-Wertung')+1:] or element[element.find('Pressekritiken')+1:])
			rating = re.compile('<span class=["\']note["\']>([^<]+?)</span></span>', re.S).findall(result_4)[0].strip().replace(',', '.')
		except: pass
		debug_MS("(navigator.listKino_small) Name : {0} || Link : {1}".format(name, link))
		debug_MS("(navigator.listKino_small) Genre : {0} || Thumb : {1}".format(genre, photo))
		debug_MS("(navigator.listKino_small) Regie : {0} || Cast : {1}".format(director, cast))
		if link and not 'button btn-disabled' in element:
			FOUND = True
			addLink(name, photo, {'mode': 'playVideo', 'url': link, 'extras': url}, plot, genre, director, cast, rating)
		else:
			FOUND = True
			addDir(translation(30835).format(name), photo, {'mode': 'blankFUNC', 'url': '00'}, plot, genre, director, cast, rating, False)
	if not FOUND:
		return dialog.notification(translation(30523), translation(30524), icon, 8000)
	if 'fr">Nächste<i class="icon-arrow-right">' in content:
		debug_MS("(navigator.listKino_small) Now show NextPage ...")
		addDir(translation(30832), artpic+'nextpage.png', {'mode': 'listKino_small', 'url': NEPVurl, 'page': int(PAGE)+1})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listNews(url, PAGE):
	debug_MS("(navigator.listNews) -------------------------------------------------- START = listNews --------------------------------------------------")
	NEPVurl = url
	PGurl = '{}?page={}'.format(url, PAGE) if int(PAGE) > 1 else url
	debug_MS("(navigator.listNews) ##### URL = {0} ##### PAGE = {1} #####".format(PGurl, str(PAGE)))
	content = getUrl(PGurl)
	result = content[content.find('<div class="colcontent">')+1:]
	result = result[:result.find('class="centeringtable">')]
	part = result.split('<div class="datablock')
	for i in range(1,len(part),1):
		element = part[i]
		image = re.compile(r'src=["\'](https?://.+?(?:[0-9]+\.png|[a-z]+\.png|[0-9]+\.jpg|[a-z]+\.jpg|[0-9]+\.gif|[a-z]+\.gif))["\'\?]', re.S|re.IGNORECASE).findall(element)[0]
		photo = enlargeIMG(image)
		matchUN = re.compile(r'href=["\'](.+?)["\'](?: class=.*?</strong)?>(.+?)</a>', re.S).findall(element)
		link = BASE_URL+matchUN[0][0]
		title = matchUN[0][1].replace('\n', '').strip()
		name = cleaning(re.sub(r'\<.*?\>', '', title))
		try: # Grab - Plot
			desc = re.compile('class=["\']fs11 purehtml["\']>(.+?)<div class=["\']spacer["\']></div>', re.S).findall(element)[0]
			plot = cleaning(re.sub(r'\<.*?\>', '', desc))
		except: plot = name
		debug_MS("(navigator.listNews) Name : {0} || Link : {1}".format(name, link))
		debug_MS("(navigator.listNews) Thumb : {0}".format(photo))
		addLink(name, photo, {'mode': 'playVideo', 'url': link, 'extras': url}, plot)
	try:
		nextPG = re.compile('(<li class="navnextbtn">[^<]+<span class="acLnk)', re.S).findall(content)[0]
		debug_MS("(navigator.listNews) Now show NextPage ...")
		addDir(translation(30832), artpic+'nextpage.png', {'mode': 'listNews', 'url': NEPVurl, 'page': int(PAGE)+1})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playVideo(url, type, REF):
	debug_MS("(navigator.playVideo) -------------------------------------------------- START = playVideo --------------------------------------------------")
	debug_MS("(navigator.playVideo) ##### URL = {0} ##### TYPE = {1} ##### REFERER = {2} ##### ".format(url, type, REF))
	MEDIAS = []
	FIRST, finalURL = (False for _ in range(2))
	if type == 'filtervorschau':
		html = getUrl(url)
		try: # <a class="trailer item"   href="/kritiken/278374/trailer/19576405.html" title="Trailer"
			FIRST = re.compile('class=["\']trailer item["\']   href=["\']([^"]+?)["\'] title=["\']Trailer["\']>', re.S).findall(html)[0]
		except:
			try:
				selection = re.findall('<main id="content-layout" class="content-layout entity movie cf(.+?)<div class="rc-content">', html, re.S)
				for chtml in selection:
					matchU = re.compile(r'<span class=["\']ACr([^ ]+?) button button-sm button-primary-full["\']>', re.S).findall(chtml)[0]
					FIRST = convert64(matchU)
			except: pass
	content = getUrl(BASE_URL+FIRST, referer=url) if FIRST else getUrl(url, referer=REF)
	try:
		SECOND = re.compile("<iframe[^>]+?src=['\"](.+?)['\"]", re.S).findall(content)
		debug_MS("(navigator.playVideo) *FOUND-1* Extra-Content : {0}".format(SECOND))
		if "_video" in SECOND[1]:
			newURL = BASE_URL+SECOND[1]
			content = getUrl(newURL, referer=url)
		elif "youtube.com" in SECOND[0]:
			youtubeID = SECOND[0].split('/')[-1].strip()
			debug_MS("(navigator.playVideo) *FOUND-2* Extern-Video auf Youtube [ID] : {0}".format(youtubeID))
			finalURL = 'plugin://plugin.video.youtube/play/?video_id='+youtubeID
	except: pass
	if not finalURL:
		mp4_QUALITIES = ['high', 'medium', 'standard']
		response = re.compile(r'(?:class=["\']player  js-player["\']|class=["\']player player-auto-play js-player["\']|<div id=["\']btn-export-player["\'].*?) data-model=["\'](.+?),&quot;disablePostroll&quot;', re.S).findall(content)[0].replace('&quot;', '"')+"}"
		debug_MS("(navigator.playVideo) ##### Extraction of Stream-Links : {0} #####".format(response))
		DATA = json.loads(response)
		for item in DATA.get('videos', []):
			vidQualities = item.get('sources', '')
			for found in mp4_QUALITIES:
				for quality in vidQualities:
					if quality == found:
						MEDIAS.append({'url': vidQualities[quality], 'quality': quality, 'mimeType': 'video/mp4'})
	if MEDIAS:
		finalURL = VideoBEST(MEDIAS[0]['url'])
	if finalURL:
		finalURL = 'https:'+finalURL.replace(' ', '%20') if not 'youtube' in finalURL and finalURL[:4] != 'http' else finalURL.replace(' ', '%20')
		log("(navigator.playVideo) StreamURL : {0}".format(finalURL))
		listitem = xbmcgui.ListItem(path=finalURL)
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, listitem)
	else:
		failing("(navigator.playVideo) ##### Die angeforderte Video-Url wurde leider NICHT gefunden !!! #####\n   ##### URL : {0} #####".format(url))
		return dialog.notification(translation(30521).format('PLAY'), translation(30525), icon, 8000)

def VideoBEST(best_url):
	# *mp4URL* Qualität nachbessern, überprüfen, danach abspielen
	standards = [best_url, ""]
	standards[1] = standards[0].replace('_sd_', '_hd_')
	for element in reversed(standards):
		if len(element) > 0:
			try:
				code = urlopen(element).getcode()
				if str(code) == '200':
					return element
			except: pass
	return best_url

def addDir(name, image, params={}, plot=None, genre=None, director=None, cast=None, rating=None, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Genre': [genre], 'Director': [director], 'Cast': [cast], 'Rating': rating})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addLink(name, image, params={}, plot=None, genre=None, director=None, cast=None, rating=None, duration=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	info = {}
	info['Season'] = None
	info['Episode'] = None
	info['Tvshowtitle'] = None
	info['Title'] = name
	info['Tagline'] = None
	info['Plot'] = plot
	info['Duration'] = duration
	info['Year'] = None
	info['Genre'] = [genre]
	info['Director'] = [director]
	info['Writer'] = None
	info['Cast'] = [cast]
	info['Rating'] = rating
	info['Mpaa'] = None
	info['Mediatype'] = 'movie'
	liz.setInfo(type='Video', infoLabels=info)
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	liz.addStreamInfo('Video', {'Duration': duration})
	liz.setProperty('IsPlayable', 'true')
	liz.setContentLookup(False)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)

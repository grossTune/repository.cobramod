# -*- coding: utf-8 -*-

import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import shutil
import time
import _strptime
from datetime import datetime, timedelta
import sqlite3
import traceback
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote_plus, unquote_plus  # Python 2.X
else:
	from urllib.parse import urlencode, quote_plus, unquote_plus  # Python 3+

from common import *
HOST_AND_PATH                 = sys.argv[0]
ADDON_HANDLE                  = int(sys.argv[1])


if not xbmcvfs.exists(temp):
	xbmcvfs.mkdirs(temp)

def mainMenu():
	if os.path.isdir(temp) and xbmcvfs.exists(Database):
		xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
		try:
			conn = sqlite3.connect(Database)
			cur = conn.cursor()
			cur.execute('SELECT * FROM stocks')
			for (stunden, url, name, last, source) in cur.fetchall():
				name, shortENTRY = py2_enc(name), py2_enc(name)
				name += translation(30601).format(url.split('@@')[1].split('&')[0]) if '@@' in url else translation(30602)
				shortENTRY += '  ('+url.split('@@')[1].split('&')[0]+')' if '@@' in url else '  (Serie)'
				debug("(navigator.mainMenu) ##### Stunden= {0} || URL= {1} || shortENTRY= {2} || lastUPDATE= {3} || Source= {4} #####".format(str(stunden), url, shortENTRY, last, source))
				if source != 'standard' and os.path.isdir(source) and forceTrash:
					addDir(translation(30603).format(name), icon, {'mode': 'delete_table', 'url': url, 'shortENTRY': shortENTRY, 'source': source})
				elif source == 'standard' or not forceTrash:
					addDir(translation(30604).format(name), icon, {'mode': 'delete_table', 'url': url, 'shortENTRY': shortENTRY, 'source': source})
		except:
			if enableWARNINGS:
				dialog.notification(translation(30521).format('Menü anzeigen'), translation(30522), icon, 10000)
			failing("(navigator.mainMenu) ERROR - ERROR - ERROR : "+traceback.format_exc())
		finally:
			cur.close()
			conn.close()
	else:
		dialog.ok(addon_id, translation(30505))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def create_table():
	conn = sqlite3.connect(Database)
	cur = conn.cursor()
	try:
		cur.execute('CREATE TABLE IF NOT EXISTS stocks (stunden INTEGER, url TEXT PRIMARY KEY, name TEXT, last DATETIME)')
		try:
			cur.execute('ALTER TABLE stocks ADD COLUMN source TEXT')
		except sqlite3.OperationalError: pass
		conn.commit()
	except :
		if enableWARNINGS:
			dialog.notification(translation(30521).format('Tabelle erstellen'), translation(30522), icon, 10000)
		failing("(navigator.create_table) ERROR - ERROR - ERROR : "+traceback.format_exc())
	finally:
		cur.close()
		conn.close()

def insert_table(name, stunden, url, source):
	last = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	try:
		conn = sqlite3.connect(Database)
		conn.text_factory = str
		cur = conn.cursor()
		cur.execute('INSERT OR REPLACE INTO stocks VALUES (?,?,?,?,?)', (int(stunden), url, name, last, source))
		conn.commit()
	except:
		conn.rollback() # Roll back any change if something goes wrong
		if enableWARNINGS:
			dialog.notification(translation(30521).format('Eintrag einfügen'), translation(30522), icon, 10000)
		failing("(navigator.insert_table) ERROR - ERROR - ERROR : "+traceback.format_exc())
	finally:
		cur.close()
		conn.close()

def delete_table(shortENTRY, url, source):
	source = TRANS_PATH(os.path.join(source, '')) if source.startswith('special://') else source
	source = py2_uni(source)
	first_BASE = os.sep.join(source.split(os.sep)[:-1]) if '@@' in url and source != 'standard' else False
	try:
		conn = sqlite3.connect(Database, isolation_level=None)
		cur = conn.cursor()
		cur.execute('DELETE FROM stocks WHERE url = ?', (url,))
		cur.execute('VACUUM')
		conn.commit()
		if source != 'standard' and os.path.isdir(source) and forceTrash:
			shutil.rmtree(source, ignore_errors=True)
			log("(navigator.delete_table) ########## DELETING from Crontab and System || FOLDER = {0} || TITLE = {1} || ##########".format(str(source), shortENTRY))
			if first_BASE:
				if len([f for f in os.listdir(first_BASE)]) == 1:
					shutil.rmtree(first_BASE, ignore_errors=True)
					log("(navigator.delete_table) ########## LAST TURN - DELETING from System || BASE-FOLDER = {0} || ##########".format(str(first_BASE)))
		elif source == 'standard' or not forceTrash:
			dialog.ok(addon_id, translation(30501))
			log("(navigator.delete_table) ########## DELETING only from Crontab - TITLE = {0} ##########".format(shortENTRY))
	except:
		conn.rollback() # Roll back any change if something goes wrong
		if enableWARNINGS:
			dialog.notification(translation(30521).format('Eintrag löschen'), translation(30522), icon, 10000)
		failing("(navigator.delete_table) ERROR - ERROR - ERROR : ########## ({0}) received... ({1}) ...Delete Name in List failed ##########".format(shortENTRY, traceback.format_exc()))
	finally:
		cur.close()
		conn.close()

def clearEntireBase():
	if os.path.isdir(temp) and xbmcvfs.exists(Database):
		if dialog.yesno(addon_id, translation(30502), nolabel=translation(30503), yeslabel=translation(30504)):
			shutil.rmtree(temp, ignore_errors=True)
			xbmc.sleep(1000)
			dialog.notification(translation(30523), translation(30524), icon, 8000)
			log("(navigator.clearEntireBase) ########## DELETING complete DATABASE ... {0} ... success ##########".format(Database))
		else:
			return # they clicked no, we just have to exit the gui here
	else:
		dialog.ok(addon_id, translation(30505))

def addDir(name, image, params={}):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type="Video", infoLabels={"Title": name})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	xbmcplugin.setContent(ADDON_HANDLE, 'movies')
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=True)

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split('&')
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', 'root'))
shortENTRY = unquote_plus(params.get('shortENTRY', ''))
stunden = unquote_plus(params.get('stunden', ''))
source = unquote_plus(params.get('source', 'standard'))

if mode == 'root':
	mainMenu()
elif mode == 'adddata':
	create_table()
	debug("(navigator.adddata) ########## START INSTERT ##########")
	debug("(navigator.adddata) ### Name = {0} || Stunden = {1} || URL-1 = {2} || Source = {3} ###".format(name, str(stunden), url, source))
	insert_table(name, stunden, url, source)
	debug("(navigator.adddata) ########## AFTER INSTERT ##########")
	xbmc.executebuiltin('RunPlugin('+url+')')
elif mode == 'delete_table':
	delete_table(shortENTRY, url, source)
	xbmc.executebuiltin('Container.Refresh')
elif mode == 'clearEntireBase':
	clearEntireBase()

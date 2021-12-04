# -*- coding: utf-8 -*-

import sys
import os
import xbmc
import xbmcaddon
import json
import xbmcvfs
import time
import _strptime
from datetime import datetime, timedelta
import sqlite3
import traceback

from common import *
from provider import Client

wait_time = 160  # 20+160 Seconds = 180 seconds = 3 minutes - wait at KODI start
loop_time = 3600  # 3600 seconds = 1 hour - time when the process started again
MAX_ERRORS = 10


class KodiMonitor(xbmc.Monitor):
	def __init__(self):
		xbmc.Monitor.__init__(self)
		self.Monitor = xbmc.Monitor()
		self.Scan = xbmc.getCondVisibility('Library.IsScanningVideo')
		self.Base = xbmcvfs.exists(Database)
		self.traversing = Client(Client.SUPPORTED_ADDONS)

	def current_os(self):
		COS = 'Unknown'
		platforms = ['System.Platform.Android', 'System.Platform.Darwin', 'System.Platform.Linux', 'System.Platform.IOS', 'System.Platform.OSX', 'System.Platform.Windows']
		for elem in platforms:
			if xbmc.getCondVisibility(elem):
				COS = elem.split('.')[-1]
				break
		return COS

	def start_signal(self):
		time.sleep(20)
		special("#############################################################################################")
		special("########## RUNNING: "+addon_id+" VERSION "+addon_version+" / ON PLATFORM: "+self.current_os()+" ##########")
		special("############## Start the Service in nearly 3 minutes - wait for other Instances to close ####################")
		special("#############################################################################################")
		time.sleep(wait_time)
		self.load_rebuild()

	def load_rebuild(self):
		errors = 0
		log("(service.load_rebuild) ########## START SERVICE ##########")
		while not self.Monitor.abortRequested() and not self.Scan and self.Base:
			debug("(service.load_rebuild) ########## START LOOP ... ##########")
			try:
				conn = sqlite3.connect(Database)
				cur = conn.cursor()
				cur.execute('SELECT * FROM stocks')
				for (stunden, url, name, last, source) in cur.fetchall():
					name = py2_uni(name)
					SUFFIX = url.split('@@')[1].split('&')[0] if '@@' in url else ""
					name += '  ('+SUFFIX+')' if len(SUFFIX) == 4 else '  ('+SUFFIX.replace('es', 'e')+')' if SUFFIX.startswith(('Staffel', 'Series', 'Movies')) else '  (Serie)'
					debug("(service.load_rebuild) ######## Control-Session for TITLE = {0} || LASTUPDATE: {1} ########".format(name, last))
					presentTIME = datetime.now()
					previousTIME = datetime(*(time.strptime(last, '%Y-%m-%d %H:%M:%S')[0:6])) # 2019-06-23 14:10:00
					newTIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					newADDON, ALLOWED = self.access_permission(url)
					if presentTIME > previousTIME + timedelta(hours=stunden):
						if ALLOWED is True:
							log("(service.load_rebuild) ######## starting ACTION for TITLE = {0} || LASTUPDATE: {1} || ADDON: {2} ########".format(name, last, newADDON))
							self.update_data(url)
							cur.execute('UPDATE stocks SET last = ? WHERE url = ?', (newTIME, url))
							conn.commit()
						else:
							log("(service.load_rebuild) ######## DO NOTHING FOR TITLE = {0} || LASTUPDATE: {1} ########".format(name, last))
							log("(service.load_rebuild) #### ERROR #### REASON = {0} ########".format(newADDON))
			except:
				conn.rollback() # Roll back any change if something goes wrong
				if enableWARNINGS:
					dialog.notification(translation(30521).format('Eintrag updaten'), translation(30522), icon, 10000)
				formatted_lines = traceback.format_exc().splitlines()
				errors += 1
				if errors >= MAX_ERRORS:
					failing("(service.load_rebuild) ERROR - ERROR - ERROR :\n{0} \n{1} \n{2} ...\n########## (now: {3}/max: {4}) ...Ending Service ##########".format(formatted_lines[1], formatted_lines[2], formatted_lines[3], errors, MAX_ERRORS))
					break
				else:
					failing("(service.load_rebuild) ERROR - ERROR - ERROR :\n{0} \n{1} \n{2} ...\n########## (now: {3}/max: {4}) ...Continuing Service ##########".format(formatted_lines[1], formatted_lines[2], formatted_lines[3], errors, MAX_ERRORS))
			finally:
				cur.close()
				conn.close()
			debug("(service.load_rebuild) ########## ... END LOOP ##########")
			if self.Monitor.waitForAbort(loop_time):
				break

	def access_permission(self, IDD, default=False):
		DATA = []
		RECORDS = self.traversing.get_records()
		DATA = [obj for obj in RECORDS['specifications'] if obj.get('route') in IDD]
		debug("(service.access_permission) XXXXX IDD : {0} XXXXX".format(IDD))
		debug("(service.access_permission) XXXXX DATA : {0} XXXXX".format(str(DATA)))
		if DATA:
			if xbmc.getCondVisibility('System.HasAddon({})'.format(DATA[0]['route'])):
				self.varSetting = xbmcaddon.Addon('{}'.format(DATA[0]['route'])).getSetting('{}'.format(DATA[0]['branch']))
				if self.varSetting in ['false', 'true']:
					self.switch = (True if self.varSetting == 'true' else False)
					return ('XXX Die Bibliothek-Funktion des Addons "{0}" ist NICHT aktiviert XXX'.format(DATA[0]['name']), self.switch) if self.switch is False else (DATA[0]['name'], self.switch)
				return ('XXX Die gesuchte Einstellung vom "{0}" wurde NICHT gefunden XXX'.format(DATA[0]['route']), default)
			return ('XXX Das benötigte Addon "{0}" ist NICHT installiert/aktiviert XXX'.format(DATA[0]['name']), default)
		return ('XXX KEINEN Eintrag in der Liste für das gesuchte Addon gefunden XXX', default)

	def update_data(self, renovate):
		debug("(service.update_data) ######## SEND COMMAND TO ADDON ########")
		xbmc.executebuiltin('RunPlugin('+renovate+')')

if __name__ == '__main__':
	KodiMonitor().start_signal()

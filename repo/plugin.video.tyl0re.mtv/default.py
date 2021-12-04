# -*- coding: utf-8 -*-

'''
    Copyright (C) 2021 realvito

    MTV Germany

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import os
import xbmc
import xbmcaddon
import xbmcvfs
import shutil
from resources.lib.common import *
from resources.lib import navigator


def run():
	SEP = os.sep
	if mode == 'root': ##### Delete complete old Userdata-Folder to cleanup old Entries #####
		DONE = False    ##### [plugin.video.tyl0re.mtv v.1.2.7] - 28.10.2020 #####
		firstSCRIPT = TRANS_PATH(os.path.join('special://home'+SEP+'addons'+SEP+addon_id+SEP+'lib'+SEP)).encode('utf-8').decode('utf-8')
		UNO = os.path.join(firstSCRIPT, 'only_at_FIRSTSTART')
		if xbmcvfs.exists(UNO):
			sourceUSER = TRANS_PATH(os.path.join('special://home'+SEP+'userdata'+SEP+'addon_data'+SEP+addon_id+SEP)).encode('utf-8').decode('utf-8')
			if xbmcvfs.exists(sourceUSER):
				try:
					xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{"addonid":"'+addon_id+'", "enabled":false}}')
					shutil.rmtree(sourceUSER, ignore_errors=True)
				except: pass
				xbmcvfs.delete(UNO)
				xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{"addonid":"'+addon_id+'", "enabled":true}}')
				xbmc.sleep(500)
				DONE = True
			else:
				xbmcvfs.delete(UNO)
				xbmc.sleep(500)
				DONE = True
		else:
			DONE = True
		if DONE is True: navigator.mainMenu()
	elif mode == 'listBroadcasts':
		navigator.listBroadcasts(url)
	elif mode == 'listSeries':
		navigator.listSeries(url, transmit)
	elif mode == 'listSeasons':
		navigator.listSeasons(url, extras)
	elif mode == 'seasonPart':
		navigator.seasonPart(url)
	elif mode == 'seasonVideos':
		navigator.seasonVideos(url, transmit)
	elif mode == 'listCharts':
		navigator.listCharts(url)
	elif mode == 'chartPart':
		navigator.chartPart(url)
	elif mode == 'listMusics':
		navigator.listMusics(url)
	elif mode == 'musicPart':
		navigator.musicPart(url)
	elif mode == 'musicVideos':
		navigator.musicVideos(url, transmit)
	elif mode == 'playCompilation':
		navigator.playCompilation(url)
	elif mode == 'listAlphabet':
		navigator.listAlphabet()
	elif mode == 'listArtists':
		navigator.listArtists(url)
	elif mode == 'artistPart':
		navigator.artistPart(url, extras)
	elif mode == 'playVideo':
		navigator.playVideo(url, transmit)
	elif mode == 'playLIVE':
		navigator.playLIVE(url)
	elif mode == 'blankFUNC':
		pass # do nothing
	elif mode == 'AddToQueue':
		navigator.AddToQueue()
	elif mode == 'clearCache':
		navigator.clearCache()
	elif mode == 'aConfigs':
		addon.openSettings()
	elif mode == 'iConfigs':
		xbmcaddon.Addon('inputstream.adaptive').openSettings()

run()

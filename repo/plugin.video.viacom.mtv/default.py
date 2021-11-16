# -*- coding: utf-8 -*-

'''
    Copyright (C) 2021 realvito

    MTV Germany (neu)

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

import xbmcaddon
from resources.lib.common import *
from resources.lib import navigator


def run():
	if mode == 'root':
		navigator.mainMenu()
	elif mode == 'listBroadcasts':
		navigator.listBroadcasts(url)
	elif mode == 'listSeasons':
		navigator.listSeasons(url, pict, transmit)
	elif mode == 'listMusics':
		navigator.listMusics()
	elif mode == 'listPlaylists':
		navigator.listPlaylists(url, page)
	elif mode == 'listEpisodes':
		navigator.listEpisodes(url, extras, transmit, page, type)
	elif mode == 'listCharts':
		navigator.listCharts()
	elif mode == 'chartVideos':
		navigator.chartVideos(url, transmit, type)
	elif mode == 'playCODE':
		navigator.playCODE(IDENTiTY)
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

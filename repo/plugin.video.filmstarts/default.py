# -*- coding: utf-8 -*-

'''
    Copyright (C) 2021 realvito

    FILMSTARTS.de

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

from resources.lib.common import *
from resources.lib import navigator


def run():
	if mode == 'root':
		navigator.mainMenu()
	elif mode == 'trailer':
		navigator.trailer()
	elif mode == 'kino':
		navigator.kino()
	elif mode == 'series':
		navigator.series()
	elif mode == 'news':
		navigator.news()
	elif mode == 'filtertrailer':
		navigator.filtertrailer(url)
	elif mode == 'filterkino':
		navigator.filterkino(url)
	elif mode == 'filterserien':
		navigator.filterserien(url)
	elif mode == 'selectionCategories':
		navigator.selectionCategories(url, type, extras)
	elif mode == 'selectionWeek':
		navigator.selectionWeek(url)
	elif mode == 'listTrailer':
		navigator.listTrailer(url, page, position)
	elif mode in ['listKino_big', 'listSeries_big']:
		navigator.listKino_big(url, page, position)
	elif mode == 'listKino_small':
		navigator.listKino_small(url, page)
	elif mode == 'listNews':
		navigator.listNews(url, page)
	elif mode == 'playVideo':
		navigator.playVideo(url, type, extras)
	elif mode == 'blankFUNC':
		pass # do nothing
	elif mode == 'aConfigs':
		addon.openSettings()

run()

# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcaddon
PY2 = sys.version_info[0] == 2


def py2_enc(s, nom='utf-8', ign='ignore'):
	if PY2:
		if not isinstance(s, basestring):
			s = str(s)
		s = s.encode(nom, ign) if isinstance(s, unicode) else s
	return s

def translation(id):
	return py2_enc(xbmcaddon.Addon().getLocalizedString(id))


class Client(object):
	CONFIG_MTVDE = {
		'via_API': 'https://neutron-api.viacom.tech/api/2.8/{}',
		'chart_API': 'https://mtv.marsl.net/demo/showdbcharts.php?{}',
		'live_M3U8': 'https://unilivemtveu-lh.akamaihd.net/i/mtvde_1@134922/master.m3u8',
		'collect_Date': 'https://neutron-api.viacom.tech/api/2.8/content-collection?types={}&orderBy=originalPublishDate&order=descending&region=DE&brand=mtv&platform=web',
		'collect_Title': 'https://neutron-api.viacom.tech/api/2.8/content-collection?types={}&orderBy=title&order=ascending&region=DE&brand=mtv&platform=web',
		'collect_Idd': 'https://neutron-api.viacom.tech/api/2.8/content-collection?{}&types={}&orderBy=originalPublishDate&order=descending&region=DE&brand=mtv&platform=web',
		'items': 'https://neutron-api.viacom.tech/api/2.8/property/items/{}?types={}&region=DE&brand=mtv&platform=web',
		'search': 'https://www.mtv.de/api/search?q={}&activeTab=All&searchFilter=site&pageNumber=0&rowsPerPage=110',
		'RELATED': 'relatedIds=2534ef73-7207-4e9b-a49a-9d1d5386bc78,7aa61362-d1cf-4818-8974-af5900abc198,c83b2a23-5f91-41bd-949a-3bc21f79c51d,'\
								'89e622aa-e85f-4b1c-9c56-b29ffcbec864,4ad67c58-9130-43d2-af1f-0217ee9dcfea,9f583945-829b-4837-acfb-035e2a3654c1,'\
								'c5f4e984-c4e6-4a09-9367-15ec0a3f1131,1f70f6b1-0988-4b36-aded-910f4e498e89',
		'EXCLUDED': 'excludeLinkIds=f74d7083-f48d-449f-8428-6503e0dff65d,da0a90e0-6dd8-45f8-8000-198703f56a0e,'\
								'c767eece-55f0-4fa1-aa35-3f575257cd38,69ef8376-bc27-4525-864a-7ce41e0dc558,8dba2ab3-9011-4c73-b8a5-ea999fad6164',
		'shortID': 'https://neutron-api.viacom.tech/api/2.8/property?shortId={}&type=musicvideo&region=DE&brand=mtv&platform=web',
		'streamREQ': 'https://media.mtvnservices.com/pmt/e1/access/index.html?uri={}&configtype=edge&ref={}',
		'music': [
		{
			'title': translation(30702),
			'id': 'relatedIds=2534ef73-7207-4e9b-a49a-9d1d5386bc78',
			'description': 'TOP ARTISTS'
		},
		{
			'title': translation(30703),
			'id': 'relatedIds=7aa61362-d1cf-4818-8974-af5900abc198',
			'description': 'HITS'
		},
		{
			'title': translation(30704),
			'id': 'relatedIds=c83b2a23-5f91-41bd-949a-3bc21f79c51d',
			'description': 'MADE IN GERMANY'
		},
		{
			'title': translation(30705),
			'id': 'relatedIds=89e622aa-e85f-4b1c-9c56-b29ffcbec864',
			'description': 'HIP HOP'
		},
		{
			'title': translation(30706),
			'id': 'relatedIds=4ad67c58-9130-43d2-af1f-0217ee9dcfea',
			'description': 'UPCOMING'
		},
		{
			'title': translation(30707),
			'id': 'relatedIds=9f583945-829b-4837-acfb-035e2a3654c1',
			'description': 'ALTERNATIVE'
		},
		{
			'title': translation(30708),
			'id': 'relatedIds=c5f4e984-c4e6-4a09-9367-15ec0a3f1131',
			'description': 'DANCE'
		},
		{
			'title': translation(30709),
			'id': 'relatedIds=1f70f6b1-0988-4b36-aded-910f4e498e89',
			'description': 'POP'
		}], # Die Kategorie = ALLE ist schon unter -RELATED- vorhanden !
		'picks': [
		{
			'title': translation(30721),
			'id': 'c=1',
			'img': '{}deutschS15.jpg',
			'description': 'DE SINGLE TOP 15'
		},
		{
			'title': translation(30722),
			'id': 'c=4',
			'img': '{}single100.jpg',
			'description': 'SINGLE TOP 100'
		},
		{
			'title': translation(30723),
			'id': 'c=7',
			'img': '{}midweekS100.jpg',
			'description': 'MIDWEEK SINGLE TOP 100'
		},
		{
			'title': translation(30724),
			'id': 'c=2',
			'img': '{}streaming.jpg',
			'description': 'STREAMING CHARTS'
		},
		{
			'title': translation(30725),
			'id': 'c=3',
			'img': '{}trendingS.jpg',
			'description': 'SINGLE TRENDING'
		},
		{
			'title': translation(30726),
			'id': 'c=10',
			'img': '{}downloadS.jpg',
			'description': 'DOWNLOAD CHARTS SINGLE'
		},
		{
			'title': translation(30727),
			'id': 'c=12',
			'img': '{}dance.jpg',
			'description': 'DANCE CHARTS'
		},
		{
			'title': translation(30728),
			'id': 'c=15',
			'img': '{}jahres.jpg',
			'description': 'JAHRESCHARTS 2020'
		}], # Die anderen Charts haben KEINE Videos, also weg damit !
	}

	def __init__(self, config):
		self._config = config

	def get_config(self):
		return self._config

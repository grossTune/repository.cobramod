# -*- coding: utf-8 -*-


class Client(object):
	SUPPORTED_ADDONS = {
		'specifications': [
		{
			"name": "DMAX Mediathek",
			"route": "plugin.video.discovery.dmax",
			"branch": "dmax_library",
			"number": 1
		},
		{
			"name": "TVNOW - V.3",
			"route": "plugin.video.rtlgroup.de",
			"branch": "tvnow_library",
			"number": 2
		},
		{
			"name": "TVNOW - DE",
			"route": "plugin.video.rtlnow",
			"branch": "tvnow_library",
			"number": 3
		}]
	}

	def __init__(self, records):
		self._records = records

	def get_records(self):
		return self._records

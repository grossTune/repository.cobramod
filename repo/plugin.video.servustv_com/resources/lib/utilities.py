# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import xbmcvfs
import shutil
import time
from datetime import datetime, timedelta
import io
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .common import *


USERTOKEN = None
USERCOUNTRY = None
REFERRER = None

def _header(send_token):
	header = {}
	header['Connection'] = 'keep-alive'
	header['Pragma'] = 'no-cache'
	header['Cache-Control'] = 'no-cache'
	header['Accept'] = 'application/json, text/javascript, */*; q=0.01'
	header['User-Agent'] = get_userAgent()
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'en-US,en;q=0.8,de;q=0.7'
	header['Host'] = 'api.redbull.tv'
	if REFERRER:
		header['Referer'] = REFERRER
	if USERTOKEN and send_token:
		header['Authorization'] = USERTOKEN
	return header

class Transmission(object):

	def __init__(self):
		self.maxTokenTime = tokenDelay * 60 * 60 # max. Token-Time (Seconds) before clear the Token and delete Token-File [60*60 = 1 hour | 360*60 = 6 hours | 720*60 = 12 hours]
		self.tempTO_folder = tempTN
		self.token_file = tokenFile
		self.MATO = (time.time() - self.maxTokenTime) # Date and time now minus 'maxTokenTime'
		self.verify_ssl = (True if addon.getSetting('verify_ssl') == 'true' else False)
		self.validate_session()

	def clear_special(self, filename, foldername):
		debug_MS("(utilities.clear_special) ##### START clear_special #####")
		if filename is not None and os.path.isfile(filename):
			if xbmcvfs.exists(foldername) and os.path.isdir(foldername):
				shutil.rmtree(foldername, ignore_errors=True)
				return True
		return False

	def save_special(self, filename, auth):
		debug_MS("(utilities.save_special) ##### START save_special #####")
		if not xbmcvfs.exists(self.tempTO_folder) and not os.path.isdir(self.tempTO_folder):
			xbmcvfs.mkdirs(self.tempTO_folder)
		with io.open(filename, 'w', encoding='utf-8') as itf:
			itf.write(py2_uni(auth))
		return True

	def validate_session(self, forceRenew=False):
		global USERTOKEN
		global USERCOUNTRY
		debug_MS("(utilities.validate_session) ##### START validate_session #####")
		if self.maxTokenTime > 1 and self.token_file is not None and os.path.isfile(self.token_file):
			if os.path.getmtime(self.token_file) < self.MATO:
				debug_MS("(utilities.validate_session) XXXXX TIMEOUT FOR TOKEN - DELETE TOKENFILE XXXXX")
				self.clear_special(self.token_file, self.tempTO_folder)
				forceRenew = True
			else:
				try:
					with io.open(self.token_file, 'r', encoding='utf-8') as otf:
						support = json.load(otf)
						USERTOKEN = support.get('token')
						USERCOUNTRY = support.get('country_code')
					debug_MS("(utilities.validate_session) XXXXX NOTHING CHANGED - TOKENFILE OKAY XXXXX")
				except:
					failing("(utilities.validate_session) XXXXX !!! ERROR = TOKENFILE [TOKENFORMAT IS INVALID] = ERROR !!! XXXXX")
					forceRenew = True
		else:
			debug_MS("(utilities.validate_session) XXXXX NOTHING FOUND - SEARCH FOR NEW TOKEN XXXXX")
			forceRenew = True
		if forceRenew:
			if self.maxTokenTime == 0 and self.token_file is not None and os.path.isfile(self.token_file):
				self.clear_special(self.token_file, self.tempTO_folder)
			try:
				CODING = self.retrieveContent(SERVUSTV_API+'session?namespace=stv&category=personal_computer&os_family=http')
				debug_MS('(utilities.validate_session) XXXXX THIS IS YOUR TOKEN: {0} XXXXX'.format(CODING))
				if CODING:
					if self.maxTokenTime > 1:
						debug_MS("(utilities.validate_session) XXXXX NEW TOKENFILE CREATED - EVERTHING OKAY XXXXX")
						self.save_special(self.token_file, CODING)
					else:
						debug_MS("(utilities.validate_session) XXXXX YOU ARE IN LIVE-SESSION WITHOUT SAVING TOKEN - EVERTHING OKAY XXXXX")
					USERTOKEN = re.findall('token":"(.*?)"', CODING, re.S)[0]
					USERCOUNTRY = re.findall('country_code":"(.*?)"', CODING, re.S)[0]
			except:
				failing("(utilities.validate_session) XXXXX persToken : Gesuchtes Token-Dokument NICHT gefunden !!! XXXXX")
				dialog.notification(translation(30521).format('Token nicht gefunden'), translation(30527), icon, 12000)

	def load_credentials(self):
		return (py2_enc(USERTOKEN), py2_enc(USERCOUNTRY))

	def retrieveContent(self, url, method='GET', REF=None, send_token=None, headers=None, cookies=None, allow_redirects=True, stream=None, data=None, json=None):
		global REFERRER
		self.session = requests.Session()
		debug_MS("(utilities.retrieveContent) === URL that wanted : {0} ===".format(url))
		REFERRER = REF
		result = None
		self.session.headers.update(_header(send_token))
		try:
			if method == 'GET':
				result = self.session.get(url, headers=headers, allow_redirects=allow_redirects, verify=self.verify_ssl, stream=stream, timeout=30).text
				result = py2_enc(result)
			elif method == 'POST':
				result = self.session.post(url, headers=headers, allow_redirects=allow_redirects, verify=self.verify_ssl, data=data, json=json, timeout=30)
			debug_MS("(utilities.retrieveContent) === send url-HEADERS : {0} ===".format(str(self.session.headers)))
		except requests.exceptions.RequestException as e:
			failure = str(e)
			failing("(utilities.retrieveContent) ERROR - ERROR - ERROR : ##### {0} === {1} #####".format(url, failure))
			dialog.notification(translation(30521).format('URL'), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
			return sys.exit(0)
		return result

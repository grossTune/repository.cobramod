# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode

from Cryptodome.Cipher import DES3
from Cryptodome.Util.Padding import pad, unpad
from time import sleep
from uuid import NAMESPACE_DNS, uuid5

import xbmc
import xbmcgui


class Credential:


    def __init__(self, plugin):
        self.plugin = plugin


    def encode(self, data):
        key_handle = DES3.new(self.uniq_id(), DES3.MODE_CBC, iv=b'\0\0\0\0\0\0\0\0')
        encrypted = key_handle.encrypt(pad(data.encode('utf-8'), DES3.block_size))
        return self.plugin.b64enc(encrypted)


    def decode(self, data):
        if data == '':
            return data

        key_handle = DES3.new(self.uniq_id(), DES3.MODE_CBC, iv=b'\0\0\0\0\0\0\0\0')
        decrypted = unpad(key_handle.decrypt(self.plugin.b64dec(data)), DES3.block_size)
        return decrypted.decode('utf-8')


    def uniq_id(self):
        id = self.plugin.uniq_id()
        if len(id) > 24:
            id = id[:24]
        elif len(id) < 24:
            id = '{0}{1}'.format(id, (24 - len(id)) * '=')

        return id.encode('utf-8')


    def has_credentials(self):
        user = self.plugin.get_setting('user')
        password = self.plugin.get_setting('password')
        user_token = self.plugin.get_setting('user_token')
        return user != '' and password != '' and user_token != ''


    def set_credentials(self, user, password):
        _user = self.encode(user) if user != '' else user
        _password = self.encode(password) if password != '' else password
        self.plugin.set_setting('user', _user)
        self.plugin.set_setting('password', _password)


    def get_credentials(self):
        if self.has_credentials():
            return {
                'user': self.decode(self.plugin.get_setting('user')),
                'password': self.decode(self.plugin.get_setting('password'))
            }
        else:
            user = self.plugin.get_dialog().input('E-Mail-Adresse oder Kundennummer', type=xbmcgui.INPUT_ALPHANUM)
            password = self.plugin.get_dialog().input('Passwort', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
            if len(password) == 4:
                return {
                    'user': user,
                    'password': password
                }
        return {}


    def clear_credentials(self):
        user, password, user_token = '', '', ''
        self.plugin.set_setting('user', user)
        self.plugin.set_setting('password', password)
        self.plugin.set_setting('user_token', user_token)

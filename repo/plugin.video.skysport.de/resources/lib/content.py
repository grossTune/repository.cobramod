# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from base64 import b64decode
from bs4 import BeautifulSoup, element as bs4Element
from json import load as json_load, loads as json_loads
from re import compile as re_compile, search as re_search
from requests import get as requests_get, post as requests_post

import xbmcplugin

try:
    from html.parser import HTMLParser
    from urllib.parse import urljoin as urllib_urljoin
    from xbmcvfs import translatePath as xbmcvfs_translatePath
except:
    from HTMLParser import HTMLParser
    from urlparse import urljoin as urllib_urljoin
    from xbmc import translatePath as xbmcvfs_translatePath


class Content:


    def __init__(self, plugin, credential):
        self.plugin = plugin
        self.credential = credential

        self.base_url = 'https://sport.sky.de'
        self.htmlparser = HTMLParser()
        self.live_hls_url = 'https://websitefreestreaming.akamaized.net/11111_ssnweb/index.m3u8'
        self.nav_json = json_load(open(xbmcvfs_translatePath('{0}/resources/navigation.json'.format(self.plugin.addon_path))))
        self.sky_sport_news_icon = '{0}/resources/skysport_news.jpg'.format(xbmcvfs_translatePath(self.plugin.addon_path))
        self.user_agent = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'


    def rootDir(self):
        url = self.plugin.build_url({'action': 'playLive'})
        self.addVideo('Sky Sport News HD', url, self.sky_sport_news_icon)

        url = self.plugin.build_url({'action': 'listHome'})
        self.addDir('Home', url)

        for item in self.nav_json:
            action = item.get('action', 'showVideos')
            if action == 'showVideos':
                url = self.plugin.build_url({'action': action, 'path': item.get('path'), 'show_videos': 'false'})
            else:
                url = self.plugin.build_url({'action': action, 'path': item.get('path'), 'hasitems': 'true' if item.get('children', None) is not None else 'false'})

            self.addDir(item.get('label'), url)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def addDir(self, label, url, icon=None):
        self.addVideo(label, url, icon, True)


    def addVideo(self, label, url, icon, isFolder=False):
        li = self.plugin.get_listitem()
        li.setLabel(label)
        li.setArt({'icon': icon, 'thumb': icon})
        li.setInfo('video', {})
        li.setProperty('IsPlayable', str(isFolder))

        xbmcplugin.addDirectoryItem(handle=self.plugin.addon_handle, url=url, listitem=li, isFolder=isFolder)


    def listHome(self):
        html = requests_get(self.base_url).text
        soup = BeautifulSoup(html, 'html.parser')

        for item in soup('div', 'sdc-site-tile--has-link'):
            videoitem = item.find('span', {'class': 'sdc-site-tile__badge'})
            if videoitem is not None and videoitem.find('path') is not None:
                headline = item.find('h3', {'class': 'sdc-site-tile__headline'})
                label = headline.span.string
                url = self.plugin.build_url({'action': 'playVoD', 'path': headline.a.get('href')})
                icon = item.img.get('src')
                self.addVideo(label, url, icon)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def listSubnavi(self, path, hasitems, items_to_add=None):
        if hasitems == 'false':
            url = urllib_urljoin(self.base_url, path)
            html = requests_get(url).text
            soup = BeautifulSoup(html, 'html.parser')

            for item in soup('a', 'sdc-site-directory__content'):
                if items_to_add and item.get('href') not in items_to_add:
                    continue

                label = item.span.string
                url = self.plugin.build_url({'action': 'showVideos', 'path': '{0}-videos'.format(item.get('href')), 'show_videos': 'false'})
                self.addDir(label, url)
        else:
            items = None
            for nav_item in self.nav_json:
                if nav_item.get('path') == path:
                    items = nav_item.get('children')

            if items:
                for item in items:
                    action = item.get('action') if item.get('action', None) else 'showVideos'
                    if action == 'listSubnavi':
                        url = self.plugin.build_url({'action': action, 'path': item.get('path'), 'hasitems': 'true' if item.get('children', None) else 'false', 'items_to_add': item.get('includes')})
                    else:
                        url = self.plugin.build_url({'action': action, 'path': item.get('path'), 'show_videos': 'true' if item.get('show_videos', None) is None or item.get('show_videos') == 'true' else 'false'})
                    self.addDir(item.get('label'), url)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def showVideos(self, path, show_videos):
        url = urllib_urljoin(self.base_url, path)
        html = requests_get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        nav = soup.find('nav', {'aria-label': 'Videos:'})

        if show_videos == 'false' and nav is not None:
            for item in nav.findAll('a'):
                label = item.string
                url = self.plugin.build_url({'action': 'showVideos', 'path': item.get('href'), 'show_videos': 'true'})
                if label is not None and label != '':
                    self.addDir(label, url)
        else:
            for item in soup.find_all('div', class_=re_compile('^sdc-site-tiles__item sdc-site-tile sdc-site-tile--has-link')):
                link = item.find('a', {'class': 'sdc-site-tile__headline-link'})
                label = link.span.string
                url = self.plugin.build_url({'action': 'playVoD', 'path': link.get('href')})
                icon = item.img.get('src')
                self.addVideo(label, url, icon)

        xbmcplugin.endOfDirectory(self.plugin.addon_handle, cacheToDisc=True)


    def getVideoConfigFromCache(self, path):
        return self.plugin.cache.cacheFunction(self.getVideoConfig, path)


    def getVideoConfig(self, path):
        video_config = dict()

        url = urllib_urljoin(self.base_url, path)
        html = requests_get(url).text
        soup = BeautifulSoup(html, 'html.parser')

        div = soup.find('div', {'class': 'sdc-site-video'})
        if div:
            video_config.update(dict(
                                    account_id=div.get('data-account-id'),
                                    id=div.get('data-sdc-video-id'),
                                    auth_config=json_loads(div.get('data-auth-config')),
                                    originator_handle=div.get('data-originator-handle'),
                                    package_name=div.get('data-package-name')
                                    ))

        if not video_config:
            scripts = soup.findAll('script')
            for script in scripts:
                if hasattr(bs4Element, 'Script') and isinstance(script.string, bs4Element.Script):
                    script = script.string
                else:
                    script = script.text

                match = re_search('data-account-id="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(account_id=match.group(1)))

                match = re_search('data-sdc-video-id="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(id=match.group(1)))

                match = re_search('data-auth-config="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(auth_config=json_loads(self.htmlparser.unescape(match.group(1)))))

                match = re_search('data-originator-handle="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(originator_handle=match.group(1)))

                match = re_search('data-package-name="([^"]*)"', script)
                if match is not None:
                    video_config.update(dict(package_name=match.group(1)))

                video_config.update(dict(user_token_required=True))

        return video_config


    def playVoD(self, path):
        video_config = self.getVideoConfigFromCache(path)
        if video_config:
            li = self.getVideoListItem(video_config)
        else:
            li = self.plugin.get_listitem()
        xbmcplugin.setResolvedUrl(self.plugin.addon_handle, True, li)


    def playLive(self):
        li = self.getVideoListItem(None)
        xbmcplugin.setResolvedUrl(self.plugin.addon_handle, True, li)


    def getVideoListItem(self, video_config):
        li = self.plugin.get_listitem()

        if not video_config:
            url = self.live_hls_url
            li.setPath('{0}|{1}'.format(url, self.user_agent))
        else:
            video_config = self.getToken(video_config)
            if video_config.get('user_token_required') and not self.plugin.get_setting('user_token'):
                self.plugin.dialog_notification('Login erforderlich')
            elif self.plugin.get_setting('booked_packages') and video_config.get('package_name') and video_config.get('package_name') not in self.plugin.get_setting('booked_packages').split(','):
                self.plugin.dialog_notification('Paket "{0}" erforderlich'.format(video_config.get('package_name')))
            elif not video_config.get('token'):
                self.plugin.dialog_notification('Auth-Token konnte nicht abgerufen werden')
            else:
                url = self.getUrl(video_config)
                li.setPath('{0}|{1}'.format(url, self.user_agent))

        return li


    def getUrl(self, video_config):
        url = 'https://edge-auth.api.brightcove.com/playback/v1/accounts/{0}/videos/ref%3A{1}'.format(video_config.get('account_id'), video_config.get('id'))
        res = requests_get(url, headers=dict(Authorization='Bearer {0}'.format(video_config.get('token'))))
        video = dict()
        for source in res.json().get('sources'):
            if not source.get('width'):
                continue
            if not video or video.get('width') < source.get('width'):
                video = source
        return video.get('src')


    def getToken(self, video_config):
        headers = video_config.get('auth_config').get('headers')
        headers.update(dict(Authorization=b64decode(headers.get('Authorization'))))
        data = dict(fileReference=video_config.get('id'), v='1', originatorHandle=video_config.get('originator_handle'))
        if video_config.get('user_token_required'):
            data.update(dict(userToken=self.plugin.get_setting('user_token')))
        res = requests_post(video_config.get('auth_config').get('url'), headers=headers, data=data)
        if res.status_code == 200:
            video_config.update(dict(token=res.text[1:-1]))
        return video_config


    def login(self):
        data = self.credential.get_credentials()
        res = requests_post('https://auth.sport.sky.de/login', data=dict(user=data.get('user'), pin=data.get('password')))
        if res.status_code == 200:
            self.credential.set_credentials(data.get('user'), data.get('password'))
            user_token = res.text[1:-1]
            self.plugin.set_setting('user_token', user_token)
            self.plugin.set_setting('login_acc', data.get('user'))
            packages = json_loads(self.plugin.b64dec(user_token.split('.')[1])).get('packages')
            self.plugin.set_setting('booked_packages', ','.join(packages))
            self.plugin.dialog_notification('Anmeldung erfolgreich')
        else:
            self.plugin.dialog_notification('Anmeldung nicht erfolgreich')


    def logout(self):
        self.credential.clear_credentials()
        self.plugin.set_setting('login_acc', '')
        self.plugin.set_setting('booked_packages', '')
        self.plugin.dialog_notification('Abmeldung erfolgreich')


    def clearCache(self):
        self.plugin.cache.delete('%')
        self.plugin.dialog_notification('Leeren des Caches erfolgreich')

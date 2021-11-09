# -*- coding: utf-8 -*-

# 2021-02-27

import time
import requests
from resources.lib.requestHandler import cRequestHandler
from scrapers.modules.tools import cParser
from scrapers.modules import cleantitle, source_utils
from resources.lib.control import quote_plus, urlparse


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0'
        self.base_link = 'https://www.alleserien.com/'
        self.search_link = 'https://alleserien.com/search?search=%s'
        self.link_url_movie = '/film-getpart'

    def run(self, titles, year, season=0, episode=0, imdb='', hostDict=None):
        sources = []
        sUrl = ''
        t = [cleantitle.get(i) for i in titles if i]
        fromYear = ''
        toYear = ''
        if year != 0:
            fromYear = int(year)-1
            toYear = int(year)+1

        for title in titles:
            try:
                entryUrl = self.search_link % quote_plus(title)
                sHtmlContent = cRequestHandler(entryUrl, ignoreErrors=True).request()
                isMatch, url = cParser.parseSingleResult(sHtmlContent, ",url.*?'([^']+)")
                isMatch, token = cParser.parseSingleResult(sHtmlContent, "token':'([^']+)',")
                oRequest = cRequestHandler(url, ignoreErrors=True)
                oRequest.addParameters('search', title)
                page = '1'
                stype = 'Alle'
                sortBy = 'latest'
                oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
                oRequest.addParameters('_token', token)
                oRequest.addParameters('from', 1900)
                oRequest.addParameters('page', page)
                oRequest.addParameters('rating', 0)
                oRequest.addParameters('sortBy', sortBy)
                oRequest.addParameters('to', time.strftime('%Y', time.localtime()))
                oRequest.addParameters('type', stype)
                sHtmlContent = oRequest.request()
                pattern = '<a title=[^>]"(.*?)" href=[^>]"([^"]+).*?src=[^>]"([^"]+).*?sh1[^>]">(\d{4})'
                isMatch, aResult = cParser.parse(sHtmlContent, pattern)
                if not isMatch: continue
                if season >= 1:
                    for sName, sUrl, sThumbnail, sYear in aResult:
                        sUrl = sUrl[:-1] if cleantitle.get(sName[:-1]) in t and 'folge' in sUrl[:-1].lower() else None
                        if not sUrl: continue
                        sHtmlContent = cRequestHandler(sUrl).request()
                        pattern = '<div[^>]class="collapse[^>]m.*?id="s([\d]+)">'
                        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
                        if not isMatch or not str(season) in str(aResult): return sources
                        pattern = 'id="s%s">.*?</table>' % season
                        isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
                        if not isMatch: return sources
                        isMatch, aResult = cParser.parse(sContainer, "href = '([^']+).*?episodeNumber.*?>([\d]+)")
                        url = [i[0] for i in aResult if i[1] == str(episode)]
                        if not url: continue
                        else:
                            sUrl = url[0]
                            break

                else:
                    for sName, sUrl, sThumbnail, sYear in aResult:
                        sUrl = sUrl[:-1] if cleantitle.get(sName[:-1]) in t and fromYear <= int(sYear) <= toYear and 'filme' in sUrl[:-1].lower() else None
                        # 'https://alleserien.com/phantastische-tierwesen-und-wo-sie-zu-finden-sind-filme-stream-hd-deutsch-zusehen'
                        if not sUrl: continue
                        else:
                            break
            except:
                pass

            if not sUrl: return sources
            try:
                #url = 'https://alleserien.com/phantastische-tierwesen-und-wo-sie-zu-finden-sind-filme-stream-hd-deutsch-zusehen'
                sHtmlContent = cRequestHandler(sUrl, ignoreErrors=True).request()
                isMatch, sUrl = cParser().parseSingleResult(sHtmlContent, '<iframe[^>]src="([^"]+)')
                if isMatch:
                    if 'alleserien' in sUrl:
                        oRequest = cRequestHandler(sUrl + '?do=getVideo', ignoreErrors=True)
                        oRequest.addHeaderEntry('Origin', 'http://alleserienplayer.com')
                        oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
                        oRequest.addParameters('r', self.base_link)
                        oRequest.addParameters('hash', sUrl[47:]) # d95706dcb85e7a82fd5b9fb68127f7c
                        sHtmlContent = oRequest.request()
                        isMatch, aResult = cParser().parse(sHtmlContent, 'file":"([^"]+).*?label":"([^"]+)')
                        if isMatch:
                            for url, quality in aResult:
                                valid, hoster = source_utils.is_host_valid(sUrl, hostDict)
                                if not valid: direct = True
                                else: direct = False
                                sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': url, 'direct': direct})

            except:
                pass

            finally:
                return sources


    def resolve(self, url):
        try:
            url = self.check_302(url)
            if url: return url + '|User-Agent=' + self.user_agent
            return
        except:
            return

    def check_302(self, url):
        try:
            host = urlparse(url).netloc
            headers_dict = {'User-Agent': self.user_agent, 'Host': host, 'Range': 'bytes=0-',
                            'Connection': 'keep-alive',
                            'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5'}
            r = requests.get(url, allow_redirects=False, headers=headers_dict, timeout=7)
            if 300 <= r.status_code <= 400:
                url = r.headers['Location']
            elif 400 <= r.status_code:
                url = ''
            else:
                url = url

            return url
        except:
            return


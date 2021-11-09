# -*- coding: UTF-8 -*-

#2021-02-27

import re
from resources.lib.requestHandler import cRequestHandler
from scrapers.modules import cleantitle, dom_parser, source_utils
from scrapers.modules.tools import cParser
from resources.lib.control import urlparse, urljoin, getSetting, quote_plus

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['hdfilme.cx']
        self.base_link = 'https://hdfilme.cx'
        self.search_link = '/search?key=%s'
        self.search_api = self.base_link + '/search'
        self.get_link = 'movie/load-stream/%s/%s?'


    def run(self, titles, year, season=0, episode=0, imdb='', hostDict=None):
        sources = []
        url = ''
        t = [cleantitle.get(i) for i in set(titles) if i]
        for title in titles:
            try:
                title = cleantitle.query(title)
                query = self.search_link % (quote_plus(title))
                query = urljoin(self.base_link, query)
                oRequest = cRequestHandler(query)
                oRequest.addHeaderEntry('Referer', self.base_link + '/')
                oRequest.addHeaderEntry('Host', self.domains[0])
                oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')
                content = oRequest.request()
                searchResult = dom_parser.parse_dom(content, 'div', attrs={'class': 'body-section'})

                if season == 0: #movie
                    years = ('%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0')
                    results = re.findall(r'title-product.*?href=\"(.*?)\" title=\"(.*?)\sstream.*?(\d{4})',
                                         searchResult[0].content, flags=re.DOTALL)
                    for x in range(0, len(results)):
                        if results[x][2] in years:
                            title = cleantitle.get(results[x][1])
                            if any(i in title for i in t):
                                url = (results[x][0]) + '/deutsch'
                                break
                    if url: break

                else: #tvshow
                    results = re.findall(r'title-product.*?href=\"(.*?)\" title=\"(.*?)\"\>.*?(\d{4})',
                                         searchResult[0].content, flags=re.DOTALL)
                    #TODO
                    for x in range(0, len(results)):
                        if not year == results[x][2]: continue
                        title = cleantitle.get(results[x][1])
                        if any(i in title for i in t):
                            if "staffel0" + str(season) in title or "staffel" + str(season) in title:
                                if not 'special' in title and not 'special' in i and year == results[x][2]:
                                    url = (results[x][0])
                                    break

                    for x in range(0, len(results)): # ohne 'year'
                        title = cleantitle.get(results[x][1])
                        if any(i in title for i in t):
                            if "staffel0" + str(season) in title or "staffel" + str(season) in title:
                                if not 'special' in title and not 'special' in i:
                                    url = (results[x][0])
                                    break

                    if url:
                        urlWithEpisode = url + '/folge-%s' % episode
                        url = urljoin(self.base_link, urlWithEpisode)
                        break
            except:
                 pass

        # print (url +'\n') # test only

        try:
            if not url: return sources
            #u'https://hdfilme.cc/the-poison-rose-dunkle-vergangenheit-14882-stream/deutsch'
            query = urljoin(self.base_link, url)
            oRequest = cRequestHandler(query)
            oRequest.addHeaderEntry('Host', self.domains[0])
            oRequest.addHeaderEntry('Upgrade-Insecure-Requests', '1')
            sHtmlContent = oRequest.request()
            pattern = 'data-movie-id="(\d+).*?data-episode-id="(\d+)"'
            isMatch, aResult = cParser().parse(sHtmlContent, pattern)
            if isMatch:
                movie_id = aResult[0][0]
                episode_id = aResult[0][1]
            else: return sources

            for server in ['']: #, 'server=1']: # temp. disabled
                #'movie/load-stream/14882/130355?'
                link = self.get_link % (movie_id,episode_id ) + server
                link = urljoin(self.base_link, link)
                oRequest = cRequestHandler(link)
                oRequest.addHeaderEntry('Referer', urljoin(self.base_link, url))
                oRequest.addHeaderEntry('Host', self.domains[0])
                oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
                moviesource = oRequest.request()
                if not moviesource: continue
                if server == '':
                    #'https://load.hdfilme.ws/playlist/203829575d4e8d6602a69a746d7dacf4/203829575d4e8d6602a69a746d7dacf4.m3u8'
                    isMatch, hUrl = cParser().parse(moviesource, 'urlVideo = "([^"]+)')
                    if not isMatch: continue
                    m3u8_url =  hUrl[0]
                    m3u8_base_url = urlparse(m3u8_url).scheme + '://' + urlparse(m3u8_url).netloc
                    oRequest = cRequestHandler(m3u8_url)
                    oRequest.addHeaderEntry('Referer', urljoin(self.base_link, url))
                    oRequest.addHeaderEntry('Origin', self.domains[0])
                    sHtmlContent = oRequest.request()
                    pattern = 'RESOLUTION=\d+x([\d]+)([^#]+)'
                    isMatch, aResult = cParser().parse(sHtmlContent, pattern)

                    if isMatch:
                        for _quality, url in aResult:
                            if not 'http' in url: url = urljoin(m3u8_base_url, url)
                            url = url +'|' + query
                            quality = 'SD'
                            if "1080" in _quality or "720" in _quality:
                                quality = _quality +'p'
                            sources.append({'source': 'HDFILME.WS', 'quality': quality, 'language': 'de',
                                                'url': url, 'direct': True, 'debridonly': False, 'info': 'S0', 'local': True})

            #     if server == 'server=1':
            #         continue # no server 1
            #         foundsources = re.findall('({"file".+?})', moviesource)
            #         if foundsources == []: continue
            #         #foundsource = []
            #         for i in foundsources:
            #             sourcelink = json.loads(i.replace('\'', '"'))
            #             if 'error' in sourcelink['file']: continue
            #             url = sourcelink['file']
            #             #quality = 'SD'
            #             if sourcelink['label'] == '1080p' or sourcelink['label'] == '720p':
            #                 quality = sourcelink['label']
            #                 sources.append({'source': 'gvideo', 'quality': quality, 'language': 'de', 'url': str(url),
            #                             'direct': True, 'debridonly': False, 'info': 'S1'})
            #
            # return sources #no server 2
            #
            # server = 'server=2'
            # link = self.get_link % (movie_id, episode_id) + server
            # moviesource = self.scraper.get(urljoin(self.base_link, link), headers=headers)
            # foundsource = re.search('var sources = (\[.*?\]);', moviesource.content).group(1)
            #
            # sourcejson = json.loads(foundsource.replace('\'', '"'))
            # for sourcelink in sourcejson:
            #     try:
            #         if 'error' in sourcelink['file']: continue
            #         url = sourcelink['file'] + '|verifypeer=false&Referer=' + query
            #         #quality = 'SD'
            #         if sourcelink['label'] == '1080p' or sourcelink['label'] == '720p':
            #             quality = sourcelink['label']
            #             sources.append({'source': 'CDN', 'quality': quality, 'language': 'de', 'url': str(url),
            #                         'direct': True, 'debridonly': False, 'info': 'S2'})
            #     except:
            #         pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            import requests
            userAgent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
            referer = url.split('|')[1]
            url = url.split('|')[0]

            if 'redirector' in url:
                host = urlparse.urlparse(url).netloc
                headers_dict = {'User-Agent': userAgent, 'Host': host}
                r = requests.get(url, allow_redirects=False, headers=headers_dict)
                if 300 <= r.status_code <= 400: url = r.headers['Location']

            if 'm3u8' in url:
                headers = {'Origin': self.base_link, 'Referer': referer,
                           'User-Agent': userAgent}

                if getSetting('hlscache.enabled') == '0' or getSetting('hlscache.enabled') == '':
                    url = url + '|Origin=' + self.base_link + '&User-Agent=' + userAgent + '&Referer=' + referer
                    return url

                if getSetting('hlscache.enabled') != '0':
                    import xbmc, xbmcvfs, os
                    from scrapers.modules import hls

                    hls.cache_loader(url, headers, {'Origin': self.base_link})

                    if getSetting('hlscache.enabled') == '1':
                        ip = getSetting('hlscache.ip')
                        port = getSetting('hlscache.port')
                        new_url = 'http://' + ip + ':' + port + '/cache/hls.m3u8'
                        m3u8_file_1 = xbmc.translatePath('special://home/addons/script.module.openscrapers/cache/1')
                    else:
                        new_url = getSetting('hlscache.extWebSrv') + 'hls.m3u8'
                        m3u8_file_1 = getSetting('hlscache.nfs_path') + '1'

                    count = int(0)
                    while True:
                        if count == 5: return
                        if xbmcvfs.exists(m3u8_file_1) == 1 or os.path.isfile(m3u8_file_1):
                            return new_url
                        count += 1
                        xbmc.sleep(2500)

            else:
                url = url +'|verifypeer=false&Origin=' + self.base_link + '&Referer=' + referer
                return url
        except:
            return



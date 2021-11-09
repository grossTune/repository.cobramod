# -*- coding: UTF-8 -*-

# 2021-02-21

import json, time, re
from scrapers.modules import dom_parser, source_utils
from scrapers.modules.tools import cUtil
from resources.lib.requestHandler import cRequestHandler

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['hd-streams.org']
        self.base_link = 'https://hd-streams.org/'
        self.search = self.base_link + 'search?q=%s&movies=true&seasons=true&actors=false&didyoumean=false'


    def run(self, titles, year=0, season=0, episode=0, imdb='', hostDict=None):
        sources = []
        try:
            oRequest = cRequestHandler('https://hd-streams.org/movies')
            oRequest.removeBreakLines(False)
            oRequest.removeNewLines(False)
            sHtmlContent = oRequest.request()
            pattern = '<meta name="csrf-token" content="([^"]+)">'
            string = str(sHtmlContent)
            token = re.compile(pattern, flags=re.I | re.M).findall(string)

            if len(token) == 0:
                return #No Entry found?
            # first iteration of session object to be parsed for search
            oRequest = cRequestHandler(self.search % imdb)
            oRequest.removeBreakLines(False)
            oRequest.removeNewLines(False)
            oRequest.addHeaderEntry('X-CSRF-TOKEN', token[0])
            oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
            sHtmlContent = oRequest.request()

            content = json.loads(sHtmlContent)
            if season == 0:
                if len(content["movies"]) >= 2:
                    url = content["movies"][1]['url']
                else:
                    imdb = titles[0]
                    titles.pop(0)
                    #print 'suche nach Titel: ' + imdb
                    time.sleep(2)
                    url =  self.run(titles, imdb=imdb )

            else:
                url = content["series"][1]['seasons']
                url = [i['url'] for i in url if 'season/' + str(season) in i['url']]
                url = url[0]
        except:
            return sources

        try:
            if not url: return sources
            oRequest = cRequestHandler(url)
            oRequest.removeBreakLines(False)
            oRequest.removeNewLines(False)
            r = oRequest.request()
            token = dom_parser.parse_dom(r, "meta", attrs={"name": "csrf-token"})[0].attrs["content"]

            if "season" in url:
                pattern = "loadEpisodeStream[^>]'%s'[^>]*'(\d+)'.*?'([^']+)'.*?'([^']+)'.*?\n.*?title>([^(\s|>)]+)" % episode
                links = re.findall(pattern, r)
                links = [(episode, i[0], i[1], i[2], i[3]) for i in links]
            else:
                links = self._getMovieLinks(r)

            for e, h, quali, lang, sName in links:
                valid, hoster = source_utils.is_host_valid(sName, hostDict)
                if not valid: continue

                sources.append({'source': hoster, 'quality': quali, 'language': 'de', 'url': (url, e, h, lang, quali, token),  'direct': False})

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            sUrl, e, h, sLang, sQuality, sToken = url
            return self.getLinks(sUrl, e, h, sLang, sQuality, sToken)
        except:
            return



    def getLinks(self, sUrl, e, h, sLang, sQuality, sToken):
        import base64, json, binascii
        oRequest = cRequestHandler(sUrl + '/stream')
        # oRequest = cRequestHandler(sUrl)
        oRequest.addHeaderEntry('X-CSRF-TOKEN', sToken)
        oRequest.addHeaderEntry('X-Requested-With', 'XMLHttpRequest')
        oRequest.addHeaderEntry('Referer', sUrl)
        oRequest.addParameters('e', e)
        oRequest.addParameters('h', h)
        if sLang:
            oRequest.addParameters('lang', sLang)
        if sQuality:
            oRequest.addParameters('q', sQuality)
        oRequest.addParameters('grecaptcha', '')
        sHtmlContent = oRequest.request()
        Data = json.loads(sHtmlContent)
        tmp = Data.get('d', '') + Data.get('c', '') + Data.get('iv', '') + Data.get('f', '') + Data.get('h', '') + Data.get('b', '')
        tmp = json.loads(base64.b64decode(tmp))
        salt = binascii.unhexlify(tmp['s'])
        ciphertext = base64.b64decode(tmp['ct'][::-1])
        b = base64.b64encode(sToken[::-1].encode('utf-8'))
        tmp = cUtil.evp_decode(ciphertext, b, salt)
        tmp = json.loads(base64.b64decode(tmp))
        ciphertext = base64.b64decode(tmp['ct'][::-1])
        salt = binascii.unhexlify(tmp['s'])
        b = ''
        a = sToken
        for idx in range(len(a) - 1, 0, -2):
            b += a[idx]
        if Data.get('e', None):
            b += '1'
        else:
            b += '0'
        tmp = cUtil.evp_decode(ciphertext, b.encode('utf-8'), salt)
        return json.loads(tmp)

    def _getMovieLinks(self, content):
        links = dom_parser.parse_dom(content, "v-tabs")
        links = [i for i in links if 'alt="de"' in dom_parser.parse_dom(i, "v-tab")[0].content]
        links = dom_parser.parse_dom(links, "v-tab-item")
        links = dom_parser.parse_dom(links, "v-flex")
        links = [dom_parser.parse_dom(i, "v-btn") for i in links]
        links = [[(a.attrs["@click"], re.findall("\n(.*)", a.content)[0].strip(), i[0].content) for a in i if
                  "@click" in a.attrs] for i in links]
        links = [item for sublist in links for item in sublist]
        links = [(re.findall("\d+|de", i[0]), i[1], i[2]) for i in links]
        return [(i[0][0], i[0][1], i[2], i[0][2], i[1]) for i in links]

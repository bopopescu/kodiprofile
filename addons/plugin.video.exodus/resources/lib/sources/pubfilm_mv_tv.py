# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,urllib,urlparse,json,base64

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache


class source:
    def __init__(self):
        self.domains = ['pubfilmno1.com', 'pubfilm.com']
        self.base_link = 'http://pubfilm.com'
        self.moviesearch_link = '/%s-%s-full-hd-pubfilm-free.html'
        self.tvsearch_link = '/wp-admin/admin-ajax.php'


    def movie(self, imdb, title, year):
        try:
            title = (title.translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()

            query = self.moviesearch_link % (title, year)
            query = urlparse.urljoin(self.base_link, query)

            result = client.request(query, limit='1')

            if result == None: raise Exception()

            url = re.findall('(?://.+?|)(/.+)', query)[0]
            url = url.encode('utf-8')
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            year = re.findall('(\d{4})', premiered)[0]
            season = '%01d' % int(season) ; episode = '%01d' % int(episode)
            tvshowtitle = '%s %s: Season %s' % (data['tvshowtitle'], year, season)

            headers = {'X-Requested-With': 'XMLHttpRequest'}

            post = urllib.urlencode({'sf_value': tvshowtitle, 'action': 'ajaxy_sf', 'search': 'false'})

            url = urlparse.urljoin(self.base_link, self.tvsearch_link)

            url = client.request(url, post=post, headers=headers)
            url = json.loads(url)['post'][0]['all']
            url = [i['post_link'] for i in url if i['post_title'] == tvshowtitle][0]

            url = urlparse.urljoin(self.base_link, url)
            url = re.findall('(?://.+?|)(/.+)', url)[0]
            url += '?episode=%01d' % int(episode)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            content = re.compile('(.+?)\?episode=\d*$').findall(url)
            content = 'movie' if len(content) == 0 else 'episode'

            try: url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
            except: pass

            result = client.request(url)

            url = zip(client.parseDOM(result, 'a', ret='href', attrs = {'target': 'EZWebPlayer'}), client.parseDOM(result, 'a', attrs = {'target': 'EZWebPlayer'}))
            url = [(i[0], re.compile('(\d+)').findall(i[1])) for i in url]
            url = [(i[0], i[1][-1]) for i in url if len(i[1]) > 0]

            if content == 'episode':
                url = [i for i in url if i[1] == '%01d' % int(episode)]

            links = [client.replaceHTMLCodes(i[0]) for i in url]

            for u in links:

                try:
                    result = client.request(u)
                    result = re.findall('sources\s*:\s*\[(.+?)\]', result)[0]
                    result = re.findall('"file"\s*:\s*"(.+?)".+?"label"\s*:\s*"(.+?)"', result)

                    url = [{'url': i[0], 'quality': '1080p'} for i in result if '1080' in i[1]]
                    url += [{'url': i[0], 'quality': 'HD'} for i in result if '720' in i[1]]

                    for i in url:
                        sources.append({'source': 'gvideo', 'quality': i['quality'], 'provider': 'Pubfilm', 'url': i['url'], 'direct': True, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return



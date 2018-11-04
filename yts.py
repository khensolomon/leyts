# VERSION: 3.2
# AUTHORS: Khen Solomon Lethil (khensolomon@gmail.com)

import json
import time
import re
import math
try:
    # python3
    from urllib.parse import urlencode, unquote, quote_plus
    from html.parser import HTMLParser
except ImportError:
    # python2
    from urllib import urlencode, unquote, quote_plus
    from HTMLParser import HTMLParser

# local
from novaprinter import prettyPrinter
from helpers import retrieve_url


class yts(object):
    url = 'https://yts.am'
    name = 'YTS'
    supported_categories = {'all': 'All', 'movies': 'Movie'}

    def done(res={}):
        if res:
            print(res['name'])
        else:
            print('none')

    def search(self, keyword, cat='all'):
        api_url_list = self.url+"/api/v2/list_movies.json?%s"
        api_url_browse = self.url+"/browse-movies/{query_term}/{quality}/{genre}/{minimum_rating}/{order_by}?%s"
        api_url_detail = self.url+"/api/v2/movie_details.json?%s"
        parameter = {
            'query_term':'',
            'quality':'',
            'genre':'',
            'minimum_rating':'',
            'order_by':''}

        keyword = unquote(keyword)

        genreRegex = "(genre=\w+[\s+|$]?)"
        genre = re.findall(genreRegex, keyword)
        if len(genre):
            keyword = re.sub(genreRegex,"",keyword)
            parameter['genre'] = re.findall("=(.*)", genre[0])[0].strip()

        quality_regex = "(quality=\w+[\s+|$]?)"
        quality = re.findall(quality_regex, keyword)
        if len(quality):
            keyword = re.sub(quality_regex,"",keyword)
            parameter['quality'] = re.findall("=(.*)", quality[0])[0].strip()

        minimum_rating_regex = "(minimum_rating=?[0-9]*[.]?[0-9]+[\s+|$]?)"
        minimum_rating = re.findall(minimum_rating_regex, keyword)
        if len(minimum_rating):
            keyword = re.sub(minimum_rating_regex,"",keyword)
            parameter['minimum_rating'] = re.findall("=(.*)", minimum_rating[0])[0].strip()

        sort_by_regex = "(sort_by=\w+[\s+|$]?)"
        sort_by = re.findall(sort_by_regex, keyword)
        if len(sort_by):
            keyword = re.sub(sort_by_regex,"",keyword)
            parameter['sort_by'] = re.findall("=(.*)", sort_by[0])[0].strip()

        order_by_regex = "(order_by=\w+[\s+|$]?)"
        order_by = re.findall(order_by_regex, keyword)
        if len(order_by):
            keyword = re.sub(order_by_regex,"",keyword)
            parameter['order_by'] = re.findall("=(.*)", order_by[0])[0].strip()

        with_rt_ratings_regex = "(with_rt_ratings=\w+[\s+|$]?)"
        with_rt_ratings = re.findall(with_rt_ratings_regex, keyword)
        if len(with_rt_ratings):
            keyword = re.sub(with_rt_ratings_regex,"",keyword)
            parameter['with_rt_ratings'] = re.findall("=(.*)", with_rt_ratings[0])[0].strip()

        page_regex = "(page=\w+[\s+|$]?)"
        page = re.findall(page_regex, keyword)
        if len(page):
            keyword = re.sub(page_regex,"",keyword)
            parameter['page'] = re.findall("=(.*)", page[0])[0].strip()

        limit_regex = "(limit=.*[\s+|$]?)"
        limit = re.findall(limit_regex, keyword)
        if len(limit):
            keyword = re.sub(limit_regex,"",keyword)
            parameter['limit'] = re.findall("=(.*)", limit[0])[0].strip()

        query_term = re.sub(' +',' ',keyword).strip()
        if query_term:
            if query_term !='%%':
                parameter['query_term'] = query_term
                # parameter['query_term'] = quote_plus(query_term)

        tr_tracker = ['udp://open.demonii.com:1337/announce',
                    'udp://tracker.openbittorrent.com:80',
                    'udp://tracker.coppersurfer.tk:6969',
                    'udp://glotorrents.pw:6969/announce',
                    'udp://tracker.opentrackr.org:1337/announce',
                    'udp://torrent.gresille.org:80/announce',
                    'udp://p4p.arenabg.com:1337',
                    'udp://tracker.leechers-paradise.org:6969']
        magnet = "magnet:?xt=urn:btih:{Hashs}&{Downloads}&{Trackers}"

        data = retrieve_url(api_url_list % urlencode(parameter))
        j = json.loads(data)
        if j['data']['movie_count']:
            result_page = str(j['data']['page_number'])+'of'+str(math.ceil(j['data']['movie_count'] / j['data']['limit']))
            for movies in j['data']['movies']:
                for torrent in movies['torrents']:
                    res = {'link': magnet.format(Hashs=torrent['hash'],
                                                Downloads=urlencode({'dn': movies['title']}),
                                                Trackers='&'.join(map(lambda x: 'tr='+quote_plus(x.strip()), tr_tracker))),
                           'name': '{n} ({y}) [{q}]-[{p}]-[{i}]'.format(n=movies['title'], y=movies['year'], q=torrent['quality'], p=result_page, i=self.name),
                           'size': torrent['size'],
                           'seeds': torrent['seeds'],
                           'leech': torrent['peers'],
                           'engine_url': 'IMDB:[{rating}], Genre:[{genres}]'.format(rating=movies['rating'], genres=', '.join(movies['genres'])),
                           # 'engine_url': self.url,
                           'desc_link': movies['url']}
                    prettyPrinter(res)
        elif api_url_browse:
            if not parameter['query_term']:
                parameter['query_term'] = '0'
            if not parameter['quality']:
                parameter['quality'] = 'all'
            if not parameter['genre']:
                parameter['genre'] = 'all'
            if not parameter['minimum_rating']:
                parameter['minimum_rating'] = '0'
            if not parameter['order_by']:
                parameter['order_by'] = 'latest'
            search_url = api_url_browse.format(query_term=parameter['query_term'],
                                        quality=parameter['quality'],
                                        genre=parameter['genre'],
                                        minimum_rating=parameter['minimum_rating'],
                                        order_by=parameter['order_by'])

            if 'page' in parameter and parameter['page'] > '1':
                search_url = search_url.replace('%s','page='+parameter['page'])
            else:
                search_url = search_url.replace('?%s','')
            data = retrieve_url(search_url)
            data = re.sub("\s\s+", "", data).replace('\n', '').replace('\r', '')

            data_container = re.findall('<div class="browse-content"><div class="container">.*?<section><div class="row">(.*?)</div></section>.*?</div></div>', data)
            result_page = re.findall('<li class="pagination-bordered">(.*?)</li>', data)[0] # 1 of 5
            if result_page:
                result_page = re.sub(' +','',result_page).strip()
            else:
                result_page = '?'

            data_movie = re.findall('<div class=".?browse-movie-wrap.*?">.*?</div></div></div>', data_container[0])
            for hM in data_movie:
                movie_link = re.findall('<a href="(.*?)" class="browse-movie-link">.*?</a>', hM)[0]
                response_detail = retrieve_url(movie_link)
                response_detail = re.sub("\s\s+", "", response_detail).replace('\n', '').replace('\r', '')

                movie_id = re.findall('data-movie-id="(\d+)"', response_detail)[0]
                if movie_id:
                    api_url_detail_response = retrieve_url(api_url_detail % urlencode({'movie_id':movie_id}))
                    j = json.loads(api_url_detail_response)
                    movies = j['data']['movie']
                    for torrent in movies['torrents']:
                        res = {'link': magnet.format(Hashs=torrent['hash'],
                                                    Downloads=urlencode({'dn': movies['title']}),
                                                    Trackers='&'.join(map(lambda x: 'tr='+quote_plus(x.strip()), tr_tracker))),
                               'name': '{n} ({y}) [{q}]-[{p}]-[{i}]'.format(n=movies['title'], y=movies['year'], q=torrent['quality'], p=result_page,i='AM'),
                               'size': torrent['size'],
                               'seeds': torrent['seeds'],
                               'leech': torrent['peers'],
                               'engine_url': 'IMDB:[{rating}], Genre:[{genres}]'.format(rating=movies['rating'], genres=', '.join(movies['genres'])),
                               'desc_link': movies['url']}
                        prettyPrinter(res)
                else:
                    movie_title = re.findall('<a.*?class="browse-movie-title".*?>(.*?)</a>', hM)[0]
                    movie_year = re.findall('<div.?class="browse-movie-year".*?>(.*?)</div>', hM)[0]

                    movie_rate = re.findall('<h4.?class="rating".*?>(.*?)</h4>', hM)[0]
                    movie_rate = movie_rate.split('/')[0]

                    movie_genre = re.findall('<figcaption class=".*?">.*?(<h4>.*</h4>).*?</figcaption>', hM)[0]
                    movie_genre = re.findall('<h4>(.*?)</h4>', movie_genre)
                    # print(movie_title,movie_link,movie_year,movie_rate,movie_genre)
                    self.done()
        else:
            self.done()

if __name__=="__main__":
    # Scarlett Johansson
    # yts.search(yts,'Mandy Patinkin page=2')
    # yts.search(yts,'Shekhar Kapur')
    yts.search(yts,'love')

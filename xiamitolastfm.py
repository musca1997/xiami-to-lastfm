#! /usr/bin/env python
# -- encoding:utf - 8 --
import sys
import requests
import re
import time
import pickle
from bs4 import BeautifulSoup
import pylast
import logging
import schedule
import os
from datetime import datetime,timedelta

reload(sys)
sys.setdefaultencoding('utf-8')

# edit the config part
API_KEY = ""
API_SECRET = ""
username = ""
password_hash = pylast.md5("")

def get_xiami():

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive'}
                
    #edit your xiami url
    xiami_url = 'http://www.xiami.com/space/charts-recent/u/15438578'
    r = requests.get(xiami_url, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    
    #get tracks you played
    minutes = 5
    track_times = soup.findAll('td', class_='track_time')
    track_times = [re.search(u'\d+', track_time.text).group()
                    for track_time in track_times
                    if re.search(u'分钟前', track_time.text)]
    track_times = [int(track_time) for track_time in track_times
                    if int(track_time) < minutes]
    record_time = datetime.now() - timedelta(minutes = 5)
    record_time = record_time.strftime('%Y-%m-%d %H:%M:%S')
    track_times = [int(time.time() - track_time * 60) for track_time in track_times]
    track_number = len(track_times)
    track_htmls = soup.findAll('tr', id=re.compile('track_\d+'), limit=track_number)
    upper_htmls = [track_html.find('td', class_='song_name') for track_html in track_htmls]
    artists_html = [artist_html.findAll('a')[1:] for artist_html in upper_htmls]
    artists = []

    for artist in artists_html:
        all_artists = [str(one_artist.text) for one_artist in artist
                        if not re.search('http://i.xiami.com',
                                        one_artist['href'])]
        all_artist = '&'.join(all_artists)
        artists.append(all_artist)

    title_htmls = []
    for title_html in upper_htmls:
        title_htmls.append(title_html.findAll('a')[0:][0])

    titles = [str(title['title']) for title in title_htmls]

    #scrobble

    network = pylast.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET, username=username, password_hash=password_hash)
    for title, artist, timestamp in zip(titles, artists, track_times):
        network.scrobble(artist, title, timestamp)

def time_wait():
    schedule.every(3).minutes.do(get_xiami)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == '__main__':
    time_wait()

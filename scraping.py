import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep

def scraping_web_page(url):
    sleep(5)
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup

def get_lyrics(url):
    soup = scraping_web_page(url)
    #htmlをパースして曲名、各曲URL、アーティスト名、作詞、作曲者名を取得する
    contents = []
    contents.append(soup.find_all(href=re.compile('/song/\d+/$')))
    contents.append(soup.find_all(href=re.compile('/song/\d+/$')))
    contents.append(soup.find_all(class_=re.compile('td2')))
    contents.append(soup.find_all(class_=re.compile('td3')))
    contents.append(soup.find_all(class_=re.compile('td4')))
    informations = []
    for i, content in enumerate(contents):
        tmp_list = []
        for element in content:
            if i == 0:
                tmp_list.append(element.get('href'))
            else:
                tmp_list.append(element.string)
        informations.append(tmp_list)
    #pandas DataFrameにする
    artist_df = pd.DataFrame({
        'URL' : informations[0],
        'SongName' : informations[1],
        'Artist' : informations[2],
        'Lyricist' : informations[3],
        'Composer' : informations[4]})
    #URLにホストネームを付加
    artist_df.URL = artist_df.URL.apply(lambda x : 'https://www.uta-net.com' + x)
    #各曲のページをスクレイピングする
    contents_list = []
    for i, url in artist_df.URL.iteritems():
        contents_list.append(scraping_web_page(url))
    #歌詞、発売日、商品番号をdataframeに格納する
    lyrics = []
    sales_dates = []
    cd_nums = []
    for contents in contents_list:
        lyrics.append(contents.find(id='kashi_area').text)
        sales_dates.append(contents.find(id='view_amazon').text[4:14])
        cd_nums.append(contents.find(id='view_amazon').text[19:28])
    artist_df['Lyric'] = lyrics
    artist_df['Sales_Date'] = sales_dates
    artist_df['CD_Number'] = cd_nums
    return artist_df

def main():
    #松本隆
    base_url = "https://www.uta-net.com/lyricist/32462/0/"
    df = pd.DataFrame()
    num = 1
    #松本隆は複数ページあるので、複数ページにわたって行なう。
    while num <= 6:
        print(num)
        url = base_url+ str(num) + '/'
        df = pd.concat([df, get_lyrics(url)])
        print("concated")
        num += 1

    #松山千春
    base_url = "https://www.uta-net.com/lyricist/32318/0/"
    num = 1
    while num <= 6:
        print(num)
        url = base_url+ str(num) + '/'
        df = pd.concat([df, get_lyrics(url)])
        print("concated")
        num += 1

    df = df.reset_index(drop=True) # デフォではインデックスが重複してしまい、jsonに書けない
    path = 'lyrics.json'
    df.to_json(path)

if __name__ == '__main__':
    main()

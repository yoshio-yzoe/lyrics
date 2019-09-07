# FreeTalk改善 歌詞の利用

文責：山添　2019/08/29

FreeTalkの精度を改善し、しゃべっていて楽しいAIを実現したい。

## フリートークの現状

HALとの会話は成り立っていない。
単語レベルの認識はできるが、文章になると難しい。
応答に時間がかかる。（短くて3秒、長いと40秒ほどかかる）

## 歌詞の利用

歌詞は共感性が高いことが多い。その中でも特に一般性・抽象性の高い作詞家の松本隆、松山千春の二人の歌詞をデータとして収集し、分析することを考える。分析の際

- 手がかり表現
- TF-IDF

あたりが使える可能性がある

## データ収集

[/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/scraping.py](/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/scraping.py)　を作成。

```
python3 scaping.py
```

当該ファイルにて関数get_lyricsを以下のように定義。

URLを入力すると、uta-netからスクレイピングをして、'URL', 'SongName', 'Artist', 'Lyricist', 'Composer', 'Lyric', 'Sales_Date', 'CD_Number'の8つの列を持ったpandasデータフレームが出力される。

```Python
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from time import sleep

def scraping_web_page(url):
    #攻撃とみなされるのを防ぐ
    sleep(5)
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    return soup

def get_lyrics(url):
    #uta-netから引っ張ってくることが前提
    soup = scraping_web_page(url)
    #htmlをパースして、URL、曲名、アーティスト名、作詞、作曲者名を取得する
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
    #pandasデータフレームにする
    artist_df = pd.DataFrame({
        'URL' : informations[0],
        'SongName' : informations[1],
        'Artist' : informations[2],
        'Lyricist' : informations[3],
        'Composer' : informations[4]})
    #URLにホストネームを付加
    artist_df.URL = artist_df.URL.apply(lambda x : 'https://www.uta-net.com' + x)
    #それぞれの曲のページをスクレイピングする
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
```



これを元に、scaping.pyでは松山千春・松本隆作詞の全曲についてjsonデータとして保存([/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/lyrics.json](/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/lyrics.json))



## 分析方法

- 手がかり表現
- TF-IDF

の２つが使える可能性がある。

### 手がかり表現

手がかり表現とは、”特定の文章箇所を見つける上で手がかりとなる表現”のこと

これを取得する方法として、坂地先生らによって提案されたCrossBootstrap法がある。

その概要は以下の通り。

1. CrossBootstapに「初期集合」と「十分な量の該当データ」を入力
2. CrossBootstrapが「手がかり表現の集合を出力」

初期集合というのは、手作業でも見当たるぐらいの手がかり表現。今回の場合、共感をよぶ、抽象的なポップミュージックの歌詞についての手がかり表現を得たいので、「愛してる」「恋」「寂しい」「夢」あたりだろう。

十分な量の該当データは全歌詞データを入力すれば良い。

### TF-IDF

**レアな単語が何回も出てくるようなら、文書を分類する際にその単語の重要度を上げる**という考えに基づいている。

**「tf」は（Term Frequency）の略。** 要は単語の出現頻度のこと。各文書においてその単語がどのくらい出現したのかを意味する。

*tf*=文書*A*における単語*X*の出現頻度/文書*A*における全単語の出現頻度の和



**「idf」は（Inverse Document Frequency）の略。** 単語がレアなら高い値を、色々な文書によく出現する単語なら低い値を示す。 

*idf*=*l**o**g*(全文書数/ある単語*X*を含む文書数)



tf-idfは

*tfidf*=*tf*∗*i**d**f*

である。つまり、

*t**f**i**d**f*=(単語の出現頻度)∗(各単語のレア度)

で、「その単語が当該文章によく出現するほど」、「その単語がレアなほど」大きい値を示す。ある単語Xが普段は使われないのにその文章に限っては大量に使われている、という場合、Xはその文章を特徴づけているであろうということ。(例: 普段はめったに使わない言葉、"MeCab"が大量に使われていたら、形態素解析についての文章だと予想できる。)



## 分析

### はじめに

デフォルトではmatplotlibは文字化けする。それを解消する方法をメモする。

端末に以下の例のように入力。

```bash
gpu3@gpu3-desktop:/mnt/NAS/99_個人フォルダ/yamazoe/lyrics
$ python3
Python 3.5.5 (default, Dec 18 2018, 21:32:36) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import matplotlib
>>> matplotlib.matplotlib_fname()
'/home/gpu3/.pyenv/versions/3.5.5/lib/python3.5/site-packages/matplotlib/mpl-data/matplotlibrc'
>>> matplotlib.get_configdir()
'/home/gpu3/.config/matplotlib'
>>> matplotlib.rcParams['font.family']
['sans-serif']
```

この場合、３行目の[‘sans-serif’]が現在のフォント。最初が設定ファイルのパス、２つ目がユーザー設定するフォルダ。

設定ファイルをユーザー設定するフォルダにコピーしておき、コピーした方のファイルを修正することで設定変更する。

コピーした方のファイルを開き、195行目あたりに存在するfont.familyを以下の画像のように修正する(#を取り除くのを忘れないこと)



![Screenshot from 2019-09-04 15-26-22](/mnt/NAS/99_個人フォルダ/yamazoe/Screenshot from 2019-09-04 15-26-22.png)

<div style="text-align: center;"><B>↓</B></div>

![Screenshot from 2019-09-04 15-26-54](/mnt/NAS/99_個人フォルダ/yamazoe/Screenshot from 2019-09-04 15-26-54.png)

端末に

```python
matplotlib.rcParams['font.family']
```

を入力し、きちんと変更されているか確認。

```bash
gpu3@gpu3-desktop:/mnt/NAS/99_個人フォルダ/yamazoe/lyrics
$ python3
Python 3.5.5 (default, Dec 18 2018, 21:32:36) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import matplotlib
>>> matplotlib.rcParams['font.family']
['TakaoPGothic']
```



### TF-IDF

全歌詞のTF-IDF分析を行い、ポピュラー・ミュージックによく出てくる言葉を分析した。詳しくは[/mnt/NAS/99_個人フォルダ/yamazoe/report/report_0831_yamazoe.md](/mnt/NAS/99_個人フォルダ/yamazoe/report/report_0831_yamazoe.md)にも記載している。

- 前処理なし

  前処理なしで、単純に数え上げた場合、TF-IDFを使った場合で分析。

  該当ファイルが多いので解説すると、

  - [tfidf_all.py](/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/tfidf_all.py) … 本体
    - 関数all_lyrics_tfidf(wordlist) … 文字列の入ったリストを入れると、tfidfが高い順に、pandasDataframeとして、その単語とtfidfの値を出力
    - 関数all_lyrics_count(wordlist)…文字列の入ったリストを入れると、出現回数が高い順に、pandasDataframeとして、その単語と出現回数の値を出力
  - [generating_txt.py](/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/generating_txt.py) …MeCabの処理、文字列をリスト格納する処理をしている
  - [countwords.py](/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/countwords.py) … 語数カウント。最初練習で使用しただけ
  - [TF_IDF.py](/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/TF_IDF.py) … 昨日作ったファイル。各曲ごとの重要度が高い単語を出力する。

  しかし、「て」「に」「を」「は」など、格助詞など所謂stopwordだらけになり、ほとんど分析には役に立たないと言える。また、単純数え上げでは、全角空白も数えてしまっているのでほとんど意味がない。

  - そこで、以下の前処理をすることを考える。
    - 名詞、動詞、形容詞に絞る
    - 英語のstopwordは取り除く

- 前処理あり

  上述ファイルに加え、

  - [tfidf_all_preprocessed.py](/mnt/NAS/99_個人フォルダ/yamazoe/lyrics/tfidf_all_preprocessed.py) … 本体
    - 関数generating_txt_getting_rid_of_needed_parse(text)…MeCabで各形態素ごとに分け、名詞、動詞、形容詞のみを抽出する
    - 関数process_of_English(text)…英語のstopwordを取り除く

  前処理の威力がわかるが、依然「の」「し」などが残っている。上図と比べる限り、名詞・動詞・形容詞扱いされてしまっている「の」「し」などが相当あるということである。

  
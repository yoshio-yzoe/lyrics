import numpy as np
import MeCab
import codecs
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import json
import nltk
import string
from sklearn.feature_extraction import stop_words
import re
from generating_txt import make_corpus
from generating_txt import generating_txt
from generating_txt import make_large_list
from TF_IDF import get_important_words
import matplotlib.pyplot as plt
from tfidf_all import all_lyrics_tfidf
from tfidf_all import all_lyrics_count
from lyrics_split import split_lyrics

#tfidf_all.py に前処理を加えるのを目的


def generating_txt_getting_rid_of_needed_parse(text):
    # 名詞、動詞、形容詞を残し、ほかは全てカットする
    tagger = MeCab.Tagger('-d /usr/lib/mecab/dic/mecab-ipadic-neologd')
    tagger.parse('')
    #形態素解析の結果をリストで習得、単語ごとにリストの要素に入っている
    node = tagger.parseToNode(text)
    word_list = []

    while node:
        #品詞情報を取得する
        pos = node.feature.split(",")[0]
        if pos == u"名詞" or pos == u"形容詞" or pos == u"動詞":
            word_list.append(node.feature.split(",")[6])
        node = node.next

    return " ".join(word_list)


def delete_English(text):
    #英語・数字は全て消去
    #ついでに記号等も削除
    replaced_text = '\n'.join(s.strip() for s in text.splitlines() if s != '')  # skip header by [2:]
    replaced_text = replaced_text.lower()
    replaced_text = re.sub(r'[【】]', ' ', replaced_text)       # 【】の除去
    replaced_text = re.sub(r'[（）()]', ' ', replaced_text)     # （）の除去
    replaced_text = re.sub(r'[［］\[\]]', ' ', replaced_text)   # ［］の除去
    replaced_text = re.sub(r'[@＠]\w+', '', replaced_text)  # メンションの除去
    replaced_text = re.sub(r'[qwertyuiopasdfghjklzxcvbnm]', '', replaced_text) #アルファベットの除去
    replaced_text = re.sub(r'["#$%&=-~^|{}*:;+><,._/×]', '', replaced_text) #記号の除去
    replaced_text = re.sub(r'[1234567890]', '', replaced_text) #数字の除去
    return replaced_text


if __name__ == '__main__':
    path = "lyrics.json"
    lyricistname = input("input the full name of lyricist you want to analyze, if all, write 'all'.")
    if (lyricistname == "松山千春"):
        artist_df = split_lyrics(path)[0]
    elif (lyricistname == "松本隆"):
        artist_df = split_lyrics(path)[1]
    elif (lyricistname == "阿久悠"):
        artist_df = split_lyrics(path)[2]
    elif (lyricistname == "秋元康"):
        artist_df = split_lyrics(path)[3]
    elif (lyricistname == "all"):
        artist_df = pd.read_json(path)
    lyrics = artist_df['Lyric']
    text = ' '.join(lyrics)
    text = delete_English(text)
    text = generating_txt_getting_rid_of_needed_parse(text)
    print(text)
    #tfidf.pyと違い、関数generating_txt_getting_rid_of_needed_parse内でMeCab処理を行なう
    listA = []
    listA.append(text)
    words = [w for w in text.split(" ")]
    words_tfidf_df = all_lyrics_tfidf(listA)
    plt.figure(figsize = (30,20))
    words_df = all_lyrics_count(words)
    n = 50 #Topいくつを表記するか
    ax = words_df.iloc[:n,:].plot.bar()
    ax.set_ylabel("count",fontsize=15)
    ax.set_xticklabels(
        words_df.iloc[:n,:]["noun"],
        fontsize = 10
    )
    ax.legend_.remove()
    ay = words_tfidf_df.iloc[:n,:].plot.bar()
    ay.set_ylabel("TF-IDF",fontsize=15)
    ay.set_xticklabels(
        words_tfidf_df.iloc[:n,:]["noun"],
        fontsize = 10
    )
    ay.legend_.remove()
    plt.show()

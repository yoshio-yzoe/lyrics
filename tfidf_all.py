import numpy as np
import codecs
import MeCab
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import json
from generating_txt import make_corpus
from generating_txt import generating_txt
from generating_txt import make_large_list
from TF_IDF import get_important_words
import matplotlib.pyplot as plt



def all_lyrics_tfidf(wordlist):
    vectorizer = TfidfVectorizer(max_df=1.0, min_df=0.0001, use_idf=True, token_pattern=u'(?u)\\b\\w+\\b')
    tfidf = vectorizer.fit_transform(wordlist).toarray()
    tfidf_X = tfidf.flatten()
    word_tfidf = pd.Series(tfidf_X)
    #toarray() すべての文書における単語の出現頻度をnumpy型の配列に変換する。
    feature_names = np.array(vectorizer.get_feature_names())
    #get_feature_names 出現した単語がリストに入っている。

    #pandasのSeriesに変換してvalue_counts()
    words_tfidf_df = pd.DataFrame({'noun' : feature_names.tolist(), 'tfidf' : word_tfidf.tolist()})
    return words_tfidf_df.sort_values('tfidf', ascending = False)
    #特徴的な言葉が重要度(tfidf)順に格納される

def all_lyrics_count(wordlist):
    #テキストを入れたら、それぞれの語とその出現回数(ただ数えただけ、つまりTF)を記録する。
    word_freq = pd.Series(wordlist).value_counts() #pandasのSeriesに変換してvalue_counts()
    words_df = pd.DataFrame({'noun' : word_freq.index,
                 'frequency' : word_freq.tolist()})
    return words_df

if __name__ == '__main__':

    path = "lyrics_matsuyama.json"
    lyrics = generating_txt(path)
    text = ' '.join(lyrics)
    words = [w for w in text.split(" ")]
    listA =[]
    listA.append(text)
    words_df = all_lyrics_count(words)
    words_tfidf_df = all_lyrics_tfidf(listA)
    plt.figure(figsize = (30,20))
    n = 20 #Topいくつを表記するか
    print(words_df.iloc[:n,:])
    print(words_tfidf_df.iloc[:n,:])

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

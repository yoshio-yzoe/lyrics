import re
import MeCab
import codecs
import pandas as pd




def readpndic(filename):
    with open(filename, "r", encoding='shift-jis') as dicfile:
        items = dicfile.read().splitlines()
    return {u.split(':')[0]: float(u.split(':')[3]) for u in items}


def make_wordlist(text):
    tagger = MeCab.Tagger('-d /usr/lib/mecab/dic/mecab-ipadic-neologd')
    tagger.parse('')
    node = tagger.parseToNode(text)
    word_list = []

    while node:
        #品詞情報を取得する
        pos = node.feature.split(",")[0]
        if pos == u"名詞" or pos == u"形容詞" or pos == u"動詞":
            word_list.append(node.feature.split(",")[6])
        node = node.next
    return word_list

def emotional_vectorizer(path):
    pndicfname = "pn_ja.dic"
    pndic = readpndic(pndicfname)
    artist_df = pd.read_json(path)
    lyrics = artist_df['Lyric']
    word_list = [make_wordlist(song) for song in lyrics]
    #text = ' '.join(lyrics)
    df = pd.DataFrame(columns = ['word', 'emotional vector'])
    ve = []
    vec = []
    for sentence in word_list:
        for v in sentence:
            ve.append(v)
            vec.append(pndic.get(v))
    df = pd.DataFrame(
            data={'word': ve, 'vector': vec},
            columns=['word', 'vector']
        )
    return df

if __name__ == '__main__':
    path = "lyrics.json"
    emotional_vectorizer(path).to_json("song_analyzed.json")
"""
for v in word_list:
    print(v, pndic.get(v))


tagger = MeCab.Tagger('-Ochasen -d /usr/lib/mecab/dic/mecab-ipadic-neologd')
sentencewordlist = [\
[v.split()[2] for v in tagger.parse(sentence).splitlines() \
if(len(v.split())>=3 and v.split()[3][:2] in ['名詞', '形容詞','動詞','副詞'])] \
for sentence in lyrics]

print(sentencewordlist[0][1:50])


"""

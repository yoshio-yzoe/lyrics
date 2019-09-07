import numpy as np
import codecs
from sklearn.feature_extraction.text import TfidfVectorizer
from generating_txt import make_corpus


def get_important_words(corpus):
    vectorizer = TfidfVectorizer(min_df=0.03)
    tfidf_X = vectorizer.fit_transform(corpus).toarray()
    #toarray() すべての文書における単語の出現頻度をnumpy型の配列に変換する。
    index = tfidf_X.argsort(axis=1)[:,::-1]
    #降順にソートしている
    feature_names = np.array(vectorizer.get_feature_names())
    #get_feature_names 出現した単語がリストに入っている。
    feature_words = feature_names[index]
    #特徴的な言葉が重要度順に格納される
    return feature_words

def main():
    # データの用意
    corpus = make_corpus('lyrics-tfidf-dataset.txt')
    feature_words = get_important_words(corpus)
    n = 15  # top何単語取るか
    m = len(corpus)  # 何歌詞サンプルとして抽出するか
    for fwords, target in zip(feature_words[:m,:n], corpus):
        # 各文書ごとにtarget（ラベル）とtop nの重要語を表示
        # print(news20.target_names[target])
        print(fwords)


if __name__ == '__main__':
    main()

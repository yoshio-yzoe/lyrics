import re
import MeCab


#textは文字列

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

def cut_pos(text):
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

    return word_list

def allprocess(text):
    text = delete_English(text)
    text = cut_pos(text)
    return text

if __name__ == '__main__':
    text = "私は楽しいHappyな男で、最高にExitedだが、今夜は雨でナーバスだ!?"
    print(allprocess(text))

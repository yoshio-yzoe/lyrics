
import json
import pandas as pd
import cv2
import numpy as np
import sys
from skimage.measure import compare_ssim as ssim
import pymysql.cursors
#色々面倒だったのでインスタンスをインポートするのではなくコピペした

class parameter():
    def __init__(self):
        pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
        pymysql.converters.conversions = pymysql.converters.encoders.copy()
        pymysql.converters.conversions.update(pymysql.converters.decoders)
        self.conn = pymysql.connect(
            user='yoshioyyy',
            passwd='mysql2255',
            host='127.0.1.1',
            db='parameter',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
        #self.conn.cursor().execute("CREATE TABLE caluculatedtable (word VARCHAR(255), ANGRY float(10,10), HAPPY float(10,10), SAD float(10,10))")


    def image_weightavarage(self, word):
        with open("/mnt/NAS/02_チームフォルダ/01_ハルさん/99_work/sing/imageword_dataset_new.json") as f:
            data = json.load(f) #なぜか同ディレクトリ内のファイルでは読めなかった
        df = pd.DataFrame(data)
        #df = pd.read_json('imageword_dataset_new.json')
        #重くなるので、ファイルパスが入っているほうのデータセットを使う
        images_list = np.array(list(df[df['noun'] == word].image_path)).flatten()
        #wordに関連する画像の絶対パス一覧のリスト
        if images_list.size == 0:
            print("can't do anything with this word," ,word, " doesn't contain an image file")
            return None
        else:
            img0 = cv2.imread(str(images_list[0])) #サイズを格納
            if img0 is None:
                return None
            rows, cols, channels = img0.shape
            img_ave = np.zeros((rows, cols, channels))
            i = images_list.size
            p = 0
            for image in images_list:
                img_tmp = cv2.imread(str(image))
                if img_tmp is None:
                    i -= 1
                    continue
                    p+= 1
                    print(p)
                else:
                    img_tmp = img_tmp.astype(int)
                if img_tmp.shape != img0.shape:
                    print(i , ' : the size of image files should be standardized')
                    #サイズが同じ必要がある
                    i -= 1
                    continue
                else:
                    img_ave = img_ave + i * img_tmp
                    i -= 1
                    #フォルダ内の序列が高い方が画像の信頼度が高い(Google検索の結果なので)
                    #なのでただの平均ではなく重み付けしている
            if img_ave is None:
                return None
            else:
                img_ave = img_ave / sum(range(i, images_list.size + 1))
                return img_ave

    def output(self, wordlist):
        angry = cv2.imread("/mnt/NAS/02_チームフォルダ/01_ハルさん/99_work/sing/angry_average.jpg")
        happy = cv2.imread("/mnt/NAS/02_チームフォルダ/01_ハルさん/99_work/sing/happy_average.jpg")
        sad = cv2.imread("/mnt/NAS/02_チームフォルダ/01_ハルさん/99_work/sing/sad_average.jpg")
        wlist = []
        anlist = []
        halist = []
        salist = []
        for word in wordlist:
            self.itself = self.image_weightavarage(word)
            if self.itself is None:
                pass
            else:
                try:
                    angryp = ssim(angry, self.itself, multichannel=True)
                    happyp = ssim(happy, self.itself, multichannel=True)
                    sadp = ssim(sad, self.itself, multichannel=True)
                    try:
                        with self.conn.cursor() as cursor:

                            sql = "INSERT INTO `caluculatedtable` (WORD, ANGRY, HAPPY, SAD) VALUES (%s, %s, %s, %s)"
                            cursor.execute(sql, (word, angryp, happyp, sadp))

                        # オートコミットじゃないので、明示的にコミットを書く必要がある
                        self.conn.commit()

                    finally:

                        self.conn.close()
                    """
                    wlist.append(word)
                    anlist.append(ssim(angry, self.itself, multichannel=True))
                    halist.append(ssim(happy, self.itself, multichannel=True))
                    salist.append(ssim(sad, self.itself, multichannel=True))

                    tup = (word, angryp, happyp, sadp)
                    self.dbm.INSERT_City_ID_Name(tup)
                    """
                except ValueError:
                    pass
                except pymysql.err.Error:
                    pass
        #return wlist, anlist, halist, salist


if __name__ == '__main__':
    with open("/mnt/NAS/02_チームフォルダ/01_ハルさん/99_work/sing/imageword_dataset_new.json") as f:
        data = json.load(f) #なぜか同ディレクトリ内のファイルでは読めなかった
    df = pd.DataFrame(data)
    wordlist = list(df["noun"])
    para = parameter()
    para.output(wordlist)
    """
    wlist, anlist, halist, salist = para.output(wordlist)
    df_dic = pd.DataFrame({
        'WORD' : wlist,
        'ANGRY' : anlist,
        'HAPPY' : halist,
        'SAD' : salist})
    """
    #df_dic.to_json('parameter_dict2.json')

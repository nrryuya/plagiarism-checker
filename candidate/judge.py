from janome.tokenizer import Tokenizer
from readability.readability import Document
import numpy as np
import re
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import requests
from .models import Candidate, Sim_part

# 生の文章を文に分ける
# TODO:文末の記号が除かれているのを直す


# NOTE:改行が分割されていない。
def separate_text(text):
    sentences = []
    pattern = r'？|。|！|「|」|\n|\.'
    repatter = re.compile(pattern)
    doc = filter(lambda w: len(w) > 0, re.split(repatter, text))
    for d in doc:
        sentences.append(d)
    return sentences
    print(sentences)


# 文章を文で区切ったリストにしたもの二つの類似度を判定するクラス
class Judge:

    def __init__(self, doc1, doc2):
        # parameters
        self.theta = 0.20
        self.min_size = 3
        # 元文章を文で区切ってリストにしたもの。
        self.doc1 = doc1
        self.doc2 = doc2
        # 元文章の文の数
        self.m = len(self.doc1)
        self.n = len(self.doc2)
        # 文間類似度。
        self.similarities = np.zeros((self.m, self.n))
        # 終点スコア
        self.end_scores = np.zeros((self.m, self.n))
        # ある終点スコアの状態において、道順(一つ前のマス)を記録しておく。トレースバックで使う。
        self.path = np.zeros((self.m, self.n, 2))
        # 終点候補集合。[i,j]が追加されていく
        self.candidates = []
        # 類似部分集合の文番号表記。ex : [[[1,2],[1,3],[2,4]],[[5,6],[6,7],[6,8]]]
        self.sim_parts = []
        # 類似部分集合の文章表記。 インデックスはself.candidatesと対応。
        self.sim_parts_doc = []
        # 類似スコア。類似部分集合のインデックスと対応。
        self.sim_scores = []
        # 文章同士の類似度
        self.doc_sim = 0
        # 被覆度
        self.cover = 0

    # 文間類似度リストを作成
    def set_similarities(self):
        for i in range(self.m):
            for j in range(self.n):
                words1 = self.extract_words(self.doc1[i])
                words2 = self.extract_words(self.doc2[j])
                self.similarities[i][j] = self.cal_similarity(words1, words2)
                print("set similarity for" + str(i) + self.doc1[i] + str(j) + self.doc2[j])

    # 文から名詞と動詞だけを抜き取る。和集合とかやりやすいのでセット型(つまり、単語の出現回数は考慮していない)
    def extract_words(self, sentence):
        words = set()
        t = Tokenizer()
        tokens = t.tokenize(sentence)
        # 名詞、動詞だけを取り出す
        for token in tokens:
            partOfSpeech = token.part_of_speech.split(',')[0]  # 品詞を取り出し
            if partOfSpeech in ['名詞', '動詞']:
                words.add(token.surface)
        return words

    # 文間類似度の計算
    def cal_similarity(self, words1, words2):
        intersection = words1 & words2
        union = words1 | words2
        try:
            similarity = len(intersection) / len(union)
        # 名詞も動詞も含まれない場合
        except:
            similarity = 0
        return similarity
        print("done cal_similarity for" + words1 + "/" + words2)

    # 終点スコアを計算し、その時の道順を記録する。
    def set_end_scores(self, a, b, c, d):
        print("do set_end_scores")
        for x in [a, b, c, d]:
            print(str(x))
        for i in range(a, b):
            for j in range(c, d):
                if i == 0 or j == 0:
                    values = [0,
                              0,
                              0,
                              self.similarities[i][j] - self.theta
                              ]
                else:
                    values = [0,
                              (1 - self.similarities[i - 1][j]) * self.similarities[i][j] -
                              self.theta + self.end_scores[i - 1][j],
                              (1 - self.similarities[i][j - 1]) * self.similarities[i][j] -
                              self.theta + self.end_scores[i][j - 1],
                              self.similarities[i][j] - self.theta + self.end_scores[i - 1][j - 1]
                              ]
                index_max = values.index(max(values))
                # print(index_max)
                if index_max == 0:
                    # 終点スコアが0の時は、tracebackでself.pathを呼ばないのだが、一応[0, 0]を入れておく
                    self.path[i][j][0] = 0
                    self.path[i][j][1] = 0
                    self.end_scores[i][j] = 0
                # 以下の処理、i == 0 or j == 0の時はpathに負の値が入る。tracebackではiかjが負になった場合も止める。
                elif index_max == 1:
                    self.path[i][j][0] = i - 1
                    self.path[i][j][1] = j
                    self.end_scores[i][j] = values[1]
                elif index_max == 2:
                    self.path[i][j][0] = i
                    self.path[i][j][1] = j - 1
                    self.end_scores[i][j] = values[2]
                else:
                    self.path[i][j][0] = i - 1
                    self.path[i][j][1] = j - 1
                    self.end_scores[i][j] = values[3]

    # 終点スコア>0の箇所を終点候補集合の要素とする
    def set_candidates(self):
        candidates = []
        for i in range(self.m):
            for j in range(self.n):
                if self.end_scores[i][j] > 0:
                    candidates.append([i, j])
        self.candidates = candidates

    # 最大の終点スコアの位置を取ってくる。ex : [1,3]
    def max_end_score(self):
        max_indexes = np.where(self.end_scores == self.end_scores.max())
        # 最大が複数ある場合はインデックスが若い方にする。
        max_index = [max_indexes[0][0], max_indexes[1][0]]
        return max_index

    # 終点スコアが最大の箇所からトレースバックして類似部分(sp)を構成
    def traceback(self, max_index):
        sp = []
        max_row = max_index[0]
        max_column = max_index[1]
        sp.append([max_row, max_column])

        i = max_row
        j = max_column
        while self.end_scores[i][j] != 0 and i >= 0 and j >= 0:  # set_end_scoresでi,jに負の値が入る、
            x = int(self.path[i][j][0])
            y = int(self.path[i][j][1])
            sp.insert(0, [x, y])
            i = x
            j = y
        else:
            del sp[0]
        return sp

    # 類似部分(sp)がmin_sizeより大きければ類似部分集合(sim_parts)に加える。また、類似スコアとして類似部分の終点スコアを記録する
    def add_sp(self, sp, max_index):
        if sp[-1][0] - sp[0][0] >= self.min_size and sp[-1][1] - sp[0][1] >= self.min_size:
            self.sim_parts.append(sp)
            self.sim_scores.append(self.end_scores[max_index[0]][max_index[1]])

    # 終点スコアを更新。
    # TODO:文章の後半同士で類似部分を処理し、前半同士で類似部分の処理をすると、updateにより後半の類似部分が出てきてしまうことがある
    def update_end_scores(self, sp):
        # 直前で処理した類似部分を囲う四角形の内部は全て0
        for i in range(sp[0][0], sp[-1][0] + 1):
            for j in range(sp[0][1], sp[-1][1] + 1):
                self.end_scores[i][j] = 0
        # 上で0にしたことにより影響を受ける範囲の終点スコアの更新
        self.set_end_scores(sp[-1][0] + 1, self.m, sp[-1][1] + 1, self.n)

    # 文章間類似度を計算
    def cal_doc_sim(self):
        doc_sim = 0
        for s in self.sim_scores:
            doc_sim += s
        return doc_sim

    # 被覆率を計算
    def cal_cover(self):
        cover = 0
        # 文章1,2それぞれの、類似部分集合に含まれる文の重複無しのセット
        sim_parts_doc1 = set()
        sim_parts_doc2 = set()
        for sp in self.sim_parts:
            for s in sp:
                sim_parts_doc1.add(s[0])
                sim_parts_doc2.add(s[1])

        cov1 = len(sim_parts_doc1) / len(self.doc1)
        cov2 = len(sim_parts_doc2) / len(self.doc2)
        try:
            cover = 2 * cov1 * cov2 / (cov1 + cov2)
        # 類似部分がない場合
        except:
            cover = 0
        return cover

    def make_sim_parts_doc(self):
        for sim_part in self.sim_parts:
            # ある類似部分の文番号のセット
            sp1 = set()
            sp2 = set()
            # ある類似部分の文章
            sim_part_doc1 = ""
            sim_part_doc2 = ""
            for sp in sim_part:
                sp1.add(sp[0])
                sp2.add(sp[1])
            for s in sp1:
                sim_part_doc1 += self.doc1[s]
                sim_part_doc2 += self.doc2[s]
            self.sim_parts_doc.append([sim_part_doc1, sim_part_doc2])

    # 文章間類似度と被覆率、類似部分集合をインスタンス変数に入れる
    def compute(self):
        self.set_similarities()
        self.set_end_scores(0, self.m, 0, self.n)
        self.set_candidates()

        while len(self.candidates) != 0:
            max_index = self.max_end_score()
            sp = self.traceback(max_index)
            self.add_sp(sp, max_index)
            self.update_end_scores(sp)
            self.set_candidates()

        self.make_sim_parts_doc()
        doc_sim = self.cal_doc_sim()
        cover = self.cal_cover()
        self.doc_sim = doc_sim
        self.cover = cover


def get_content(url):
    try:
        response = requests.get(url)
        doc = Document(response.text)
        soup = BeautifulSoup(doc.summary(), 'lxml')
        content = soup.text
        pattern = r'　+$|\s+$'
        repatter = re.compile(pattern)
        print("try:" + url)
        if not (content == "" or repatter.match(content)):
            print("readability worked")
            print("content: " + content)
            return content
        else:
            print("not worked like: " + content)
            content = get_body(response)
            print("content: " + content)
            return content
    except:
        return "error"


# TODO: readabilityのコードを参考に、script以外のタグも除く。
def get_body(response):
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all('script'):
        script.extract()
    content = soup.text
    return content


def judge(candidate):
    now = datetime.now(tz=pytz.timezone('Asia/Tokyo'))
    original_doc = separate_text(candidate.article.content)
    candidate_doc = separate_text(get_content(candidate.url))
    j = Judge(original_doc, candidate_doc)
    j.compute()
    # nowはmodelsの方で指定してもいいのかも
    candidate.doc_sim = j.doc_sim
    candidate.cover = j.cover
    candidate.judged_at = now
    candidate.save()
    candidate.article.judged_at = now
    candidate.article.save()
    # TODO: サイトの最終判定時を入れる
    # candidate.article.site.judged_at = now
    # candidate.article.site.save()

    for i in range(len(j.sim_parts_doc)):
        Sim_part.objects.create(candidate=candidate, original_part=j.sim_parts_doc[i][0],
                                imitated_part=j.sim_parts_doc[i][1],
                                sim_score=j.sim_scores[i])

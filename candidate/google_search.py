from janome.tokenizer import Tokenizer
import requests
import re
from bs4 import BeautifulSoup
from candidate.models import Candidate
from rss.models import Article


# TODO:文末の記号が除かれているのを直す
def separate_text(text):
    sentences = []
    pattern = r'？|。|！|\n|\.\s'
    repatter = re.compile(pattern)
    doc = filter(lambda w: len(w) > 0, re.split(repatter, text))
    for d in doc:
        sentences.append(d)
    return sentences


# 文章を文で区切ったリストにしたものから、検索キーワードのリストを作る
def make_search_words_list(doc):
    search_words_list = []
    for sentence in doc:
        words = make_search_words(sentence)
        search_words_list.append(words)
    return search_words_list


# 文から、単語を区切って検索キーワード（文字列型）を作る
# TODO: 現状動詞と名詞を抽出しているだけだが、もっと工夫したい
def make_search_words(sentence):
    words = ""
    t = Tokenizer()
    tokens = t.tokenize(sentence)
    # 名詞、動詞だけを取り出す
    for token in tokens:
        partOfSpeech = token.part_of_speech.split(',')[0]  # 品詞を取り出し
        if partOfSpeech in ['名詞', '動詞']:
            words += token.surface + " "
    return words


# 文章を文で区切ったリストにしたものから、剽窃かどうか検証するサイトのurl, titleリストを作る
def make_candidates(doc):
    candidates = []
    search_words_list = make_search_words_list(doc)
    for words in search_words_list:
        candidates.extend(make_candidates_for_words(words))
    return candidates


# TODO:すでにDBに保存されていて過去剽窃を調べたサイトは保存しないようにする
def save_candidates(article):
    # TODO: 毎回文に分割するの効率悪いからなんとかしたい（分割したやつをDBに保存するとか？）
    doc = separate_text(article.content)
    candidates = make_candidates(doc)
    for c in candidates:
        url = c[0]
        title = c[1]
        candidate = Candidate.objects.get_or_create(url=url, title=title, article=article)
        candidate.save()


# urlからそのhtmlのsoupを作る
def get_soup(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    return soup


# 特定の検索キーワードから検索結果1~10ページ目のurlリストを作る
# 「〇〇ではありませんか？」を防いで元の検索キーワードのままやらせるとかもできそう。
def get_result_pages(words):
    result_pages = []
    first_url = "https://www.google.co.jp/search?site=webhp&q=" + words
    result_pages.append(first_url)
    for i in range(1, 10):
        url = first_url + "&start=" + str(i * 10) + "&sa=N"
        result_pages.append(url)
    return result_pages


# 検索結果一覧からurl, titleリストを生成する
def get_result_list(soup):
    result_list = []
    pages = soup.select("h3 a")
    for p in pages:
        url = p.get("href")[7:]
        title = p.string
        result_list.append([url, title])
    return result_list


# 特定の検索キーワードから検索結果1~10ページ目までに出て来るサイトのurl, titleのリストを作る
def make_candidates_for_words(words):
    comp_list = []
    result_pages = get_result_pages(words)
    for url in result_pages:
        soup = get_soup(url)
        comp_list.extend(get_result_list(soup))
    return comp_list

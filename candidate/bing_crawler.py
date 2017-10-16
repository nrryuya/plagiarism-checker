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
# TODO: candidateが増えすぎるため、単語数５以下は除いているが、tf-idf等で検索ワードの精度上げたい
def make_search_words_list(doc):
    search_words_list = []
    for sentence in doc:
        words, word_num = make_search_words(sentence)
        if word_num > 5:
            search_words_list.append(words)
            print("5文字以上のため追加:" + words)
    print("検索キーワード数:" + str(len(search_words_list)))
    return search_words_list


# 文から、単語を区切って検索キーワード（文字列型）を作る
# TODO: 現状動詞と名詞を抽出しているだけだが、もっと工夫したい
def make_search_words(sentence):
    words = ""
    word_num = 0
    t = Tokenizer()
    tokens = t.tokenize(sentence)
    # 名詞、動詞だけを取り出す
    for token in tokens:
        partOfSpeech = token.part_of_speech.split(',')[0]  # 品詞を取り出し
        if partOfSpeech in ['名詞', '動詞']:
            words += token.surface + " "
            word_num += 1
    return words, word_num


# 文章を文で区切ったリストにしたものから、剽窃かどうか検証するサイトのurl, titleリストを作る
# TODO: titleは微妙にことなることがあるので、urlだけで重複除きたい
def make_candidates(doc):
    candidates = []
    search_words_list = make_search_words_list(doc)
    for words in search_words_list:
        print("search for:" + words)
        candidates.extend(make_candidates_for_words(words))
    print("重複のぞく前:" + str(len(candidates)))
    candidates = list(set(map(tuple, candidates)))
    print("重複のぞいた後:" + str(len(candidates)))
    print(candidates)
    return candidates


# TODO: urlをデコードしたい
def save_candidates(article):
    # TODO: 毎回文に分割するの効率悪いからなんとかしたい（分割したやつをDBに保存するとか？）
    doc = separate_text(article.content)
    candidates = make_candidates(doc)
    for c in candidates:
        url = c[0]
        title = c[1]
        print("try:" + title + url)
        candidate, created = Candidate.objects.get_or_create(
            url=url, article=article, defaults={'title': title})
        if created:
            candidate.save()
            print("created:" + title)
        else:
            print("not created:" + title)


# NOTE:検索エンジン変える場合はここから下をいじる

# urlからそのhtmlのsoupを作る
def get_soup(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    return soup


# 検索結果一覧からurl, titleリストを生成する
def get_result_list(soup):
    result_list = []
    pages = soup.select(".b_algo h2 a")
    for p in pages:
        url = p.get("href")
        title = p.text
        result_list.append([url, title])
    return result_list


# 特定の検索キーワードから検索結果1~3ページ目までに出て来るサイトのurl, titleのリストを作る
def make_candidates_for_words(words):
    comp_list = []
    url = "https://www.bing.com/search?q=" + words
    for i in range(3):
        soup = get_soup(url)
        result_list = get_result_list(soup)
        comp_list.extend(result_list)
        try:  # 検索結果が少なかった場合のために分岐
            url = "https://www.bing.com" + soup.select('.sb_pagN')[0].get('href')
        except:
            break
    return comp_list

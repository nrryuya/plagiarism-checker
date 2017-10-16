from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Article
import requests
import feedparser
from bs4 import BeautifulSoup

# Create your views here.
def index(request):
    return HttpResponse('HELLO!')

def check(request):
    # TODO adminでしか実行できないように制限をかける

    # ユーザを一人ずつ取り出し、紐づくURLを取得
    # users = User.objects.all()
    # for user in users:
    #     user_id = user.id
    #     if not hasattr(user, 'url'):
    #         continue
    #     url = user.url.url
    #     links = get_links(url)
    #     register_links(user_id, links)

    return HttpResponse('CHECK!')

# # TODO get_links, register_linksの定義はここで良いのか？
# def get_links(url):
#     """
#     RSSのURLを解析してリンクのリストを生成
#     :param string url: hrssのurl
#     :return list links:
#     """
#     feed = feedparser.parse(url)
#     links = []
#     # TODO 例外処理した方がいいと思うが、RSSじゃなくても.entries使える？
#     entries = feed.entries
#     for entry in entries:
#         link_url = entry.link
#         link_title = entry.title
#         links.append({'url':link_url, 'title':link_title})
#     return links
#
# def register_links(user_id, links):
#     """
#     リンクのリストを受けとり、これを解析
#     データベースに既に登録済みなら何もしない
#     未登録なら登録する
#     :param integer user_id: ユーザID
#     :param list links: 記事のリンク
#     :return:
#     """
#     user = User.objects.get(id=user_id)
#     for link in links:
#         html = requests.get(link['url']).content
#         soup = BeautifulSoup(html, "html.parser")
#         content = soup.find("body").text
#         obj, created = Article.objects.get_or_create(
#             title=link['title'],
#             url=link['url'],
#             content=content,
#             user=user
#         )

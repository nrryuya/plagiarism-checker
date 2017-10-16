from django.core.management.base import BaseCommand
from ...models import Article, Site
from django.contrib.auth.models import User
import requests
import feedparser
from bs4 import BeautifulSoup
from candidate.judge import get_content


class Command(BaseCommand):
    help = 'RSSを巡回して新着記事を登録する'

    def handle(self, *args, **options):
        # TODO adminでしか実行できないように制限をかける
        print('command start')

        # ユーザを一人ずつ取り出し、紐づくURLを取得
        users = User.objects.all()
        for user in users:
            # TODO: ForeignKeyっぽいやつに
            # if not hasattr(user, 'site'):
            #     print('not')
            #     continue
            print('has')
            sites = Site.objects.filter(user=user).order_by('id')
            for site in sites:
                links = get_links(site.url)
                register_links(site.id, links)

        print('command end')


# TODO get_links, register_linksの定義場所はここで良いか検討する
def get_links(url):
    """
    RSSのURLを解析してリンクのリストを生成
    :param string url: rssのurl
    :return list links:
    """
    feed = feedparser.parse(url)
    links = []
    # TODO 例外処理した方がいいと思うが、RSSじゃなくても.entries使える？
    entries = feed.entries
    print(feed)
    for entry in entries:
        link_url = entry.link
        link_title = entry.title
        links.append({'url': link_url, 'title': link_title})
    return links


def register_links(site_id, links):
    """
    リンクのリストを受けとり、これを解析
    データベースに既に登録済みなら何もしない
    未登録なら登録する
    :param integer site_id: サイトID
    :param list links: 記事のリンク
    :return:
    """
    # NOTE: param siteの方が早い？
    site = Site.objects.get(pk=site_id)
    for link in links:
        # <body>だけ抜き出し
        # html = requests.get(link['url']).content
        # soup = BeautifulSoup(html, "html.parser")
        # content = soup.find("body").text

        # readability使って本文抜き出し
        content = get_content(link['url'])

        obj, created = Article.objects.get_or_create(
            title=link['title'],
            url=link['url'],
            content=content,
            user=site.user,
            site=site
        )

from django.core.management.base import BaseCommand
from register.models import Profile, Site
from rss.models import Article
from candidate.models import Candidate, Sim_part
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
# from candidate.google_search import save_candidates
from candidate.bing_crawler import save_candidates


class Command(BaseCommand):
    help = '特定のサイトの全記事についてcandidateを集める'
    args = '<site_id>'

    def add_arguments(self, parser):
        parser.add_argument('--site_id', type=int)

    def handle(self, *args, **options):
        # TODO adminでしか実行できないように制限をかける
        print('command start')

        site_id = options['site_id']
        site = get_object_or_404(Site, pk=site_id)
        articles = Article.objects.filter(site=site).order_by('id')
        for article in articles:
            print("start:" + str(article))
            save_candidates(article)
        print('command end')

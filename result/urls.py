from django.conf.urls import url
from result import views

# TODO: 設定ページ（通知の設定とか）作る？
urlpatterns = [
    url(r'^top/$', views.site_list, name='file_list'),  # トップっぽいやつ。何を入れようか。
    url(r'^site/$', views.site_list, name='site_list'),  # 監視しているサイト一覧
    url(r'^articles/(?P<site_id>\d+)/$', views.article_list,
        name='article_list'),  # あるサイトに対して、監視しているページ一覧
    url(r'^candidates/(?P<site_id>\d+)/(?P<article_id>\d+)/$', views.candidate_list,
        name='candidate_list'),  # 特定の監視ページに対して、剽窃候補のページ一覧。
    url(r'^candidates/(?P<site_id>\d+)/(?P<article_id>\d+)/(?P<candidate_id>\d+)/$',
        views.result, name='result'),  # 特定の監視ページと剽窃候補のページとの比較の詳細結果。
    url(r'^mark_confirmed/(?P<site_id>\d+)/(?P<article_id>\d+)/(?P<candidate_id>\d+)/$',
        views.mark_confirmed, name='mark_confirmed'),  # 結果の確認状態を変更
    url(r'^judge_site/(?P<site_id>\d+)/$',
        views.judge_site, name='judge_site'),  # 結果の確認状態を変更
    url(r'^new/(?P<site_id>\d+)/$', views.new_articles, name='file_add'),  # rssにより新しく追加されたページ一覧
    # url(r'^add/$', views.file_edit, name='file_add'),  # 新しい監視サイトの登録ページ。これはregisterにあった。
]

from register.models import Profile, Site
from rss.models import Article
from candidate.models import Candidate, Sim_part
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.views.decorators.http import require_POST
from django.core.management import call_command


# TODO:サイトごとのページ数を渡したい
@login_required
def site_list(request):
    sites = Site.objects.filter(user=request.user).order_by('id')
    unconfirmed_num_dict = make_unconfirmed_num_dict(sites)
    context = {'user': request.user, 'sites': sites, 'unconfirmed_num_dict': unconfirmed_num_dict}
    return render(request, 'result/site_list.html', context)


# TODO: 各articleの一番類似性高いcandidateの情報を載せてソートするとかしたい
# TODO: articleが一つもない場合 has no attributeエラーになる
@login_required
def article_list(request, site_id):
    sites = Site.objects.filter(user=request.user).order_by('id')
    unconfirmed_num_dict = make_unconfirmed_num_dict(sites)
    site = get_object_or_404(Site, pk=site_id)
    articles = Article.objects.filter(site=site).order_by('id')
    context = {'user': request.user, 'sites': sites,
               'unconfirmed_num_dict': unconfirmed_num_dict, 'site': site, 'articles': articles}
    return render(request, 'result/article_list.html', context)


@login_required
def new_articles(request, site_id):
    sites = Site.objects.filter(user=request.user).order_by('id')
    unconfirmed_num_dict = make_unconfirmed_num_dict(sites)
    site = get_object_or_404(Site, pk=site_id)
    try:
        # TODO:前回確認してから新しく入ったやつ、とかにしたい
        articles = Article.objects.filter(site=site).order_by('-updated_at')[0:10]
    except:  # 記事が10個未満の時用
        articles = Article.objects.filter(site=site).order_by('-updated_at')
    context = {'user': request.user, 'sites': sites,
               'unconfirmed_num_dict': unconfirmed_num_dict, 'site': site, 'articles': articles}

    return render(request, 'result/article_list.html', context)


@login_required
def candidate_list(request, site_id, article_id):
    sites = Site.objects.filter(user=request.user).order_by('id')
    unconfirmed_num_dict = make_unconfirmed_num_dict(sites)
    site = get_object_or_404(Site, pk=site_id)
    article = get_object_or_404(Article, pk=article_id)
    candidates = Candidate.objects.filter(article=article).order_by('id')
    context = {'user': request.user, 'sites': sites, 'unconfirmed_num_dict': unconfirmed_num_dict, 'site': site,
               'article': article, 'candidates': candidates}
    return render(request, 'result/candidate_list.html', context)


@login_required
def result(request, site_id, article_id, candidate_id):
    sites = Site.objects.filter(user=request.user).order_by('id')
    unconfirmed_num_dict = make_unconfirmed_num_dict(sites)
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    sim_parts = Sim_part.objects.filter(candidate=candidate).order_by('id')
    context = {'user': request.user, 'sites': sites, 'unconfirmed_num_dict': unconfirmed_num_dict, 'site_id': site_id,
               'article_id': article_id, 'candidate': candidate, 'sim_parts': sim_parts}
    return render(request, 'result/result.html', context)


# TODO;AJAXにする
@login_required
def mark_confirmed(request, site_id, article_id, candidate_id):
    sites = Site.objects.filter(user=request.user).order_by('id')
    unconfirmed_num_dict = make_unconfirmed_num_dict(sites)
    site = get_object_or_404(Site, pk=site_id)
    article = get_object_or_404(Article, pk=article_id)
    candidates = Candidate.objects.filter(article=article).order_by('id')
    # 以下confirmedの変更
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    candidate.confirmed = not candidate.confirmed
    candidate.save()
    context = {'user': request.user, 'sites': sites, 'unconfirmed_num_dict': unconfirmed_num_dict, 'site': site,
               'article': article, 'candidates': candidates}
    return render(request, 'result/candidate_list.html', context)


def get_unconfirmed_num(site_id):
    unconfirmed_num = Article.objects.filter(site_id=site_id).count()
    # unconfirmed_num = Article.objects.filter(site_id=site_id, confirmed=Fales).count()
    return unconfirmed_num


# NOTE: 未確認類似記事数をテンプレートに出す方法下記以外にあるのか
def make_unconfirmed_num_dict(sites):
    unconfirmed_num_dict = {}
    for site in sites:
        unconfirmed_num = get_unconfirmed_num(site.id)
        unconfirmed_num_dict[site.id] = unconfirmed_num
    return unconfirmed_num_dict


# TODO: Ajaxとか使う
def judge_site(request, site_id):
    sites = Site.objects.filter(user=request.user).order_by('id')
    unconfirmed_num_dict = make_unconfirmed_num_dict(sites)
    site = get_object_or_404(Site, pk=site_id)
    # コマンド呼び出す部分
    call_command('judge_site', site_id=site_id)
    context = {'user': request.user, 'sites': sites, 'unconfirmed_num_dict': unconfirmed_num_dict}
    return render(request, 'result/site_list.html', context)

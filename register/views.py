from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .forms import UserCreateForm, ProfileForm, SiteForm, ArticleForm
from .models import Profile, Site
from rss.models import Article
from django.contrib.auth import login
from candidate.judge import get_content

# Create your views here.


def index(request):
 # TODO: hasattr(user, 'url')の返り値を
    user = request.user
    if user.is_authenticated():
        name = user.username
        # url = user.url.url
        url = Site.objects.filter(user_id=user.id)
    else:
        name = ''
        url = ''

    context = {
        'user': user,
        'name': name,
        'url': url,
    }

    return render(
        request,
        'register/index.html',
        context
    )


# TODO: ログインしていたらprofileに飛ばす
def register(request):
    user_form = UserCreateForm(None)
    context = {
        'user_form': user_form,
    }
    return render(
        request,
        'register/register.html',
        context
    )


# TODO: ログインしていたらprofileに飛ばす
@require_POST
def register_save(request):
    user_form = UserCreateForm(request.POST)
    if user_form.is_valid():
        # Userモデルの処理。ログインできるようis_staffをTrueにし保存
        user = user_form.save(commit=False)
        user.is_staff = True
        user.save()
        login(request, user)
        # TODO: ここでログインさせてからprofileを表示
        return redirect('register:profile')

    context = {
        'user_form': user_form,
    }
    return render(request, 'register/regist.html', context)


@login_required
def profile(request):
    user = request.user
    if not hasattr(user, 'profile'):
        profile_form = ProfileForm(None)
    else:
        profile_form = ProfileForm(instance=user.profile)
    # TODO: 複数をformで扱う
    # if not hasattr(user, 'site'):
    #     site_form = SiteForm(None)
    #     sites = ''
    #     print('no site')
    # else:
    #     site_form = SiteForm(instance=user.url)
    #     sites = Site.objects.filter(user_id=user.id)
    #     print('has site')
    try:
        sites = Site.objects.filter(user_id=user.id)
    except:
        pass
    if not sites:
        print('sites空')
    context = {
        'user': user,
        'profile_form': profile_form,
        # 'site_form': site_form,
        'sites': sites,
    }
    return render(
        request,
        'register/profile.html',
        context
    )


# TODO: プロフィールをセーブする時カスタマイズして使う
@login_required
@require_POST
def profile_save(request):
    user = request.user
    profile_form = ProfileForm(request.POST)
    site_form = SiteForm(request.POST)
    context = {
        'profile_form': profile_form,
        'site_form': site_form,
    }
    if not (profile_form.is_valid() and site_form.is_valid()):
        return render(request, 'register/profile.html', context)

    profile, created = Profile.objects.get_or_create(user=user)
    site, created = Site.objects.get_or_create(user=user)

    profile.plan = request.POST['plan']
    profile.save()

    site.name = request.POST["name"]
    site.url = request.POST["url"]
    site.save()

    context["changed"] = True
    return render(request, 'register/profile.html', context)


@login_required
def plan(request):
    user = request.user

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST)
        if profile_form.is_valid():
            profile, created = Profile.objects.get_or_create(user=user)
            profile.plan = request.POST['plan']
            profile.save()
            context = {
                "changed": True,
            }
            return render(request, 'register/profile.html', context)

    elif request.method == 'GET':
        if not hasattr(user, 'profile'):
            profile_form = ProfileForm(None)
        else:
            profile_form = ProfileForm(instance=user.profile)

    context = {
        'user': user,
        'profile_form': profile_form,
    }
    print(context)
    return render(
        request,
        'register/plan.html',
        context
    )


# サイトの追加及び編集
@login_required
def site_add(request, site_id=None):
    user = request.user
    added = False
    changed = False
    if site_id:   # site_id が指定されている (修正時
        site = get_object_or_404(Site, pk=site_id)
        changed = True
    else:               # site_id が指定されていない (追加時)
        site = Site()
        added = True

    if request.method == 'POST':
        site_form = SiteForm(request.POST, instance=site)
        if site_form.is_valid():
            site = site_form.save(commit=False)
            site.name = request.POST['name']
            site.url = request.POST['url']
            site.user = user
            site.save()
            # TODO: 登録後のページ変える、登録or編集しましたというアラートつける
            context = {
                "added": added,
                "changed": changed,
            }
            return render(request, 'register/profile.html', context)

    elif request.method == 'GET':
        site_form = SiteForm(instance=site)  # site インスタンスからフォームを作成

    context = {
        'user': user,
        'site_form': site_form,
    }
    return render(
        request,
        'register/site_add.html',
        context
    )


# サイトの削除
@login_required
def site_del(request, site_id):
    site = get_object_or_404(Site, pk=site_id)
    site.delete()
    return redirect('result:site_list')


# 記事の追加及び編集
@login_required
def article_add(request, site_id, article_id=None):
    site = get_object_or_404(Site, pk=site_id)
    user = request.user
    added = False
    changed = False
    if article_id:   # article_id が指定されている (修正時
        article = get_object_or_404(Article, pk=article_id)
        changed = True
        print("changed")
    else:               # article_id が指定されていない (追加時)
        article = Article()
        added = True
        print("added")

    if request.method == 'POST':
        article_form = ArticleForm(request.POST, instance=article)
        if article_form.is_valid():
            article = article_form.save(commit=False)
            article.title = request.POST['title']
            url = request.POST['url']
            article.url = url
            article.content = get_content(url)
            article.user = user
            article.site = site
            article.save()
            # TODO: 登録後のページ変える、登録or編集しましたというアラートつける
            context = {
                "site_id": site_id,
                "added": added,
                "changed": changed,
            }
            return redirect('result:article_list', site_id=site_id)

    elif request.method == 'GET':
        article_form = ArticleForm(instance=article)  # site インスタンスからフォームを作成

    context = {
        "site_id": site_id,
        "article_id": article_id,
        'user': user,
        'article_form': article_form,
    }
    return render(
        request,
        'register/article_add.html',
        context
    )


# 監視記事の削除
@login_required
def article_del(request, site_id, article_id):
    article = get_object_or_404(Article, pk=article_id)
    article.delete()
    return redirect('result:article_list', site_id=site_id)

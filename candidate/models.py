from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from rss.models import Article
# Create your models here.


class Candidate(models.Model):

    class Meta:
        db_table = 'candidates'
    # NOTE: urlをデコードしてから保存するなら、maxはこんなにいらない
    url = models.URLField(max_length=1000)
    title = models.CharField("タイトル", max_length=255)
    # クロールして保存された日
    created_at = models.DateTimeField(default=datetime.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # 最後にジャッジされた日
    judged_at = models.DateTimeField(null=True, blank=True)
    # 元記事
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    # 類似度
    doc_sim = models.FloatField(null=True)
    # 被覆度
    cover = models.FloatField(null=True)
    # 判定結果の確認済みか否か
    # confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Sim_part(models.Model):

    class Meta:
        db_table = 'sim_parts'
    created_at = models.DateTimeField(default=datetime.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    # 元文章側のの類似部分の文章
    original_part = models.TextField()
    # candidate側の類似部分の文章
    imitated_part = models.TextField()
    # 類似スコア
    sim_score = models.FloatField()

    def __str__(self):
        return content

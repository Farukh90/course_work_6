import random

from config.settings import CACHE_ENABLED
from django.core.cache import cache
from blog.models import BlogPost


def get_cached_articles():
    if not CACHE_ENABLED:
        all_articles = BlogPost.objects.filter(is_published=True)
        if all_articles.exists():
            return random.sample(list(all_articles), min(3, all_articles.count()))
        else:
            return []

    key = "index_random_articles"
    articles = cache.get(key)

    if articles is not None:
        return articles

    all_articles = BlogPost.objects.filter(is_published=True)
    if all_articles.exists():
        articles = random.sample(list(all_articles), min(3, all_articles.count()))
    else:
        articles = []
    cache.set(key, articles, 3)
    return articles

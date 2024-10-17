from django.conf import settings
from apps.models import Visitor, Article
from collections import Counter
import datetime


def most_viewed_article():
    
    visitors = Visitor.objects.filter(path__startswith='/news/')

    # Ambil ID artikel dari path
    article_ids = []
    for visitor in visitors:
        # Ambil bagian ID dari path, misalnya '/news/1/' menjadi '1'
        parts = visitor.path.split('/')
        if len(parts) > 2 and parts[2].isdigit():  # Memastikan ada ID di bagian yang benar
            article_ids.append(int(parts[2]))

    # Hitung frekuensi setiap ID artikel
    id_count = Counter(article_ids)

    # Ambil artikel dan tambahkan view_count
    articles = []
    for article in Article.objects.all():
        count = id_count.get(article.id, 0)  # Ambil jumlah tampilan, default 0
        articles.append((article, count))

    # Urutkan artikel berdasarkan jumlah tampilan terbanyak
    articles.sort(key=lambda x: x[1], reverse=True)

    return articles
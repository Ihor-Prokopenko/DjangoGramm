from .models import Tag, User
from django.core.cache import cache


def tags(request):
    search_items = cache.get('search_items')
    if search_items is None:
        search_items = list(Tag.objects.all()) + list(User.objects.all())
        cache.set('search_items', search_items, 15)
    return {'search_items': search_items}

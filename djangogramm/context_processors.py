from .models import Tag, User
from django.views.decorators.cache import cache_page


@cache_page(60 * 3)
def tags(request):
    search_items = list(Tag.objects.all()) + list(User.objects.all())
    return {'search_items': search_items}

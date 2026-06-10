from django.utils.functional import SimpleLazyObject
from .models import Collection


def collections_processor(request):
    return {"collections": SimpleLazyObject(lambda: list(Collection.objects.all()))}

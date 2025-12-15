from .models import Collection


def collections_processor(request):
    collections = Collection.objects.all()
    return {"collections": collections}

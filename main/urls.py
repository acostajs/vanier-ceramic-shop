from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path("shop/", include("shop.urls")),
    path("cart/", include("cart.urls")),
    path("account/", include("account.urls")),
    # path("contact/", include("contact.urls")),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

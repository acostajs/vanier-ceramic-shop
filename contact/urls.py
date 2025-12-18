from django.urls import path
from . import views

app_name = "contact"
urlpatterns = [
    path("", views.contact, name="contact"),
    path("submit/", views.contact_submit, name="contact_submit"),
]

from django.urls import path
from . import views

urlpatterns = [
    path("/init", views.GoogleCalendarInitView, name="initialize"),
    path("/redirect", views.GoogleCalendarRedirectView, name="getEvents"),
]
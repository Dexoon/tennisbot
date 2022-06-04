from django.urls import path
from . import views

urlpatterns = [
    path("tournament/<int:pk>/", views.tournament),
    path("tournament/<int:pk>/predictions/", views.predictions),
    path("telegram123_secret/", views.telegram),
]

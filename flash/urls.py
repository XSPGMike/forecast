from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('<str:uuid>', views.flash),
]

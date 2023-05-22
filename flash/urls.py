from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('archive', views.archive),
    path('<str:uuid>', views.flash),
]

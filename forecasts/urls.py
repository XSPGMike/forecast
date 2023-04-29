from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('archive/', views.archive, name='archive'),
    path('new/', views.new, name='new'),
    path('<str:uuid>/', views.detail, name='detail'),
    path('<str:uuid>/vote/', views.vote, name='vote'),
    path('<str:uuid>/end/', views.end, name='end'),
]

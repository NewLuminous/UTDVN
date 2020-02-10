from django.urls import path

from . import views

app_name = 'UTDVN_database'
urlpatterns = [
    path('search/', views.search, name='search'),
    path('cores/', views.cores, name='cores'),
]
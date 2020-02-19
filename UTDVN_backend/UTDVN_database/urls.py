from django.urls import path

from . import views

app_name = 'UTDVN_database'
urlpatterns = [
    path('cores/', views.cores, name='cores'),
    path('search/', views.search, name='search'),
    path('document/', views.document, name='document'),
]
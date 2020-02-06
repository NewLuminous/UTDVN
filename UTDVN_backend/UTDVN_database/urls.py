from django.urls import path

from . import views

app_name = 'UTDVN_database'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
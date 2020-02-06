from django.shortcuts import render
from django.views import generic
from .models import Thesis

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'UTDVN_database/index.html'
    context_object_name = 'latest_thesis_list'
    
    def get_queryset(self):
        return Thesis.objects.order_by('pub_year')[:20]
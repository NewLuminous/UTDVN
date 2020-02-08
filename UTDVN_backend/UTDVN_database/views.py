from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from .models import Thesis
import json
import pysolr
from .solr import connection, error

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'UTDVN_database/index.html'
    context_object_name = 'latest_thesis_list'
    
    def get_queryset(self):
        return Thesis.objects.order_by('pub_year')[:20]
    
def search(request):
    '''
    Takes a GET request containing a query and returns results from the
    connected Solr instance. The request should contain the 'q' parameter with
    a search term (i.e q=my_search_term), or a search phrase in double quotes
    (i.e q="my search phrase").
    '''
    if request.method != "GET":
        return HttpResponse(status=405)
    
    query = request.GET.get('q', '')
    if query is '':
        api_error = error.APIError(
            'Must supply a search term with the parameter "q".',
            error.ErrorType.INVALID_SEARCH_TERM
        )
        return HttpResponse(api_error.json(), status=400)
    
    try:
        json_data = json.dumps(connection.search(query))
    except pysolr.SolrError as e:
        api_error = error.APIError(
            str(e),
            error.ErrorType.SOLR_SEARCH_ERROR
        )
        return HttpResponse(api_error.json(), status=400)
    except KeyError as e:
        api_error = error.APIError(
            'An error occurred processing the request',
            error.ErrorType.UNEXPECTED_SERVER_ERROR
        )
        return HttpResponse(api_error.json(), status=500)
    except ValueError as e:
        api_error = error.APIError(
            str(e),
            error.ErrorType.SOLR_CONNECTION_ERROR
        )
        return HttpResponse(api_error.json(), status=500)
    
    return HttpResponse(json_data)
    
def cores(request):
    if request.method != "GET":
        return HttpResponse(status=405)
    
    return HttpResponse(json.dumps(connection.get_cores()), status=200)
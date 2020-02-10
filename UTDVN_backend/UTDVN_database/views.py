from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
import pysolr
from .solr import connection, error

# Create your views here.    
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
    if query == '':
        api_error = error.APIError(
            'Must supply a search term with the parameter "q".',
            error.ErrorType.INVALID_SEARCH_TERM
        )
        return JsonResponse(api_error.args(), status=400)
    
    try:
        data = connection.search(query)
    except pysolr.SolrError as e:
        api_error = error.APIError(
            str(e),
            error.ErrorType.SOLR_SEARCH_ERROR
        )
        return JsonResponse(api_error.args(), status=400)
    except KeyError as e:
        api_error = error.APIError(
            'An error occurred processing the request',
            error.ErrorType.UNEXPECTED_SERVER_ERROR
        )
        return JsonResponse(api_error.args(), status=500)
    except ValueError as e:
        api_error = error.APIError(
            str(e),
            error.ErrorType.SOLR_CONNECTION_ERROR
        )
        return JsonResponse(api_error.args(), status=500)
    
    return JsonResponse(data, safe=False)
    
def cores(request):
    if request.method != "GET":
        return HttpResponse(status=405)
    
    return JsonResponse(connection.get_cores(), safe=False, status=200)
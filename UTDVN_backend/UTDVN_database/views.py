from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
import pysolr
from .solr import connection
from .solr.error import APIError, ErrorType
from UTDVN_backend.settings import HAYSTACK_CONNECTIONS

SOLR = connection.SolrConnection(HAYSTACK_CONNECTIONS['default']['URL'])
DEFAULT_CORE = 'test'

# Create your views here.
def cores(request):
    if request.method != "GET":
        return HttpResponse(status=405)
    
    return JsonResponse(SOLR.get_core_names(), safe=False, status=200)

def search(request):
    '''
    Takes a GET request containing a query and returns results from the
    connected Solr instance.
    '''
    if request.method != "GET":
        return HttpResponse(status=405)
    
    core = request.GET.get('core', '')
    query = request.GET.get('q')
    kwargs = {
        'sort': request.GET.get('sort', ''),
        'start': request.GET.get('start', ''),
        'rows': request.GET.get('rows', ''),
        'default_field': 'title',
        'highlight_fields': 'title',
    }
    
    if core == '':
        api_error = APIError(ErrorType.INVALID_SEARCH_REQUEST)
        return JsonResponse(api_error.args(), status=400)
    
    if query is not None:
        kwargs['query'] = query
    
    try:
        response = SOLR.query(core, **kwargs)
    except pysolr.SolrError as e:
        api_error = APIError(ErrorType.SOLR_SEARCH_ERROR, str(e))
        return JsonResponse(api_error.args(), status=400)
    except KeyError:
        api_error = APIError(ErrorType.UNEXPECTED_SERVER_ERROR)
        return JsonResponse(api_error.args(), status=500)
    except ValueError:
        api_error = APIError(ErrorType.SOLR_CONNECTION_ERROR)
        return JsonResponse(api_error.args(), status=500)
    
    if 'error' in response:
        api_error = APIError(ErrorType.SOLR_SEARCH_ERROR, response['error']['msg'])
        return JsonResponse(api_error.args(), status=response['error']['code'])
    
    return JsonResponse(response)
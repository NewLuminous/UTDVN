from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
import pysolr
from .solr import connection, error
from UTDVN_backend.settings import HAYSTACK_CONNECTIONS

SOLR = connection.SolrConnection(HAYSTACK_CONNECTIONS['default']['URL'])
DEFAULT_CORE = 'thesis'

# Create your views here.    
def search(request):
    '''
    Takes a GET request containing a query and returns results from the
    connected Solr instance.
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
        data = [__get_document(doc_details) for doc_details in SOLR.query(DEFAULT_CORE, query)['response']['docs']]
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
    
    return JsonResponse(SOLR.get_core_names(), safe=False, status=200)

def __get_document(doc_details):
        """
        Returns a simple dictionary from the given document details
        """
        attributes = ['id', 'type', 'title', 'author', 'description', 'updatedAt', 'yearpub', 
                      'advisor', 'publisher', 'uri', 'file_url', 'language', 'keywords']
        doc = {}
    
        for attr in attributes:
            # In the Solr JSON responses, keys are strings and values are arrays
            if attr in doc_details.keys() and len(doc_details[attr]) > 0:
                doc[attr] = doc_details[attr][0]
        return doc
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
import pysolr
from .solr import connection, builder
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
    """
    Parameters
    ----------
    types : string, optional
        The Solr cores to search in.
        All cores by default.
    q : string
        The query string.
    sort : string, optional
        Sort field or function with asc|desc.
        Example: 'score desc, popularity desc'
    start : int, optional
        Number of leading documents to skip.
    rows : int, optional
        Number of documents to return after 'start'.
    return : string, optional
        The fields to be returned in the query response.
        All fields by default.
        Example: 'id,sales_price:price,secret_sauce:popularity,score'

    Takes a GET request containing a query and returns results from the connected Solr instance.
    
    Example Usage:
    http://.../api/search?core=thesis&q=ung thư&sort=yearpub desc&start=0&rows=10
    -------
    See https://lucene.apache.org/solr/guide/8_4/common-query-parameters.html
    and https://lucene.apache.org/solr/guide/8_4/highlighting.html for more details.
    """
    if request.method != "GET":
        return HttpResponse(status=405)
    
    try:
        target_cores = builder.build_cores(request.GET.get('types', ''), SOLR.get_core_names())
        return_fields = builder.build_return_fields(request.GET.get('return', ''), target_cores)
    except ValueError as ve:
        api_error = APIError(ErrorType.INVALID_SEARCH_REQUEST, str(ve))
        return JsonResponse(api_error.args(), status=400)
    
    query = request.GET.get('q', '')
    if query == '':
        api_error = APIError(ErrorType.INVALID_SEARCH_REQUEST)
        return JsonResponse(api_error.args(), status=400)
    
    kwargs = {
        'sort': request.GET.get('sort', ''),
        'start': request.GET.get('start', ''),
        'rows': request.GET.get('rows', ''),
        'field_list': return_fields,
    }
    
    responses = {
        'request': {
            'types': target_cores,
            'return fields': return_fields.split(","),
        },
        'data': []
    }
    for core in target_cores:
        try:
            new_query, new_kwargs = builder.build_query(core, query, kwargs)
            query_response = SOLR.query(core, new_query, **new_kwargs)
            if 'error' in query_response:
                api_error = APIError(
                    ErrorType.SOLR_SEARCH_ERROR, 
                    query_response['error']['msg'] + " on core " + core)
                return JsonResponse(api_error.args(), status=query_response['error']['code'])
            
            query_response['type'] = core
            for doc in query_response['response']['docs']:
                builder.flatten_doc(doc, return_fields, ['keywords'])

            responses['data'].append(query_response)

        #We do not use pysolr to query.
        #except pysolr.SolrError as se:
        #    api_error = APIError(ErrorType.SOLR_SEARCH_ERROR, str(se))
        #    return JsonResponse(api_error.args(), status=400)
        except KeyError as ke:
            api_error = APIError(ErrorType.UNEXPECTED_SERVER_ERROR, str(ke))
            return JsonResponse(api_error.args(), status=500)
        except ValueError as ve:
            api_error = APIError(ErrorType.SOLR_CONNECTION_ERROR, str(ve))
            return JsonResponse(api_error.args(), status=500)

    return JsonResponse(responses)
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import generic
import pysolr
from .solr import connection
from .solr.error import APIError, ErrorType
from .solr.query import Query
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
    core : string, optional
        The name of the Solr core to search in.
        All cores by default.
    q : string, optional
        The query string.
        The default is '*:*'.
    sort : string, optional
        Sort field or function with asc|desc.
        Example: 'score desc, popularity desc'
    start : int, optional
        Number of leading documents to skip.
    rows : int, optional
        Number of documents to return after 'start'.
    return : string, optional
        The fields to be returned in the query response.
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
    
    core = request.GET.get('core', '')
    query = request.GET.get('q', '')
    return_fields = request.GET.get('return', '')
    
    kwargs = {
        'sort': request.GET.get('sort', ''),
        'start': request.GET.get('start', ''),
        'rows': request.GET.get('rows', ''),
        'field_list': return_fields,
    }
        
    target_cores = []
    if core == '':
        for core in SOLR.get_core_names():
            target_cores.append(core)
    else:
        target_cores.append(core)
        
    return_fields_list = return_fields.replace(' ',',').split(',')
    
    responses = {
        'data': []
    }
    for core in target_cores:
        try:
            new_query, new_kwargs = _build_query(core, query, kwargs)
            query_response = SOLR.query(core, new_query, **new_kwargs)
            if 'error' in query_response:
                api_error = APIError(
                    ErrorType.SOLR_SEARCH_ERROR, 
                    query_response['error']['msg'] + " on core " + core)
                return JsonResponse(api_error.args(), status=query_response['error']['code'])
            
            query_response['type'] = core
            for doc in query_response['response']['docs']:
                for field in return_fields_list:
                    if field in doc:
                        doc[field] = doc[field][0] if len(doc[field]) == 1 else doc[field]

            responses['data'].append(query_response)

        except pysolr.SolrError as e:
            api_error = APIError(ErrorType.SOLR_SEARCH_ERROR, str(e))
            return JsonResponse(api_error.args(), status=400)
        except KeyError as e:
            api_error = APIError(ErrorType.UNEXPECTED_SERVER_ERROR, str(e))
            return JsonResponse(api_error.args(), status=500)
        except ValueError as e:
            api_error = APIError(ErrorType.SOLR_CONNECTION_ERROR, str(e))
            return JsonResponse(api_error.args(), status=500)

    responses['request'] = {
        'query': query,
        'types': target_cores,
        'return_fields': return_fields_list
    }
    return HttpResponse(pysolr.force_unicode(responses))

def _build_query(core, query_str, base_kwargs):
    kwargs = base_kwargs.copy()
    
    if core == 'thesis':
        fields = {
            'id': 1,
            'title': 10,
            'author': 8,
            'description': 6,
            'advisor': 7,
            'publisher': 5,
            'keywords': 6,
        }
        query = Query(query_str).fuzz(2)
        terms_query = Query(query_str, as_phrase=False, escape=True, sanitize=True) \
            .for_fields(fields)
        query = query.select_or(terms_query)
        kwargs['default_field'] = 'title'
        kwargs['highlight_fields'] = 'title,description'
    else:
        query = Query(query_str)
        
    return (str(query), kwargs)
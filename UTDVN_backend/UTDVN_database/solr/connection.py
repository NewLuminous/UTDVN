import pysolr
import json
from UTDVN_backend.settings import HAYSTACK_CONNECTIONS

SOLR_URL = HAYSTACK_CONNECTIONS['default']['URL']
SOLR_DB = pysolr.Solr(SOLR_URL, timeout=10)
SOLR_ADMIN = pysolr.SolrCoreAdmin(SOLR_URL + '/admin/cores')
DEFAULT_CORE = 'test'

def get_cores():
    # Returns a list of string, where each string is a Solr core's name
    status_response = SOLR_ADMIN.status()
    status = json.loads(status_response)
    return [core_name for core_name in status['status']]

def create_pysolr_cores(core_names):
    # Maps core names to pysolr core objects
    pysolr_cores = {}
    for core_name in core_names:
        pysolr_cores[core_name] = pysolr.Solr(SOLR_URL + '/' + core_name)
    return pysolr_cores

SOLR_CORES = create_pysolr_cores(get_cores())

def add_items(items, core_name=DEFAULT_CORE, commit=True):
    # Adds items to Solr core
    SOLR_CORES[core_name].add(items, commit=commit)
    
def search(query, core_name=DEFAULT_CORE):
    '''
    Performs a search and returns an array of documents.
    Raise a KeyError if no core with the given name was found,
    or a pysolr.SolrError if the search request to Solr fails.
    '''
    try:
        core = SOLR_CORES[core_name]
    except KeyError as e:
        raise KeyError('No Solr core with the name %s was found.' % core_name)
    
    return [__get_document(result) for result in core.search(query)]

def __get_document(document_details):
    # Returns a simple dictionary
    attributes = ['title', 'author', 'advisor', 'publish_date', 'publisher', 'abstract', 'uri', 'file_url', 'language', 'keywords']
    doc = {}
    
    for attr in attributes:
        # In the Solr JSON responses, keys are strings and values are arrays
        if attr in document_details.keys() and len(document_details[attr]) > 0:
            doc[attr] = document_details[attr][0]
    return doc
    
from . import models
from .query import Query

def build_cores(cores, solr_cores):
    """
    Builds a list of cores to search based on given parameters.
    Raises an exception if any core is not available.
    """
    if cores == '':
        return solr_cores
    
    if cores == 'test':
        return ['test']
    
    core_list = cores.split(',')
    invalid_core_list = [core for core in core_list if core not in solr_cores]
    if len(invalid_core_list) > 0:
        raise ValueError('Invalid type(s) requested: ' + ','.join(invalid_core_list))
        
    return core_list

def build_return_fields(fields, types):
    """
    Builds a string listing the fields to return based on types.
    Raises an exception if any field is not available.
    """
    if types == ['test']:
        return fields
    
    return_fields = ','.join([field for field in models.SolrDocument.doc.keys() if field != 'type'])
    field_list = fields.split(',')
    valid_field_list = models.get_models_fields(types)
    if len(valid_field_list) == 0:
        raise ValueError('Invalid type(s) requested: ' + ','.join(types))
    
    if fields == '':
        return ','.join(valid_field_list)
    
    invalid_field_list = [field for field in field_list if field not in valid_field_list]
    if len(invalid_field_list) > 0:
        raise ValueError('Invalid return field(s) requested: ' + ','.join(invalid_field_list))
        
    return return_fields + ',' + ','.join(field_list)

def build_search_query(core, query_str, base_kwargs):
    """
    Builds a search query and parameters to return the best results from the given core.
    -------
    See https://lucene.apache.org/solr/guide/8_4/the-standard-query-parser.html for more details.
    """
    kwargs = base_kwargs.copy()
    if ' ' in query_str:
        query = Query(query_str, as_phrase=True, sanitize=True).fuzz(0)
    else:
        query = Query(query_str, as_phrase=False, escape=(query_str!='*'))
            
    if core == 'thesis':
        fields = {
            'id': 1,
            'title': 10,
            'author': 5,
            'description': 8,
            'advisor': 5,
            'publisher': 4,
            'keywords': 6,
        }
        if query_str.isdigit():
            fields['yearpub'] = 1
            
        query = query.for_fields(fields)
        kwargs['default_field'] = 'title'
        kwargs['highlight_fields'] = 'title,description'
    else:
        #'test' core
        query = Query(query_str, as_phrase=False)
        
    return (str(query), kwargs)

def build_document_query(doc_id, base_kwargs):
    """
    Builds a search query and parameters to find the document with the given doc_id
    -------
    See https://lucene.apache.org/solr/guide/8_4/the-standard-query-parser.html for more details.
    """
    kwargs = base_kwargs.copy()
    query = Query(doc_id, as_phrase=False, escape=True).for_single_field('id')    
    kwargs['default_field'] = 'id'
    return (str(query), kwargs)

def flatten_doc(doc, return_fields, exceptions=None):
    """
    Parameters
    ----------
    doc : dict
        The document in the Solr response.
    return_fields : string
        A string of comma-separated field names.
    exceptions : list, optional
        A list of names of fields that should not be flattened.

    Flattens single-item list fields returned by Solr.
    """
    if type(doc) is not dict:
            raise ValueError('Document must be a dictionary.')
            
    for field in return_fields.split(","):
        if exceptions is not None and field in exceptions:
            continue
        elif field not in doc:
            continue
        else:
            doc[field] = doc[field][0] if len(doc[field]) == 1 else doc[field]
    return doc
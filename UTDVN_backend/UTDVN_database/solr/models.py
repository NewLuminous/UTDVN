class SolrDocument(object):
    """
    A base class for documents that are inserted into Solr.
    """
    #Default doc fields:
    doc = {
        'id': '',
        'type': '',
        'title': '',
        'author': '',
        'description': '',
        'updatedAt': '',
    }
    
    def __init__(self, doc, **kwargs):
        """
        This method should be called by the subclass constructor
        """
        self.doc = doc
        for key in self.doc.keys():
            if key in kwargs and key != 'type':
                doc[key] = kwargs[key]
        
    def get_type(self):
        """
        Returns the document type.
        This method should not be overridden.
        """
        return self.doc['type']
    
    def add_to_solr(self, solr_connection):
        """
        Submits the document to the given Solr connection.
        This method should not be overridden.
        """
        solr_connection.add_document(self.get_type(), self.doc.copy())
    
class SolrThesis(SolrDocument):
    """
    Represents a thesis.
    """
    doc = {
        'id': '',
        'type': 'thesis',
        'title': '',
        'author': '',
        'description': '',
        'updatedAt': '',
        'yearpub': '',
        'advisor': '',
        'publisher': '',
        'uri': '',
        'file_url': '',
        'language': '',
        'keywords': '',
    }
    
    def __init__(self, **kwargs):
        super(SolrThesis, self).__init__(self.doc, **kwargs)
        
MODELS = [SolrThesis]

def get_models_fields(type_list):
    fields = []
    for doc in [model.doc for model in MODELS]:
        if doc['type'] in type_list:
            fields += [key for key in doc.keys() if key not in fields]
    return fields
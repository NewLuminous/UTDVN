import pysolr
import json
import requests

class SolrConnection(object):
    
    # The maximum number of documents held in a core's insert queue before automatically inserted.
    QUEUE_THRESHOLD = 100
    
    def __init__(self, url):
        """
        Creates a SolrConnection from the given base Solr url of the form 
        'http://solrhostname:solrport/solr'.
        """
        self.url = url
        self.solr = pysolr.Solr(url, timeout=10)
        self.admin = pysolr.SolrCoreAdmin(url + '/admin/cores')  
        self.cores = {}
        self.queues = {}

        for core_name in self.fetch_core_names():
            self.cores[core_name] = pysolr.Solr(self.url + '/' + core_name)
            self.queues[core_name] = list()

    def fetch_core_names(self):
        """
        Makes a request to Solr and returns an array of strings 
        where each string is the name of a core in the response from Solr.
        """
        status_response = self.admin.status()
        status = json.loads(status_response)
        return [core_name for core_name in status['status']]

    def get_core_names(self):
        """
        Returns a list of known cores that is not used for testing in the Solr instance 
        without making a request to Solr.
        """
        valid_cores = list(self.cores.keys())
        if 'test' in valid_cores:
            valid_cores.remove('test')
        return valid_cores
    
    def _get_url(self, url, params):
        """
        Makes a request to the given url relative to the base url with the given parameters and
        returns the JSON response.
        """
        response = requests.get(url, params=pysolr.safe_urlencode(params))
        return response.json()

    def fetch_schema(self, core_name):
        """
        Returns the schema of the core with the given name as a dictionary.
        """
        self._validate_core(core_name)
        response = self._get_url('%s/%s/schema' % (self.url, core_name), {})
        return response['schema']

    def add_documents(self, core_name, documents, commit=True):
        """
        Adds list of documents into the solr core and
        returns Solr response.
        """
        self._validate_core(core_name)
        print('Adding %d documents into core %s' % (len(documents), core_name))
        return self.cores[core_name].add(documents, commit=commit)
    
    def add_document(self, core_name, document):
        """
        Queues a document for insertion into the specified core and returns None.
        If the number of documents in the queue exceeds QUEUE_THRESHOLD,
        this method will insert them all and return the response from Solr.
        All values in 'doc' must be strings.
        """
        self._validate_core(core_name)
        self.queues[core_name].append(document)
        if len(self.queues[core_name]) >= self.QUEUE_THRESHOLD:
            docs = list(self.queues[core_name].copy())
            del self.queues[core_name][:]
            return self.add_documents(core_name, docs)
        
        return None
    
    def add_queued(self):
        """
        Adds all queued documents in all cores.
        Returns a dictionary containing the Solr response from each core.
        """
        responses = {}
        for core in self.cores:
            docs = list(self.queues[core].copy())
            del self.queues[core][:]
            responses[core] = self.add_documents(core, docs)
        return responses
    
    def query(self, core_name, query='*:*', filter_query='', sort='', start='', rows='', 
              field_list='', default_field='', highlight_fields='', omit_header=True):
        """
        Parameters
        ----------
        core_name : string
            The name of the Solr core.
        query : string
            The query string.
        filter_query : string
            Defines a query to restrict the superset of returned documents, 
            without influencing score.
            Example: '+popularity:[10 TO *] +section:0'
        sort : string
            Sort field or function with asc|desc.
            Example: 'score desc, div(popularity,price) desc'
        start : int
            Number of leading documents to skip.
        rows : int
            Number of documents to return after 'start'.
        field_list : string
            Limits the information included in a query response 
            to a specified list of fields.
            Example: 'id,sales_price:price,secret_sauce:product(price,popularity),score'
        default_field : string
            Default search field.
        highlight_fields : string
            Fields to hightlight on.
        omit_header : boolean
            Whether or not Solr excludes the header from the returned results.

        Returns a response corresponding to the given query from Solr.
        -------
        See https://lucene.apache.org/solr/guide/8_4/common-query-parameters.html
        and https://lucene.apache.org/solr/guide/8_4/highlighting.html for more details.
        """
        self._validate_core(core_name)
        params = {
            "q": query,
            "wt": "json",
            "omitHeader": "true" if omit_header else "false",
            "hl.fragsize": 200
        }
        if filter_query != '':
            params["fq"] = filter_query
        if sort != '':
            params["sort"] = sort
        if start != '':
            params["start"] = start
        if rows != '':
            params["rows"] = rows
        if field_list != '':
            params["fl"] = field_list
        if default_field != '':
            params["df"] = default_field
        if highlight_fields != '':
            params["hl"] = "on"
            params["hl.fl"] = highlight_fields
            
        response = self._get_url('%s/%s/select' % (self.url, core_name), params)
        return response
    
    def optimize(self, core_name=None):
        """
        Performs defragmentation of specified core in Solr.
        If no core is specified, defragments all cores.
        """
        if core_name:
            self._validate_core(core_name)
            self.cores[core_name].optimize()
        else:
            [self.cores[core].optimize() for core in self.cores]
    
    def _validate_core(self, core_name):
        """
        Checks whether the specified core exists.
        """
        if core_name not in self.cores:
            raise ValueError('The core "%s" was not found' % core_name)
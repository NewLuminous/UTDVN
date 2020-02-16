from django.test import TestCase
from django.urls import reverse
from unittest.mock import MagicMock, patch, call
from .solr.connection import SolrConnection
from .solr.error import APIError, ErrorType
from .solr.models import *
from .mocks import MockSolr, MockAdmin, MockResponse

class SolrConnectionTests(TestCase):
    
    @patch('pysolr.SolrCoreAdmin')
    @patch('pysolr.Solr')
    def setUp(self, mock_solr, mock_admin):
        mock_solr.return_value = MockSolr()
        self.mock_solr = mock_solr
        
        cores = ['test', 'something']
        mock_admin.return_value = MockAdmin(cores)
        self.mock_admin = mock_admin
        
        url = "http://a.test.url/solr"
        self.solr_connection = SolrConnection(url)
        
        self.doc = {"id":"testid"}
        
    def test_url(self):
        self.assertEqual(self.solr_connection.url, "http://a.test.url/solr")
    
    def test_fetch_core_names(self):
        self.assertEqual(self.solr_connection.fetch_core_names(), ['test', 'something'])
        
    def test_get_core_name(self):
        self.assertEqual(self.solr_connection.get_core_names(), ['something'])
        
    def test_fetch_schema_with_non_existent_core(self):
        with self.assertRaises(ValueError):
            self.solr_connection.fetch_schema('blahblah')
        
    @patch('requests.get')
    def test_fetch_schema(self, mock_get):
        response = {
            "schema" : {
                "name":"custom-config",
                "version":7.0,
                "uniqueKey":"id",
                "fieldTypes":[]
            }
        }
        mock_get.return_value = MockResponse(response)
        self.assertEqual(self.solr_connection.fetch_schema('something'), response["schema"])
        
    def test_add_documents_with_non_existent_core(self):
        with self.assertRaises(ValueError):
            self.solr_connection.add_documents("blahblah", [self.doc, self.doc])
        
    def test_add_documents(self):
        self.assertEqual(self.solr_connection.add_documents('something', [self.doc, self.doc]), 
                         [self.doc, self.doc])
        
    def test_add_document_with_non_existent_core(self):
        with self.assertRaises(ValueError):
            self.solr_connection.add_document("blahblah", self.doc)
        
    def test_add_document_with_empty_queue(self):
        self.assertEqual(self.solr_connection.add_document('something', self.doc), None)
        
    def test_add_document_with_documents_under_QUEUE_THRESHOLD(self):
        responses = []
        for _ in range(self.solr_connection.QUEUE_THRESHOLD - 1):
            responses += [self.solr_connection.add_document('something', self.doc)]
        self.assertEqual(responses,(self.solr_connection.QUEUE_THRESHOLD - 1) * [None])
        
    def test_add_document_with_documents_equal_QUEUE_THRESHOLD(self):
        response = None
        for _ in range(self.solr_connection.QUEUE_THRESHOLD):
            response = self.solr_connection.add_document('something', self.doc)
        self.assertEqual(response, self.solr_connection.QUEUE_THRESHOLD * [self.doc])
        
    def test_add_document_with_documents_exceed_QUEUE_THRESHOLD(self):
        for _ in range(self.solr_connection.QUEUE_THRESHOLD):
            _ = self.solr_connection.add_document('something', self.doc)
        self.assertEqual(self.solr_connection.add_document('something', self.doc), None)
        
    def test_add_queued_calls_to_add(self):
        other_doc = {"id": "other_testid"}
        self.mock_solr.return_value = MagicMock()
        self.solr_connection.cores['test'] = self.mock_solr
        self.solr_connection.cores['something'] = self.mock_solr
        self.solr_connection.add_document('test', self.doc)
        self.solr_connection.add_document('something', other_doc)
        self.solr_connection.add_queued()
        self.assertEqual(self.mock_solr.add.call_count, 2)
        self.assertEqual(
            self.mock_solr.add.call_args_list, 
            [call([{"id": "testid"}], commit=True), call([{"id": "other_testid"}], commit=True)])
        
    def test_add_queued_return(self):
        other_doc = {"id": "other_testid"}
        self.solr_connection.add_document('test', self.doc)
        self.solr_connection.add_document('something', other_doc)
        self.assertEqual(self.solr_connection.add_queued(), 
                         {'test': [self.doc], 'something': [other_doc]})
        
    def test_query_with_test_core(self):
        solr_connection = SolrConnection("http://solr:8983/solr")
        expected_response = {
            "response": {
                "numFound":11,
                "start":3,
                "docs": [
                    {
                        "name": ["Canon PowerShot SD500"],
                        "cat": ["electronics", "camera"]
                    },
                    {
                        "name": ["CORSAIR ValueSelect 1GB 184-Pin DDR SDRAM Unbuffered DDR 400 (PC 3200) System Memory - Retail"],
                        "cat": ["electronics", "memory"]
                    },
                    {
                        "name": ["Dell Widescreen UltraSharp 3007WFP"],
                        "cat": ["electronics and computer1"]
                    }
                ]
            },
            "highlighting": {
                "9885A004": {
                    "cat": ["<em>electronics</em>"]
                },
                "VS1GB400C3": {
                    "cat": ["<em>electronics</em>"]
                },
                "3007WFP": {
                    "cat":["<em>electronics</em> and computer1"]
                }
            }
        }
        result = solr_connection.query('test', 'electronics', 'popularity:[5 TO *]', 
                                       'popularity desc, price desc', 3, 3, 'name cat', 'cat', 'cat', True)
        
        self.assertEqual(result, expected_response)
        
    def test_optimize_with_non_existent_core(self):
        with self.assertRaises(ValueError):
            self.solr_connection.optimize('blahblah')
        
    def test_optimize(self):
        self.mock_admin.return_value = MockAdmin(['c1', 'c2'])
        self.solr_connection.cores['test'] = MagicMock()
        self.solr_connection.cores['something'] = MagicMock()
        self.solr_connection.cores['c1'] = MagicMock()
        self.solr_connection.cores['c2'] = MagicMock()
        
        self.solr_connection.optimize('something')
        self.assertTrue(self.solr_connection.cores['something'].optimize.called)
        
        self.solr_connection.optimize()
        self.assertTrue(self.solr_connection.cores['test'].optimize.called)
        self.assertTrue(self.solr_connection.cores['something'].optimize.called)
        self.assertTrue(self.solr_connection.cores['c1'].optimize.called)
        self.assertTrue(self.solr_connection.cores['c2'].optimize.called)
        
class SolrModelsTests(TestCase):
    def _create_model(self, t):
        if t == 'thesis':
            args = {
                'id': 'testid',
                'type': 'thesis',
                'title': 'testtitle',
                'author': 'dummy',
                'description': 'testblurb',
                'updatedAt': '1234567',
                'yearpub': '9999',
                'advisor': 'pro',
                'publisher': 'tester',
                'uri': 'http://u.r.i',
                'file_url': 'http://file.url',
                'language': 'mom_tonge',
                'keywords': ['kw1', 'kw2']
            }
            return (args, SolrThesis(**args))
        
    def setUp(self):
        (self.args, self.model) = self._create_model('thesis')
    
    def test_init(self):
        for (key, value) in self.args.items():
            self.assertEqual(self.model.doc[key], value)
    
    def test_get_type(self):
        self.assertEqual(self.model.get_type(), 'thesis')
        
    def test_add_to_solr(self):
        mock_solr = MagicMock()
        mock_solr.add_document.return_value = None
        self.model.add_to_solr(mock_solr)
        mock_solr.add_document.assert_called_with('thesis', self.args)
        
    def test_get_models_fields(self):
        result = get_models_fields()
        self.assertEquals(result, ['id', 'type', 'title', 'author', 'description', 'updatedAt', 'yearpub',
                                   'advisor', 'publisher', 'uri', 'file_url', 'language', 'keywords'])
        
class ErrorTypeTests(TestCase):
    def test(self):
        self.assertEqual(ErrorType(0).name, 'UNEXPECTED_SERVER_ERROR')
        self.assertEqual(ErrorType(1).name, 'SOLR_CONNECTION_ERROR')
        self.assertEqual(ErrorType(2).name, 'SOLR_SEARCH_ERROR')
        self.assertEqual(ErrorType(3).name, 'INVALID_SEARCH_REQUEST')
        self.assertEqual(ErrorType(4).name, 'INVALID_GETDOCUMENT_REQUEST')
        with self.assertRaises(ValueError):
            print(ErrorType(5).name)
        
class SolrAPIErrorTests(TestCase):
    def setUp(self):
        self.error = APIError(ErrorType(0), 'An error occurred.')
        
    def test_init_with_not_none_message(self):
        self.assertEqual(self.error.error_type, ErrorType(0))
        self.assertEqual(self.error.message, 'An error occurred.')
        
    def test_init_with_none_message(self):
        error = APIError(ErrorType(0), None)
        self.assertEqual(error.message, 'An unexpected error occurred during handling of your request.')
        error = APIError(ErrorType(1), None)
        self.assertEqual(error.message, 'Failed to connect to the Solr instance.')
        error = APIError(ErrorType(2), None)
        self.assertEqual(error.message, 'Solr returned an error response to the search query.')
        error = APIError(ErrorType(3), None)
        self.assertEqual(error.message, 'Missing or incorrect search query.')
        error = APIError(ErrorType(4), None)
        self.assertEqual(error.message, 'Must supply an ID with the parameter "id".')
        
    def test_init_with_none_errortype(self):
        with self.assertRaises(ValueError):
            error = APIError(None, 'An error occurred.')
    
    def test_args(self):
        self.assertEqual(self.error.args(), {
            'errorType': ErrorType(0).name,
            'message': 'An error occurred.',
        })
        
    def test_json(self):
        self.assertEqual(self.error.json(), 
                         '{"errorType": "%s", "message": "An error occurred."}' % ErrorType(0).name)

class CoresViewTests(TestCase):
    def test_post_method(self):
        response = self.client.post(reverse('UTDVN_database:cores'))
        self.assertEqual(response.status_code, 405)
    
    def test_get_method(self):
        response = self.client.get(reverse('UTDVN_database:cores'))
        self.assertNotContains(response, "test")
        self.assertContains(response, "thesis")

class SearchViewTests(TestCase):
    def test_post_method(self):
        response = self.client.post(reverse('UTDVN_database:search'))
        self.assertEqual(response.status_code, 405)
        
    def test_get_method_without_params(self):
        response = self.client.get(reverse('UTDVN_database:search'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Missing or incorrect search query.')
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        
    def test_get_method_without_param_core(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '*:*'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Missing or incorrect search query.')
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        
    def test_get_method_with_null_core(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'core': '', 'q': '*:*'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Missing or incorrect search query.')
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        
    def test_get_method_with_empty_core(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'core': "''", 'q': '*:*'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['message'], 'Failed to connect to the Solr instance.')
        self.assertEqual(response.json()['errorType'], ErrorType.SOLR_CONNECTION_ERROR.name)
        
    def test_get_method_with_non_existent_core(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'core': 'blahblah', 'q': '*:*'})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['message'], 'Failed to connect to the Solr instance.')
        self.assertEqual(response.json()['errorType'], ErrorType.SOLR_CONNECTION_ERROR.name)
        
    def test_get_method_without_param_q(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'core': 'test','query': '*:*'})
        self.assertContains(response, 'id')
        self.assertContains(response, '_version_')
        self.assertContains(response, 'cat')
        self.assertContains(response, 'author')
        
    def test_get_method_with_null_query(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'core': 'test', 'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"response": {"numFound": 0, "start": 0, "docs": []}}')
        
    def test_get_method_with_empty_query(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'core': 'test', 'q': "''"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'undefined field title')
        self.assertEqual(response.json()['errorType'], ErrorType.SOLR_SEARCH_ERROR.name)
        
    def test_get_method_with_wrong_syntax(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'core': 'test', 'q': '/'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.SOLR_SEARCH_ERROR.name)
        
    def test_get_method_with_valid_query(self):
        response = self.client.get(
            reverse('UTDVN_database:search'), 
            {'core': 'test', 'q': 'cat:electronics', 'sort': 'popularity desc, price desc', 'start': 3, 'rows': 3}
        )
        self.assertEqual(response.json()['response']['numFound'], 14)
        self.assertEqual(response.json()['response']['start'], 3)
        self.assertEqual(response.json()['response']['docs'][0]['id'], '9885A004')
        self.assertEqual(response.json()['response']['docs'][0]['name'], ['Canon PowerShot SD500'])
        
    def test_get_method_with_core_thesis(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'core': 'thesis', 'q': '*:*'})
        self.assertContains(response, 'id')
        self.assertContains(response, 'type')
        self.assertContains(response, 'title')
        self.assertContains(response, 'author')
        self.assertContains(response, 'description')
        self.assertContains(response, 'updatedAt')
        self.assertContains(response, 'yearpub')
        self.assertContains(response, 'advisor')
        self.assertContains(response, 'publisher')
        self.assertContains(response, 'uri')
        self.assertContains(response, 'language')
        self.assertContains(response, 'keywords')
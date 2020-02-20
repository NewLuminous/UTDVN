from django.test import TestCase
from django.urls import reverse
from unittest.mock import MagicMock, patch, call
from .solr.connection import SolrConnection
from .solr.error import APIError, ErrorType
from .solr.models import *
from .solr.query import Query
from .solr import builder
from .mocks import MockSolr, MockAdmin, MockResponse
from UTDVN_database.views import SOLR
import json

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
        result = SOLR.query('test', 'electronics', 'popularity:[5 TO *]', 
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
        
    def test_get_models_fields_with_non_existent_type(self):
        result = get_models_fields(['blah'])
        self.assertEquals(result, [])
        
    def test_get_models_fields(self):
        result = get_models_fields(['thesis'])
        self.assertEquals(result, ['id', 'type', 'title', 'author', 'description', 'updatedAt', 'yearpub',
                                   'advisor', 'publisher', 'uri', 'file_url', 'language', 'keywords'])
        
class ErrorTypeTests(TestCase):
    def test(self):
        self.assertEqual(ErrorType(0).name, 'UNEXPECTED_SERVER_ERROR')
        self.assertEqual(ErrorType(1).name, 'SOLR_CONNECTION_ERROR')
        self.assertEqual(ErrorType(2).name, 'SOLR_SEARCH_ERROR')
        self.assertEqual(ErrorType(3).name, 'INVALID_SEARCH_REQUEST')
        self.assertEqual(ErrorType(4).name, 'INVALID_DOCUMENT_REQUEST')
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
        self.assertEqual(error.message, 'Must supply a query with the parameter "q".')
        error = APIError(ErrorType(4), None)
        self.assertEqual(error.message, 'Must supply an ID with the parameter "id".')
        
    def test_init_with_none_errortype(self):
        with self.assertRaises(ValueError):
            _ = APIError(None, 'An error occurred.')
    
    def test_args(self):
        self.assertEqual(self.error.args(), {
            'errorType': ErrorType(0).name,
            'message': 'An error occurred.',
        })
        
    def test_json(self):
        self.assertEqual(self.error.json(), 
                         '{"errorType": "%s", "message": "An error occurred."}' % ErrorType(0).name)
        
class SolrQueryTests(TestCase):
    def test_as_phrase_false_escape_false(self):
        query = Query('formula:1+1=2', as_phrase=False)
        self.assertEqual(str(query), 'formula:1+1=2')
        
    def test_as_phrase_false_escape_true(self):
        query = Query('formula:1+1=2', as_phrase=False, escape=True)
        self.assertEqual(str(query), 'formula\:1\+1=2')
        
    def test_as_phrase_true_escape_false(self):
        query = Query('formula:1+1=2')
        self.assertEqual(str(query), '"formula:1+1=2"')
        
    def test_as_phrase_true_escape_true(self):
        query = Query('formula:1+1=2', escape=True)
        self.assertEqual(str(query), '"formula\:1\+1=2"')
        
    def test_fuzz_with_invalid_factor(self):
        with self.assertRaises(ValueError):
            _ = Query('hello world').fuzz(3)
        
    def test_fuzz_with_valid_factor(self):
        query = Query('hello world').fuzz(2)
        self.assertEqual(str(query), '"hello world"~2')
        
    def test_fuzz_with_factor_0(self):
        query = Query('The quick brown fox jumped over 12 lazy dogs').fuzz(0)
        self.assertEqual(str(query), '"The quick brown fox jumped over 12 lazy dogs"~0')
        
    def test_fuzz_with_factor_0_after_sanitization(self):
        query = Query('The quick brown fox jumped over 12 lazy dogs', sanitize=True).fuzz(0)
        self.assertEqual(str(query), '"quick brown fox jumped 12 lazy dogs"~2')
        
    def test_boost_importance(self):
        query = Query('hello world').boost_importance(7)
        self.assertEqual(str(query), '("hello world")^7')
        
    def test_select_and(self):
        query = Query('hello world').select_and(Query(', it \'s me!'))
        self.assertEqual(str(query), '("hello world") AND (", it \'s me!")')
        
    def test_select_or(self):
        query = Query('hello world').select_or(Query(', it \'s me!'))
        self.assertEqual(str(query), '("hello world") OR (", it \'s me!")')
        
    def test_terms_with_multiple_AND_OR_operators(self):
        query = Query('A').select_and(Query('B')).select_or(Query('C'))
        self.assertEqual(str(query), '(("A") AND ("B")) OR ("C")')
        
        query = Query('A').select_and(Query('B').select_or(Query('C')))
        self.assertEqual(str(query), '("A") AND (("B") OR ("C"))')
        
        query = (Query('A').select_or(Query('B'))).select_and(Query('C').select_or(Query('D')))
        self.assertEqual(str(query), '(("A") OR ("B")) AND (("C") OR ("D"))')
        
        query = (Query('A').select_and(Query('B'))).select_or(Query('C').select_and(Query('D')))
        self.assertEqual(str(query), '(("A") AND ("B")) OR (("C") AND ("D"))')
        
    def test_select_require_with_no_terms(self):
        query = Query('hello world').select_require([])
        self.assertEqual(str(query), '"hello world"')
        
    def test_select_require_with_some_terms(self):
        query = Query('hello world').select_require(['term1', 'term2'])
        self.assertEqual(str(query), '"hello world" +term1 +term2')
        
    def test_for_single_field_with_blank_field(self):
        query = Query('hello world').for_single_field('')
        self.assertEqual(str(query), '"hello world"')
        
    def test_for_single_field_with_not_blank_field(self):
        query = Query('hello world').for_single_field('id')
        self.assertEqual(str(query), 'id:"hello world"')
        
    def test_for_fields_with_fields_not_a_dict(self):
        query = Query('hello world')
        fields = 'not a dict'
        with self.assertRaises(ValueError):
            query.for_fields(fields)
            
        fields = ['not', 'a', 'dict']
        with self.assertRaises(ValueError):
            query.for_fields(fields)
            
        fields = '{"not": 1, "a": 2, "dict": 3}'
        with self.assertRaises(ValueError):
            query.for_fields(fields)
            
    def test_for_fields_with_fields_a_dict(self):
        fields = {'id': 1, 'title': 10}
        query = Query('hello world').for_fields(fields)
        self.assertEqual(
            str(query), 
            '("hello world") OR ((id:("hello world")^1) OR (title:("hello world")^10))'
        )
        
    def test_sanitation(self):
        query = Query('The quick brown fox jumped over 12 lazy dogs', sanitize=True)
        self.assertEqual(str(query), '"quick brown fox jumped 12 lazy dogs"')
        
    def test_sanitation_with_query_str_full_of_garbage(self):
        query = Query('but to and', sanitize=True)
        self.assertEqual(str(query), '"but to and"')
        
    def test_sanitation_in_vietnamese(self):
        query = Query('Con cáo nâu nhanh nhảy qua 12 chú chó lười', sanitize=True)
        self.assertEqual(str(query), '"Con cáo nâu nhanh nhảy qua 12 chó lười"')
        
    def test_sanitation_with_query_str_full_of_garbage_in_vietnamese(self):
        query = Query('nhưng để và', sanitize=True)
        self.assertEqual(str(query), '"nhưng để và"')
        
class SolrBuilderTests(TestCase):
    def setUp(self):
        self.solr_cores = ['sc1', 'sc2', 'sc3']
    
    def test_build_core_with_no_cores(self):
        self.assertEqual(builder.build_cores('', self.solr_cores), self.solr_cores)
        
    def test_build_core_with_one_valid_core(self):
        self.assertEqual(builder.build_cores('sc1', self.solr_cores), ['sc1'])
        
    def test_build_core_with_core_test(self):
        self.assertEqual(builder.build_cores('test', self.solr_cores), ['test'])
        
    def test_build_core_with_some_invalid_cores(self):
        with self.assertRaises(ValueError):
            builder.build_cores('test,dummy,sc3', self.solr_cores)
            
    def test_build_core_with_all_cores_invalid(self):
        with self.assertRaises(ValueError):
            builder.build_cores('test,dummy', self.solr_cores)
            
    def test_build_core_with_multiple_valid_cores(self):
        self.assertEqual(builder.build_cores('sc1,sc3', self.solr_cores), ['sc1', 'sc3'])
        
    def test_build_return_fields_with_no_types(self):
        with self.assertRaises(ValueError):
            builder.build_return_fields('', [])
        
    def test_build_return_fields_with_non_existent_type(self):
        with self.assertRaises(ValueError):
            builder.build_return_fields('', ['blah'])
            
    def test_build_return_fields_with_core_test(self):
        self.assertEqual(builder.build_return_fields('id,cat', ['test']), 'id,cat')
        
    def test_build_return_fields_with_param_fields_empty(self):
        self.assertEqual(builder.build_return_fields('', ['thesis']), 'id,type,title,author,description,updatedAt,yearpub,advisor,publisher,uri,file_url,language,keywords')
            
    def test_build_return_fields_with_invalid_fields(self):
        with self.assertRaises(ValueError):
            builder.build_return_fields('id,blah', ['thesis'])
            
    def test_build_return_fields_with_valid_fields(self):
        self.assertEqual(builder.build_return_fields('advisor', ['thesis']), 'id,title,author,description,updatedAt,advisor')
        
    def test_build_search_query_with_core_test(self):
        self.assertEqual(builder.build_search_query('test', 'cat:electronics', {}), ('cat:electronics',{}))
        
    def test_build_search_query_with_search_term_in_core_thesis(self):
        self.assertEqual(
            builder.build_search_query('thesis', '1+1=2', {'sort':''}),
            (
                '(1\+1=2) OR ((id:(1\+1=2)^1) OR ((title:(1\+1=2)^10) OR ' +
                '((author:(1\+1=2)^5) OR ((description:(1\+1=2)^8) OR ' +
                '((advisor:(1\+1=2)^5) OR ((publisher:(1\+1=2)^4) OR ' +
                '(keywords:(1\+1=2)^6)))))))',
                {'default_field':'title', 'highlight_fields':'title,description', 'sort':''}
            )
        )
        
    def test_build_search_query_with_search_all_in_core_thesis(self):
        self.assertEqual(
            builder.build_search_query('thesis', '*', {'sort':''}),
            (
                '(*) OR ((id:(*)^1) OR ((title:(*)^10) OR ' +
                '((author:(*)^5) OR ((description:(*)^8) OR ' +
                '((advisor:(*)^5) OR ((publisher:(*)^4) OR ' +
                '(keywords:(*)^6)))))))',
                {'default_field':'title', 'highlight_fields':'title,description', 'sort':''}
            )
        )
        
    def test_build_search_query_with_search_number_in_core_thesis(self):
        self.assertEqual(
            builder.build_search_query('thesis', '2020', {'sort':''}),
            (
                '(2020) OR ((id:(2020)^1) OR ((title:(2020)^10) OR ' +
                '((author:(2020)^5) OR ((description:(2020)^8) OR ' +
                '((advisor:(2020)^5) OR ((publisher:(2020)^4) OR ' +
                '((keywords:(2020)^6) OR (yearpub:(2020)^1))))))))',
                {'default_field':'title', 'highlight_fields':'title,description', 'sort':''}
            )
        )
        
    def test_build_search_query_with_search_phrase_in_core_thesis(self):
        self.assertEqual(
            builder.build_search_query('thesis', 'The world', {'sort':''}),
            (
                '("world"~1) OR ((id:("world"~1)^1) OR ((title:("world"~1)^10) OR ' +
                '((author:("world"~1)^5) OR ((description:("world"~1)^8) OR ' +
                '((advisor:("world"~1)^5) OR ((publisher:("world"~1)^4) OR ' +
                '(keywords:("world"~1)^6)))))))',
                {'default_field':'title', 'highlight_fields':'title,description', 'sort':''}
            )
        )
        
    def test_build_search_query_with_sort_in_core_thesis(self):
        self.assertEqual(
            builder.build_search_query(
                'thesis', '*', 
                {'sort':'title asc, type asc, id desc, updatedAt desc, yearpub desc'}
            ),
            (
                '(*) OR ((id:(*)^1) OR ((title:(*)^10) OR ' +
                '((author:(*)^5) OR ((description:(*)^8) OR ' +
                '((advisor:(*)^5) OR ((publisher:(*)^4) OR ' +
                '(keywords:(*)^6)))))))',
                {
                    'default_field':'title', 
                    'highlight_fields':'title,description', 
                    'sort':'title_str asc, type_str asc, id desc, updatedAt desc, yearpub desc'
                }
            )
        )
        
    def test_build_document_query(self):
        self.assertEqual(builder.build_document_query('1+1=2',{}), ('id:1\+1=2',{'default_field':'id'}))
        
    def test_flatten_doc_with_not_a_dict(self):
        with self.assertRaises(ValueError):
            builder.flatten_doc('{a dict: no}', '')
        
        with self.assertRaises(ValueError):
            builder.flatten_doc(['not a dict'], '')
            
    def test_flatten_doc(self):
        self.assertEqual(
            builder.flatten_doc(
                {
                    'not_returned': ['nrt'],
                    'returned': ['rt'],
                    'list': ['l1', 'l2', 'l3'],
                    'long_string': 'long',
                    'character': 'c',
                    'exception': ['except']
                },
                'returned,list,long_string,character,exception,not_in_doc',
                ['exception']
            ),
            {
                'not_returned': ['nrt'],
                'returned': 'rt',
                'list': ['l1', 'l2', 'l3'],
                'long_string': 'long',
                'character': 'c',
                'exception': ['except']
            }
        )

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
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        self.assertEqual(response.json()['message'], 'Must supply a query with the parameter "q".')
        
    def test_get_method_without_param_types(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '*'})
        self.assertEqual(response.status_code, 200)
        for d in json.loads(response.content)['data']:
            self.assertTrue(d['response']['numFound'] > 0)
        
    def test_get_method_with_null_types(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'types': '', 'q': '*'})
        self.assertEqual(response.status_code, 200)
        for d in json.loads(response.content)['data']:
            self.assertTrue(d['response']['numFound'] > 0)
        
    def test_get_method_with_empty_types(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'types': "''", 'q': '*'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        self.assertEqual(response.json()['message'], "Invalid type(s) requested: ''")
        
    def test_get_method_with_non_existent_types(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'types': 'blahblah', 'q': '*'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        self.assertEqual(response.json()['message'], "Invalid type(s) requested: blahblah")
        
    def test_get_method_without_param_q(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'query': '*'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        self.assertEqual(response.json()['message'], 'Must supply a query with the parameter "q".')
        
    def test_get_method_with_null_query(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        self.assertEqual(response.json()['message'], 'Must supply a query with the parameter "q".')
        
    def test_get_method_with_empty_query(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': "''"})
        self.assertEqual(response.status_code, 200)
        
    def test_get_method_with_special_character(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '/'})
        self.assertEqual(response.status_code, 200)
        
    def test_get_method_with_back_slash(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '\\'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.SOLR_SEARCH_ERROR.name)
        self.assertRegex(response.json()['message'], "^org.apache.solr.search.SyntaxError: Cannot parse ")
        
    def test_get_method_with_non_existent_return_field(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '*', 'return': 'blahblah'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_SEARCH_REQUEST.name)
        self.assertEqual(response.json()['message'], "Invalid return field(s) requested: blahblah")
        
    def test_get_method_sorting_by_a_text_field(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '*', 'sort': 'title asc'})
        self.assertEqual(response.status_code, 200)
        
    def test_get_method_with_wrong_sort_syntax(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '*', 'sort': 'updatedAt'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.SOLR_SEARCH_ERROR.name)
        self.assertRegex(response.json()['message'], "^Can't determine a Sort Order \(asc or desc\) in sort spec 'updatedAt'")
        
    def test_get_method_with_rows_not_a_number(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '*', 'rows': "'20'"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.SOLR_SEARCH_ERROR.name)
        self.assertRegex(response.json()['message'], "^For input string: \"'20'\" on core ")
        
    def test_get_method_with_a_valid_query(self):
        response = self.client.get(
            reverse('UTDVN_database:search'), 
            {'types':'thesis','q':'nghiên cứu','sort':'yearpub desc','start':1,'rows':20,'return':'yearpub,advisor'}
        )
        self.assertContains(response, 'id')
        self.assertContains(response, 'type')
        self.assertContains(response, 'title')
        self.assertContains(response, 'author')
        self.assertContains(response, 'description')
        self.assertContains(response, 'updatedAt')
        self.assertContains(response, 'yearpub')
        self.assertContains(response, 'advisor')
        self.assertNotContains(response, 'publisher')
        self.assertNotContains(response, 'uri')
        self.assertNotContains(response, 'language')
        self.assertNotContains(response, 'keywords')
        
    def test_get_method_with_core_thesis_without_param_return(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'types': 'thesis', 'q': '*'})
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
        
    def test_get_method_with_core_test(self):
        response = self.client.get(
            reverse('UTDVN_database:search'),
            {'types':'test','q':'cat:electronics','sort':'popularity desc,price desc','start':3,'rows':3}
        )
        self.assertEqual(len(json.loads(response.content)['data']), 1)
        d = json.loads(response.content)['data'][0]['response']
        self.assertEqual(d['numFound'], 14)
        self.assertEqual(d['start'], 3)
        self.assertEqual(d['docs'][0]['id'], '9885A004')
        self.assertEqual(d['docs'][0]['name'], ['Canon PowerShot SD500'])
        
class DocumentViewTests(TestCase):
    def setUp(self):
        self.existing_id = 'Đặng_Ngọc_Anh_Xây_dựng_phương_pháp_định_lượng_flurbiprofen_trong_dược_phẩm'
    
    def test_post_method(self):
        response = self.client.post(reverse('UTDVN_database:document'))
        self.assertEqual(response.status_code, 405)
        
    def test_get_method_without_params(self):
        response = self.client.get(reverse('UTDVN_database:document'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_DOCUMENT_REQUEST.name)
        self.assertEqual(response.json()['message'], 'Must supply an ID with the parameter "id".')
        
    def test_get_method_without_param_types(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'id': self.existing_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['data']['doc']['id'], self.existing_id)
        
    def test_get_method_with_null_types(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'types': '', 'id': self.existing_id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['data']['doc']['id'], self.existing_id)
        
    def test_get_method_with_empty_types(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'types': "''", 'id': self.existing_id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_DOCUMENT_REQUEST.name)
        self.assertEqual(response.json()['message'], "Invalid type(s) requested: ''")
        
    def test_get_method_with_non_existent_types(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'types': 'blahblah', 'id': self.existing_id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_DOCUMENT_REQUEST.name)
        self.assertEqual(response.json()['message'], "Invalid type(s) requested: blahblah")
        
    def test_get_method_without_param_id(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'query': '*'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_DOCUMENT_REQUEST.name)
        self.assertEqual(response.json()['message'], 'Must supply an ID with the parameter "id".')
        
    def test_get_method_with_null_id(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'id': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_DOCUMENT_REQUEST.name)
        self.assertEqual(response.json()['message'], 'Must supply an ID with the parameter "id".')
        
    def test_get_method_with_empty_id(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'id': "''"})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'Document not found')
        
    def test_get_method_with_back_slash_id(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'id': '\\'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.SOLR_SEARCH_ERROR.name)
        self.assertRegex(response.json()['message'], "^org.apache.solr.search.SyntaxError: Cannot parse 'id:\\\\': Lexical error ")
        
    def test_get_method_with_non_existent_return_field(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'id': self.existing_id, 'return': 'blahblah'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], ErrorType.INVALID_DOCUMENT_REQUEST.name)
        self.assertEqual(response.json()['message'], "Invalid return field(s) requested: blahblah")
        
    def test_get_method_with_a_valid_id(self):
        response = self.client.get(
            reverse('UTDVN_database:document'), 
            {'types':'thesis','id':self.existing_id,'return':'yearpub,advisor'}
        )
        self.assertContains(response, 'id')
        self.assertContains(response, 'type')
        self.assertContains(response, 'title')
        self.assertContains(response, 'author')
        self.assertContains(response, 'description')
        self.assertContains(response, 'updatedAt')
        self.assertContains(response, 'yearpub')
        self.assertContains(response, 'advisor')
        self.assertNotContains(response, 'publisher')
        self.assertNotContains(response, 'uri')
        self.assertNotContains(response, 'language')
        self.assertNotContains(response, 'keywords')
        
    def test_get_method_with_core_thesis_without_param_return(self):
        response = self.client.get(reverse('UTDVN_database:document'), {'types': 'thesis', 'id':self.existing_id})
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
        
    def test_get_method_with_core_test(self):
        response = self.client.get(
            reverse('UTDVN_database:document'),
            {'types':'test','id':'9885A004'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['data']['doc']['id'], '9885A004')
        self.assertEqual(json.loads(response.content)['data']['doc']['name'], ['Canon PowerShot SD500'])
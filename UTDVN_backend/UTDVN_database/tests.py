from django.test import TestCase
from django.urls import reverse
from .solr import connection, error

class SolrConnectionTests(TestCase):
    def test_get_cores(self):
        self.assertTrue('test' in connection.get_cores())
        
    def test_add_items_with_non_existent_core(self):
        self.assertRaises(KeyError, connection.add_items, [], '', False)
        
    def test_search_with_non_existent_core(self):
        self.assertRaises(KeyError, connection.search, '*:*', '')
        
class ErrorTypeTests(TestCase):
    def test(self):
        self.assertEqual(error.ErrorType(0).name, 'UNEXPECTED_SERVER_ERROR')
        self.assertEqual(error.ErrorType(1).name, 'SOLR_CONNECTION_ERROR')
        self.assertEqual(error.ErrorType(2).name, 'SOLR_SEARCH_ERROR')
        self.assertEqual(error.ErrorType(3).name, 'INVALID_SEARCH_TERM')
        
class SolrAPIErrorTests(TestCase):
    def setUp(self):
        self.api_error = error.APIError('An error occurred', error.ErrorType(0))
    
    def test_args(self):
        self.assertEqual(self.api_error.args(), {
            'message': 'An error occurred',
            'errorType': error.ErrorType(0).name,
        })
        
    def test_json(self):
        self.assertEqual(self.api_error.json(), 
                         '{"message": "An error occurred", "errorType": "%s"}' % error.ErrorType(0).name)

class SearchViewTests(TestCase):
    def test_post_method(self):
        response = self.client.post(reverse('UTDVN_database:search'))
        self.assertEqual(response.status_code, 405)
        
    def test_get_method_without_params(self):
        response = self.client.get(reverse('UTDVN_database:search'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Must supply a search term with the parameter "q".')
        self.assertEqual(response.json()['errorType'], error.ErrorType.INVALID_SEARCH_TERM.name)
        
    def test_get_method_without_param_q(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'query': '*:*'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Must supply a search term with the parameter "q".')
        self.assertEqual(response.json()['errorType'], error.ErrorType.INVALID_SEARCH_TERM.name)
        
    def test_get_method_with_null_query(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': ''})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Must supply a search term with the parameter "q".')
        self.assertEqual(response.json()['errorType'], error.ErrorType.INVALID_SEARCH_TERM.name)
        
    def test_get_method_with_empty_query(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': "''"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')
        
    def test_get_method_with_failed_search(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '/'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['errorType'], error.ErrorType.SOLR_SEARCH_ERROR.name)
        
    def test_get_method_with_successful_search(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '*:*'})
        self.assertContains(response, 'title')
        self.assertContains(response, 'author')
        self.assertContains(response, 'advisor')
        self.assertContains(response, 'publish_date')
        self.assertContains(response, 'publisher')
        self.assertContains(response, 'abstract')
        self.assertContains(response, 'uri')
        self.assertContains(response, 'file_url')
        self.assertContains(response, 'language')
        self.assertContains(response, 'keywords')

class CoresViewTests(TestCase):
    def test_post_method(self):
        response = self.client.post(reverse('UTDVN_database:cores'))
        self.assertEqual(response.status_code, 405)
    
    def test_get_method(self):
        response = self.client.get(reverse('UTDVN_database:cores'))
        self.assertContains(response, "test")
        

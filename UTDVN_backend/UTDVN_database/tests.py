from django.test import TestCase
from django.urls import reverse
from .solr import error

class SearchViewTests(TestCase):
    def test_post_method(self):
        response = self.client.post(reverse('UTDVN_database:search'))
        self.assertEqual(response.status_code, 405)
        
    def test_get_method_without_params(self):
        response = self.client.get(reverse('UTDVN_database:search'))
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Must supply a search term with the parameter \\"q\\".', status_code=400)
        self.assertContains(response, error.ErrorType.INVALID_SEARCH_TERM.name, status_code=400)
        
    def test_get_method_without_param_q(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'query': '*:*'})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Must supply a search term with the parameter \\"q\\".', status_code=400)
        self.assertContains(response, error.ErrorType.INVALID_SEARCH_TERM.name, status_code=400)
        
    def test_get_method_with_null_query(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': ''})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Must supply a search term with the parameter \\"q\\".', status_code=400)
        self.assertContains(response, error.ErrorType.INVALID_SEARCH_TERM.name, status_code=400)
        
    def test_get_method_with_empty_query(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': "''"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')
        
    def test_get_method_with_failed_search(self):
        response = self.client.get(reverse('UTDVN_database:search'), {'q': '/'})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, error.ErrorType.SOLR_SEARCH_ERROR.name, status_code=400)
        
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
        

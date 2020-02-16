import json
from enum import Enum

class ErrorType(Enum):
    '''
    Defines errors that may occur when making calls to the API
    '''
    # Occurs when an unexpected error occurs during the handling of a request
    UNEXPECTED_SERVER_ERROR = 0
    # Occurs when Django cannot reach the Solr instance.
    SOLR_CONNECTION_ERROR = 1
    # Occurs when Solr returns an error response to a search query.
    SOLR_SEARCH_ERROR = 2
    # Occurs when a query is missing/incorrect in a search request.
    INVALID_SEARCH_REQUEST = 3
    # Occurs when something is missing/incorrect in a getdocument request.
    INVALID_GETDOCUMENT_REQUEST = 4

class APIError(Exception):
    '''
    Represents an error that occurred during the processing of a request to the API.
    '''

    def __init__(self, error_type, message=None):
        '''
        Takes an HTTP status code and an error message (must be one of ErrorType) 
        to return to the client and creates a APIError that can be converted
        to JSON.
        '''
        self.error_type = error_type
        if error_type is not None and message is not None:
            self.message = message
            return
        
        if error_type is ErrorType.UNEXPECTED_SERVER_ERROR:
            self.message = 'An unexpected error occurred during handling of your request.'
        elif error_type is ErrorType.SOLR_CONNECTION_ERROR:
            self.message = 'Failed to connect to the Solr instance.'
        elif error_type is ErrorType.SOLR_SEARCH_ERROR:
            self.message = 'Solr returned an error response to the search query.'
        elif error_type is ErrorType.INVALID_SEARCH_REQUEST:
            self.message = 'Missing or incorrect search query.'
        elif error_type is ErrorType.INVALID_GETDOCUMENT_REQUEST:
            self.message = 'Must supply an ID with the parameter "id".'
        else:
            raise ValueError('Invalid error type. Must be one of ErrorTypes.')
        
    def args(self):
        return {
            'errorType': self.error_type.name,
            'message': self.message,
        }

    def json(self):
        return json.dumps(self.args())
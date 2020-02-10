import json
from enum import Enum

class ErrorType(Enum):
    '''
    Defines errors that may occur when making calls to the API
    '''
    # Occurs when an unexpected error occurs duing the handling of a request
    UNEXPECTED_SERVER_ERROR = 0
    # Occurs when Django cannot reach the Solr instance.
    SOLR_CONNECTION_ERROR = 1
    # Occurs when Solr returns an error response to a search query.
    SOLR_SEARCH_ERROR = 2
    # Occurs when a search term is missing from a search request.
    INVALID_SEARCH_TERM = 3

class APIError(Exception):
    '''
    Represents an error that occurred during the processing of a request to the API.
    '''

    def __init__(self, message, error_type):
        '''
        Takes an HTTP status code and an error message (must be one of ErrorType) 
        to return to the client and creates a APIError that can be converted
        to JSON.
        '''
        self.message = message
        self.error_type = error_type
        
    def args(self):
        return {
            'message': self.message,
            'errorType': self.error_type.name,
        }

    def json(self):
        return json.dumps(self.args())
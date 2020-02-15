import json

class MockSolr(object):
    def __init__(self):
        pass
    
    def add(self, docs, commit=True):
        return docs

class MockAdmin(object):
    def __init__(self, cores):
        self.cores = cores
    
    def status(self):
        status_reponse = {
            "status": {}
        }
        
        for core in self.cores:
            status_reponse["status"][core] = core
            
        return json.dumps(status_reponse)
    
class MockResponse(object):
    def __init__(self, content):
        self.content = content
        
    def json(self):
        return self.content
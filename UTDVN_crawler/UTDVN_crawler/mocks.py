from scrapy.http import Request, TextResponse

# Creates a fake HTTP response from a given HTML file
def mock_response(file_path, url=None):
    
    if not url:
        url = 'https://repository.vnu.edu.vn/community-list'
    
    request = Request(url=url)
    file_content = open('UTDVN_crawler/UTDVN_crawler' + file_path, 'r').read()
    
    response = TextResponse(
        url=url,
        request=request,
        body=file_content,
        encoding='utf-8'
    )
    
    return response
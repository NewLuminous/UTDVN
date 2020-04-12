import Client from '../src/client';

const TEST_URL = 'http://localhost:8000/api';

describe('client', () => {
    test('_stringParams with undefined params', () => {
        const result = Client._stringParams(undefined);
        expect(result).toEqual('');
    });

    test('_stringParams', () => {
        const result = Client._stringParams({
            teststring: 'test',
            anumber: 7,
        });
        expect(result).toEqual('?teststring=test&anumber=7');
    });

    test('_get', (done) => {
        const mockResponse = '{ "data": "test" }';
        fetch.mockResponseOnce(mockResponse);

        const params = {
            q: 'test',
        }
        
        const client = new Client(TEST_URL);
        client._get('/get', params).then(response => {
            expect(response).toEqual(JSON.parse(mockResponse));
            done();
        });
    });

    test('search', (done) => {
        const mockResponse = '{ "data": "test" }';
        fetch.mockResponseOnce(mockResponse);
        
        const client = new Client(TEST_URL);
        client.search('somequery', 'test').then(response => {
            expect(response).toEqual(JSON.parse(mockResponse));
            done();
        });
    });
});
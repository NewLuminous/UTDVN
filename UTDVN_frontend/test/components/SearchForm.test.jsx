import React from 'react';
import Client from '../../src/client';
import SearchForm from '../../src/components/SearchForm';
import { ThesisResult } from '../../src/components/ResultTypes';
import { shallow, mount } from 'enzyme';

describe('<SearchForm />', () => {
    const client = new Client('FAKE_URL');

    test('handleChange', () => {
        const result = mount(<SearchForm client={client}/>);
        const input = result.find('input');

        input.simulate('change', { target: { value: 'testing' } });
        expect(result.state().query).toEqual('testing');
    });

    test('handleKeyPress', () => {
        const result = mount(<SearchForm client={client}/>);
        const input = result.find('input');

        result.instance().handleSubmit = jest.fn();
        result.update();

        input.simulate('change', { target: { value: 'testing' } });
        input.simulate('keypress', { key: 'Enter' });
        expect(result.instance().handleSubmit).toBeCalled();
    });

    test('handleSubmit with empty query', () => {
        const result = mount(<SearchForm client={client}/>);

        result.state().query = '';
        result.instance().setState = jest.fn();
        result.instance().handleSubmit();
        expect(result.instance().setState).not.toBeCalled();
    });

    test('handleSubmit with non-empty query', (done) => {
        const mockClient = new Client('FAKE_URL');
        const result = mount(<SearchForm client={mockClient}/>);

        result.state().query = 'test';
        mockClient.search = jest.fn(() => {
            return Promise.resolve();
        });
        result.instance().handleResponse = jest.fn(() => {
            expect(mockClient.search).toBeCalled();
            expect(result.state()).toEqual({
                query: 'test',
                results: [],
                noResults: false,
                errored: false,
                queryId: 1,
            });
            done();
        });
        result.instance().handleSubmit();
    });

    test('handleSubmit with errors', (done) => {
        const mockClient = new Client('FAKE_URL');
        const result = mount(<SearchForm client={mockClient}/>);

        result.state().query = 'test';
        mockClient.search = jest.fn(() => {
            return Promise.reject('FAKE_ERROR');
        });
        result.instance().handleError = jest.fn(() => {
            expect(mockClient.search).toBeCalled();
            expect(result.state()).toEqual({
                query: 'test',
                results: [],
                noResults: false,
                errored: false,
                queryId: 1,
            });
            done();
        });
        result.instance().handleSubmit();
    });

    test('handleError', () => {
        const result = mount(<SearchForm client={client}/>);
        
        result.instance().handleError('FAKE_ERROR');
        expect(result.state()).toEqual({
            query: '',
            results: [],
            noResults: false,
            errored: true,
            queryId: 0,
        });
    });

    test('handleResponse with error response', () => {
        const result = mount(<SearchForm client={client}/>);

        const response = {errorType: 'UNKNOWN', message: 'OOPS'};
        result.instance().handleError = jest.fn();
        result.instance().handleResponse(response);
        expect(result.instance().handleError).toBeCalled();
    });

    test('handleResponse with valid response', () => {
        const result = mount(<SearchForm client={client}/>);
        const mockResult = {
            id: 'testid',
            title: 'A simple title',
            author: 'someone',
            description: 'The quick brown fox jumps over the lazy dog',
            updatedAt: '9999-04-01T00:01:02Z',
            yearpub: 9999,
            publisher: 'university',
            uri: 'http://www.site.com',
            keywords: []
        };
        const mockResponse = {
            data: [
                {
                    response: {
                        numFound: 1,
                        start: 0,
                        docs: [mockResult]
                    },
                    highlighting: {
                        'testid': {
                            description: ['The quick brown <em>fox</em> jumps over the lazy <em>dog</em>']
                        }
                    },
                    type: 'thesis'
                }
            ]
        };
        const expectedResult = new ThesisResult(
            mockResult.id,
            mockResult.title,
            mockResult.author,
            'The quick brown <em>fox</em> jumps over the lazy <em>dog</em>',
            mockResult.yearpub,
            mockResult.publisher,
            mockResult.uri,
            mockResult.keywords
        );

        result.instance().handleResponse(mockResponse);
        expect(result.state()).toEqual({
            query: '',
            results: [expectedResult],
            noResults: false,
            errored: false,
            queryId: 0,
        });
    })

    test('getMessage when error occured', () => {
        const result = mount(<SearchForm client={client}/>);
        result.state().errored = true;

        const message = shallow(result.instance().getMessage()).find('h4');
        expect(message.length).toEqual(1);
        expect(message.text()).toEqual('Oops! An error occurred while performing your search.');
    });

    test('getMessage when there are no results', () => {
        const result = mount(<SearchForm client={client}/>);
        result.state().noResults = true;

        const message = shallow(result.instance().getMessage()).find('h4');
        expect(message.length).toEqual(1);
        expect(message.text()).toEqual('No results found :(');
    });

    test('getMessage when there are any results', () => {
        const result = mount(<SearchForm client={client}/>);
        result.state().noResults = false;

        const message = result.instance().getMessage();
        expect(message).toBeUndefined();
    });

    test('getResults', () => {
        const result = mount(<SearchForm client={client}/>);
        result.state().queryId = 7;

        const resultList = result.instance().getResults();
        expect(resultList.props.queryId).toEqual(7);
    });

    it('should render correctly', () => {
        const result = mount(<SearchForm client={client}/>);

        expect(result.find('input').length).toEqual(1);
        expect(result.find('button').length).toEqual(1);
        expect(result.find('ResultList').length).toEqual(1);
    });
});
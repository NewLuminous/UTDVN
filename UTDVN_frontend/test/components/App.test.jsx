import React from 'react';
import Client from '../../src/client';
import App from '../../src/components/App';
import SearchForm from '../../src/components/SearchForm';
import { mount } from 'enzyme';

describe('<App />', () => {
    it('should contain one SearchForm', () => {
        const client = new Client();
        const result = mount(<App client={client}/>);
        expect(result.find(SearchForm).length).toEqual(1);
    });
});
import React from 'react';
import ResultList from '../../src/components/ResultList';
import { ThesisResult } from '../../src/components/ResultTypes';
import { mount } from 'enzyme';

describe('<ResultList />', () => {
    test('getResultList', () => {
        const mockResult1 = new ThesisResult('id1', 'a simple title', 'sb', '', 9999, 'pub', 'a.com', []);
        const mockResult2 = new ThesisResult('id2', 'a simple title', 'sb', '', 9999, 'pub', 'a.com', []);
        
        const resultList = mount(<ResultList results={[mockResult1, mockResult2]}/>).instance().getResultList();
        expect(resultList.length).toEqual(2);
        const result = mount(resultList[0]);

        const div = result.find('div').at(0);
        expect(div.find('ResultItem').length).toEqual(1);
    });

    it('should render correctly', () => {
        const result = mount(<ResultList results={[]}/>);
        expect(result.find('div').length).toEqual(1);
    });
});
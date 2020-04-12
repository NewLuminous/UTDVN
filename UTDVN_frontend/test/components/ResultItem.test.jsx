import React from 'react';
import ResultItem from '../../src/components/ResultItem';
import { shallow, mount } from 'enzyme';

describe('<ResultItem />', () => {
    test('highlight with undefined text', () => {
        const resultItem = mount(<ResultItem id='' title='' author=''/>);
        const result = resultItem.instance().highlight(undefined);
        expect(result).toBeNull();
    });

    test('highlight with highlighted text', () => {
        const text = 'The quick brown <em>fox</em> jumps over the lazy <em>dog</em>';
        const resultItem = mount(<ResultItem id='' title='' author=''/>);
        const result = shallow(resultItem.instance().highlight(text));
        expect(result.type()).toEqual('p');
        expect(result.text()).toEqual('The quick brown fox jumps over the lazy dog');
        expect(result.find('b').length).toEqual(2);
        expect(result.find('b').at(0).text()).toEqual('fox');
        expect(result.find('b').at(1).text()).toEqual('dog');
    });

    test('highlight without highlights', () => {
        const text = 'The quick brown fox jumps over the lazy dog';
        const resultItem = mount(<ResultItem id='' title='' author=''/>);
        const result = shallow(resultItem.instance().highlight(text));
        expect(result.type()).toEqual('p');
        expect(result.text()).toEqual('The quick brown fox jumps over the lazy dog');
        expect(result.find('b').length).toEqual(0);
    });

    it('should render correctly', () => {
        const result = mount(
            <ResultItem
                id='identifier'
                title='A <em>highlighted</em> title'
                author='developer'
                description='The quick brown <em>fox</em> jumps over the lazy <em>dog</em>'
            />
        );

        const div = result.find('div');
        expect(div.length).toEqual(1);

        const a = div.childAt(0);
        expect(a.type()).toEqual('a');

        const title = a.childAt(0);
        expect(title.type()).toEqual('p');
        expect(title.text()).toEqual('A highlighted title');
        expect(title.find('b').length).toEqual(1);
        expect(title.find('b').text()).toEqual('highlighted');

        const author = div.childAt(1);
        expect(author.type()).toEqual('p');
        expect(author.text()).toEqual('developer');

        const desc = div.childAt(2);
        expect(desc.type()).toEqual('p');
        expect(desc.text()).toEqual('The quick brown fox jumps over the lazy dog');
        expect(desc.find('b').length).toEqual(2);
        expect(desc.find('b').at(0).text()).toEqual('fox');
        expect(desc.find('b').at(1).text()).toEqual('dog');
    });
});
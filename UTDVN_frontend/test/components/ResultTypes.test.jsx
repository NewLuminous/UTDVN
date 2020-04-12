import { ThesisResult } from '../../src/components/ResultTypes';

const id = 'testid';
const title = 'a simple title';
const author = 'someone';
const description = 'this is a text';
const yearpub = 9999;
const publisher = 'university';
const uri = 'www.test.com';
const keywords = ['kw1', 'kw2'];

describe('ThesisResult', () => {
    it('should be instantiable', () => {
        const thesis = new ThesisResult(id, title, author, description, yearpub, publisher, uri, keywords);
        expect(thesis.id).toEqual(id);
        expect(thesis.title).toEqual(title);
        expect(thesis.author).toEqual(author);
        expect(thesis.description).toEqual(description);
        expect(thesis.yearpub).toEqual(yearpub);
        expect(thesis.publisher).toEqual(publisher);
        expect(thesis.uri).toEqual(uri);
        expect(thesis.keywords).toEqual(keywords);
    })
});
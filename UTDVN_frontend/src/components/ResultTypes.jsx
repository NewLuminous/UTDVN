export class ThesisResult {
    /**
     * Creates a ThesisResult from the given search result data
     * @param {String} id
     * @param {String} title
     * @param {String} author
     * @param {String} description
     * @param {Number} yearpub
     * @param {String} publisher
     * @param {String} uri
     * @param {Array<String>} keywords
     */
    constructor(id, title, author, description, yearpub, publisher, uri, keywords) {
        this.id = id;
        this.title = title;
        this.author = author;
        this.description = description;
        this.yearpub = yearpub;
        this.publisher = publisher;
        this.uri = uri;
        this.keywords = keywords;
    }
}
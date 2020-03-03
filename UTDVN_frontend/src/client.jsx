import "whatwg-fetch"

export default class Client {
    constructor(url) {
        this.url = url;
    }

    /**
     * Returns a string representation of the given parameters to be used in a HTTP request.
     * @param {Object} params A JSON object of key-value pairs representing the parameters of a request.
     */
    static _stringParams(params) {
        if (params === undefined) return '';
        let paramList = [];
        for (var key in params) {
            paramList.push(key + '=' + params[key]);
        }
        return '?' + paramList.join('&');
    }

    /**
     * Makes a GET request to the given API endpoint with the given params and
     * returns the response in JSON format,
     * or throws an error.
     * @param {String} endpoint
     * @param {Object} params
     */
    async _get(endpoint, params) {
        try {
            const uri = this.url + endpoint + Client._stringParams(params);
            const response = await fetch(uri);
            return await response.json();
        } catch (e) {
            throw e;
        }
    }

    /**
     * Makes a search API call to the given core with the given query and
     * returns the response in JSON format,
     * or throws an error.
     * @param {String} query
     * @param {String} types May be undefined, in which case we search all cores.
     */
    async search(query, types) {
        const params = {
            q: query,
            rows: 100,
        };

        if (types) {
            params.types = types;
        }
        return await this._get('/search', params);
    }
}
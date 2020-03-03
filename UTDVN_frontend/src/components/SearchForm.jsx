import React from 'react';
import PropTypes from 'prop-types';
import Client from '../client.jsx';
import ResultList from './ResultList.jsx';
import { ThesisResult } from './ResultTypes.jsx';

export default class SearchForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            query: '',
            results: [],
            noResults: false,
            errored: false,
            queryId: 0,
        };

        this.handleChange = this.handleChange.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleError = this.handleError.bind(this);
        this.handleResponse = this.handleResponse.bind(this);
        this.getMessage = this.getMessage.bind(this);
        this.getResults = this.getResults.bind(this);
    }

    /**
     * Called when the user writes into the input field.
     * Updates component state to reflect the content in the search field.
     * @param {Event} event
     */
    handleChange(event) {
        this.setState({ query: event.target.value });
    }

    /**
     * Called when the user presses a key on in the input field.
     * If the user presses enter this will submit the search query.
     * @param {Event} event
     */
    handleKeyPress(event) {
        if (event.key === 'Enter') {
            this.handleSubmit();
        }
    }

    /**
     * Called when the user clicks the submit button.
     * Makes a search query and updates the component state to show the results in the response.
     */
    handleSubmit() {
        if (this.state.query.length === 0) return;
        this.setState({
            noResults: false,
            queryId: this.state.queryId + 1,
        });
        this.props.client.search(this.state.query)
            .then(this.handleResponse)
            .catch(this.handleError);
    }

    /**
     * Updates the component state to show the error that occurred.
     * @param {Exception} error
     */
    handleError(error) {
        this.setState({ errored: true });
        console.log('An error occurred handling the search request: ' + error);
    }

    /**
     * Udpates the component state to show the results in the given response.
     * @param {Object} response
     */
    handleResponse(response) {
        if (response.errorType) {
            this.handleError(response.errorType + ': ' + response.message);
            return;
        }

        let results = [];

        response.data.forEach(dataset => {
            const docs = dataset.response.docs;
            const highlights = dataset.highlighting;
            switch (dataset.type) {
                case 'thesis':
                    results = results.concat(docs.map(doc => {
                        return new ThesisResult(
                            doc.id,
                            highlights[doc.id]['title'] ? highlights[doc.id]['title'][0] : doc.title,
                            doc.author,
                            highlights[doc.id]['description'] ? highlights[doc.id]['description'][0] : doc.description,
                            doc.yearpub,
                            doc.publisher,
                            doc.uri,
                            doc.keywords,
                        );
                    }));
                    break;
            }
        });

        this.setState({
            results: results,
            noResults: results.length === 0,
        });
    }

    /**
     * Returns a message to display if there are no search results,
     * otherwise returns undefined.
     */
    getMessage() {
        if (this.state.errored) {
            return <h4>Oops! An error occurred while performing your search.</h4>;
        } else if (this.state.noResults) {
            return <h4>No results found :(</h4>;
        }
    }

    /**
     * Returns a ResultList or a ResultGraph component containing search results
     * depending on this.props.graphView.
     */
    getResults() {
        return <ResultList
            results={this.state.results}
            queryId={this.state.queryId}
        />;
    }

    render() {
        return (
            <div className='input-group'>
                <div className='input-group add-on'>
                    <input
                        id='search-input'
                        className='form-control'
                        type='text'
                        value={this.state.query}
                        onChange={this.handleChange}
                        onKeyPress={this.handleKeyPress}
                        placeholder='Search keywords...'
                    />
                    <div className='input-group-btn'>
                        <button
                            className='btn btn-primary'
                            type='button'
                            onClick={this.handleSubmit} >
                            <i className='glyphicon glyphicon-search'></i>
                        </button>
                    </div>
                </div>
                { this.getMessage() }
                { this.getResults() }
            </div>
        )
    }
}

SearchForm.propTypes = {
    client: PropTypes.instanceOf(Client)
}
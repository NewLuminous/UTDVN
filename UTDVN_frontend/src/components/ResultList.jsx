import React from 'react';
import PropTypes from 'prop-types';
import ResultItem from './ResultItem.jsx';
import { ThesisResult } from './ResultTypes.jsx';

export default class ResultList extends React.Component {
    constructor(props) {
        super(props);
        this.getResultList = this.getResultList.bind(this);
    }

    /**
     * Returns a list of components containing the results.
     */
    getResultList() {
        return this.props.results.map(result =>
            <div className='row' key={result.id}>
                <ResultItem
                    id={result.uri}
                    title={result.title}
                    author={result.author}
                    description={result.description}
                />
            </div>
        );
    }

    render() {
        const resultList = this.getResultList();
        return (
            <div className='container'>
                {resultList}
            </div>
        )
    }
}

ResultList.propTypes = {
    results: PropTypes.arrayOf(PropTypes.oneOfType([
        PropTypes.instanceOf(ThesisResult)
    ])),
    queryId: PropTypes.number,
};
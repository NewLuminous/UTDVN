import React from 'react';
import styles from '../styles.js';
import PropTypes from 'prop-types';

export default class ResultItem extends React.Component {
    constructor(props) {
        super(props);
    }

    /**
     * Returns the given text as a <p> element
     * with any <em> elements filtered from the text and rendered as <b> HTML tags.
     * @param {String} text
     */
    highlight(text) {
        if (!text) return null;
        let chunks = text.split(/<em>(.*?)<\/em>/g);
        chunks = chunks.map((chunk, index) => {
            return index % 2 == 1 ? (<b key={chunk + index}>{chunk}</b>) : chunk;
        });
        return (
            <p style={styles.description}>{chunks}</p>
        )
    }

    render() {
        const title = this.highlight(this.props.title);
        return (
            <div className='container' key={this.props.id} style={styles.itemsContainer}>
                <a href={this.props.id} style={styles.title}>{title}</a>
                <p style={styles.sideTitle}>{this.props.author}</p>
                {this.highlight(this.props.description)}
            </div>
        )
    }
}

ResultItem.propTypes = PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    author: PropTypes.string.isRequired,
    description: PropTypes.string
});
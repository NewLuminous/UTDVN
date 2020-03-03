import React from 'react';
import SearchForm from './SearchForm.jsx';
import PropTypes from 'prop-types';
import Client from '../client.jsx';

export default class App extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
				<nav className='navbar navbar-default'>
					<div className='container-fluid'>
						<div className='navbar-header'>
							<a className='navbar-brand'>UTDVN</a>
						</div>
						<div className='collapse navbar-collapse' id='navbar-collapse'>
							<ul className='nav navbar-nav'>
								<li id='toggle-view'>
									<a>Toggle View</a>
								</li>
							</ul>
						</div>
					</div>
				</nav>
				<div className='container-fluid'>
					<SearchForm client={this.props.client}/>
				</div>
			</div>
        );
    }
}

App.propTypes = {
	client: PropTypes.instanceOf(Client)
}
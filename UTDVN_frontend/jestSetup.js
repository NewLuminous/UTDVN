/**
 * This file is executed when using the command "yarn jest".
 * It configures adapter of Enzyme, a test framework for React.
 * See also: https://github.com/airbnb/enzyme
 */

import { configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

configure({ adapter: new Adapter() });

// Mock whatwg-fetch globally
global.fetch = require('jest-fetch-mock');
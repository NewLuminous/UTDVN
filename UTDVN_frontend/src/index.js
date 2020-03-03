import React from 'react';
import ReactDOM from 'react-dom';
import App from "./components/App.jsx";
import Client from "./client.jsx";

const BASE_URL = 'http://localhost:8000/api';
var client = new Client(BASE_URL);

ReactDOM.render(<App client={client}/>, document.getElementById("root"));
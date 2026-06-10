import '@testing-library/jest-dom';

// React Router 7 w środowisku Jest/jsdom wymaga TextEncoder/TextDecoder.
const { TextEncoder, TextDecoder } = require('util');

global.TextEncoder = global.TextEncoder || TextEncoder;
global.TextDecoder = global.TextDecoder || TextDecoder;

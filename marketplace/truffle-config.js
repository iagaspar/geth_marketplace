require('babel-register');
require('babel-polyfill');

module.exports = {
  networks: {
    development: {
      host: "10.20.30.7",
      port: 8557,
      network_id: "*", // Match any network id
      gas:  4963969,
    },
  },
  contracts_directory: './src/contracts/',
  contracts_build_directory: './src/abis/',
  compilers: {
    solc: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  }
}

[![Build Status](https://travis-ci.org/FeatherLightApp/FeatherLight-API.svg?branch=master)](https://travis-ci.org/FeatherLightApp/FeatherLight-API)

# FeatherLight API

FeatherLight is a GraphQL API for interacting with a custodial Bitcoin Lightning Network node. The node supports many users and handles the transfer of funds internally with an accounting system and externally via regular lightning network payments.

FeatherLight also supports GraphQL subscriptions for sending realtime payment data to any device capable of websocket connections. This is intended to enable both real-time browser based payments in any website, as well as enabling IoT devices to accept and manage payments without having to run a lightning node locally.

The repo is a fully featured FeatherLight setup which automatically builds everything from bitcoin core, lnd, lndmon and the GraphQL server. It is possible to use the bitcoin backend of your choice (btcd, neutrino, etc.) but these are not configured nor tested.

FeatherLight has many dependencies in many different languages. Docker is the best way to get a node up and running.

### Features

* Add, pay, and view lightning invoices ⚡️⚡
* Access accounts in a sleek and open source [Web App](https://featherlight.app)
* Prepay wallet creation! 🎉 Start your friends off immediately with a pre-funded wallet.
* Full transaction history. Query paginated feed of all past transactions, on or off-chain
* Delegated account access with macaroons. Allow others to create invoices on your behalf!
* Deposit funds on or off-chain
* Websockets securely push invoice data to any device in realtime. Integrate with IoT!
* Strongly typed GraphQL API ensures you only get what you ask for
* Support for hold invoices (planned)
* Seamlessly interact with lApps using WebLn (planned)

#### Setup

1. git clone https://github.com/FeatherLightApp/FeatherLight-API
2. cd FeatherLight-API
3. mv .env1 .env
4. Configure desired settings in container.env and .env
5. docker-compose up -d

*Warning* Currently setup with no seed backup for debugging purposes. Change this in the lnd/dockerfile or you risk losing funds.

### Usage

1. The GraphQL endpoint is exposed at localhost:5001/graphql. You can view and interact with schema from the GraphQL playground. Schema is also found in ariadne_server/schema. Further docs are pending.
2. Grafana dashboards are exposed at localhost:3001. Monitor and view node data over time. A password should be set to prevent outside access.
3. pytest suite can be run with `docker-compose run --rm ariadne python -m pytest -s -x`. Further tests are pending.
4. A web app GUI is available for creating accounts at [FeatherLight.app](https://featherlight.app)



### Reponsible Disclosure

This software is responsible for handling and transfering valuable Bitcoins. If you have found a vulnerability in the software please email me at hello@seanaye.ca. 

### TODOs

- ~~Implement LSAT minting and db integration~~
- ~~Add interceptor for created LSATs~~
- ~~Add mutation to redeem LSATs~~
- Add travis and coveralls
- split admin routes into secondary service and federate it
- ~~fix zmqpubhashblock port binding~~
- ~~subclass graphql to provide http only refresh macaroons on token payload responses~~
- ~~change from jwt to macaroons~~
- CHANGE TO DEFAULT ENUM TYPES ON ARIADNE 0.12 RELEASE
- ~~switch from hex data to bytea in postgres~~
- ~~restructure context object~~
- ~~consolidate DB_User and UserAPI~~
- ~~remove protobuf to dict~~
- add support for lnurl
- add hold invoices
- ~~restructure schema~~
- ~~write subscriptions~~
- ~~consolidate configs into global config~~
- mypy type checking - in progress
- write more app level tests - in progress
- ~~switch to argon2 cffi password hashing~~
- ~~restructure code directory~~
- ~~create simple frontend for api~~

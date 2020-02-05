# GraphLightning

GraphLighting is a GraphQL API for interacting with a custodial Bitcoin Lightning Network node. The node supports many users and handles the transfer of funds internally with an accounting system and externally via regular lightning network payments.

GraphLighting also supports GraphQL subscriptions for sending realtime payment data to any device capable of websocket connections. This is intended to enable both real-time browser based payments in any website, as well as enabling IoT devices to accept and manage payments without having to run a lightning node locally.

GraphLightning has many dependencies in many different languages. Docker is the best way to get a node up and running.

#### Setup

1. Ensure python is installed on the system
2. `cd ariadne`
3. `python code/helpers/generate_keys.py`
4. Configure /ariadne/code/app_config.json
5. Configure /btcd/btcd.conf
6. Configure /lnd/lnd.conf
7. `docker-compose up`


### Reponsible Disclosure

This software is responsible for handling and transfering valuable Bitcoins. If you have found a vulnerability in the software please email me at sean.aye2@gmail.com. 

### TODOs

- write subscriptions
- mypy type checking
- write function level tests
- write app level tests
- switch to argon2 cffi password hashing
- create simple frontend for api

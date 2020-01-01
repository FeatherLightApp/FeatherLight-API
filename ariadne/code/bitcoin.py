from rpyc.classic import connect
import app_config as config

client = connect(config['bitcoind']['rpc'])

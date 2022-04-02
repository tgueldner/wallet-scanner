import logging
import logging.config
import os
import time
from queue import Queue

import yaml
from threading import Thread
from keys.api import ETH_API_KEY, BSC_API_KEY, POLY_API_KEY
from keys.telegram import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN
from web3 import Web3

w3 = Web3()

from ScanWatch.Client import Client
from ScanWatch.utils.enums import NETWORK

clients = {
    NETWORK.ETHER: Client(ETH_API_KEY, NETWORK.ETHER),
    NETWORK.BSC: Client(BSC_API_KEY, NETWORK.BSC),
    NETWORK.POLYGON: Client(POLY_API_KEY, NETWORK.POLYGON)
}

queues = {k: Queue(10) for k in clients.keys()}

logging_yaml_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "resources", "logging_config.yaml")
)


def setup_logging():
    with open(logging_yaml_path, "r") as f:
        config = yaml.safe_load(f.read())
        config["handlers"]["telegram"]["token"] = TELEGRAM_TOKEN
        config["handlers"]["telegram"]["chat_id"] = TELEGRAM_CHAT_ID
        logging.config.dictConfig(config)


def generateAccount():
    while True:
        account = w3.eth.account.create()
        for c in clients.values():
            queues[c.nt_type].put(account)
        logger.debug('Produced {} (fill level {})'
            .format(
                account.address,
                '/'.join([str(q.qsize()) for q in queues.values()])
            )
        )
        time.sleep(0.1)


def handleHit(account, client):
    logger.info("HIT on {] for {}".format(client.nt_type, account.address))
    logger.info("private key: {}".format(account.key.hex()))


def checkAccount(account, client):
    try:
        balance = client.get_balance(account.address)
        logger.debug(("{}: {} = {}").format(client.nt_type, account.address, balance))
        if balance > 0:
            handleHit(account, client)
        time.sleep(1)
    except Exception as err:
        logger.debug("Error on client {}: {}".format(client.nt_type, err))
        print(err)


def worker(network, number):
    logger.debug("Start worker {}#{}".format(network, number))
    while True:
        q = queues[network]
        account = q.get()
        checkAccount(account, clients[network])
        q.task_done()


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    for network in clients.keys():
        for i in range(5):
            t = Thread(target=worker, args=(network, i,))
            t.start()
    Thread(target=generateAccount).start()

    logger.info("Scanner started!")
    while True:
        time.sleep(1)

# manager = ScanManager(ethAddress, NETWORK.ETHER, ETH_API_KEY)
# manager = ScanManager(bscAddress, NETWORK.BSC, BSC_API_KEY)
# 4 Transactions Update
# manager.update_all_transactions()
# 5 Transactions
# manager.get_transactions(TRANSACTION.NORMAL)
# manager.get_transactions(TRANSACTION.INTERNAL)
# 6 Holdings
# erc20 = manager.get_erc20_holdings()
# print(erc20)

# erc721 = manager.get_erc721_holdings()
# print(erc721)

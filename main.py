import logging
import logging.config
import os
import yaml
from keys.api import ETH_API_KEY, BSC_API_KEY, POLY_API_KEY
from keys.telegram import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN
from web3 import Web3
import time

w3 = Web3()

from ScanWatch.ScanManager import ScanManager
from ScanWatch.Client import Client
from ScanWatch.utils.enums import NETWORK, TRANSACTION

#ethAddress = "0x29c8F2A238F0e2c90cf72133873EbcAA31bD1C4c"
#bscAddress = "0xc5b793CFDc0a62911d6Ce1D209200062529eF8A0"

clients = [
    Client(ETH_API_KEY, NETWORK.ETHER),
    Client(BSC_API_KEY, NETWORK.BSC),
    Client(POLY_API_KEY, NETWORK.POLYGON)
    ]

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
    return w3.eth.account.create()


def handleHit(account, balances):
    logger.info("HIT for {}".format(account.address))
    logger.info("private key: {}".format(account.key.hex()))
    return


def checkBalance(address):
    result = {}
    for client in clients:
        balance = client.get_balance(address)
        logger.debug(("{}: {} = {}").format(client.nt_type, address, balance))
        result[client.nt_type] = balance
    return result


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    while(True):
        account = generateAccount()
        balances = checkBalance(account.address)
        balance = sum(balances.values())
        if balance > 0:
            handleHit(account, balances)

#manager = ScanManager(ethAddress, NETWORK.ETHER, ETH_API_KEY)
#manager = ScanManager(bscAddress, NETWORK.BSC, BSC_API_KEY)
# 4 Transactions Update
#manager.update_all_transactions()
# 5 Transactions
#manager.get_transactions(TRANSACTION.NORMAL)
#manager.get_transactions(TRANSACTION.INTERNAL)
# 6 Holdings
#erc20 = manager.get_erc20_holdings()
#print(erc20)

#erc721 = manager.get_erc721_holdings()
#print(erc721)
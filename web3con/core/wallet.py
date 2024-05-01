from web3 import Web3
from eth_account import Account

from web3con.core.exceptions import CanNotReachBlockchain
from web3con.core import abi


class Wallet:
    def __init__(self, private_key: str, rpc_url: str):
        self._w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not self._w3.is_connected():
            raise CanNotReachBlockchain()

        self.__chain_id = self._w3.eth.chain_id

        self.__private_key = private_key
        self.__address = Account.from_key(private_key).address

    @property
    def address(self) -> str:
        return self.__address

    def sign_transaction(self, transaction: dict) -> str | int:
        return self._w3.eth.account.sign_transaction(transaction, self.__private_key)

    def send_transaction(self, signed_transaction: dict, wait_for_result=True) -> tuple:
        tx_hash = self._w3.eth.send_raw_transaction(
            signed_transaction.rawTransaction
        ).hex()
        if wait_for_result:
            return (tx_hash, self._w3.eth.wait_for_transaction_receipt(tx_hash).status)
        return (tx_hash, None)

    def approve(self, spender: str, amount: float, abi: str, contract: str):
        contract = self._w3.eth.contract(
            address=self._w3.to_checksum_address(contract), abi=abi
        )

        tx = contract.functions.approve(
            self._w3.to_checksum_address(spender), self._w3.to_wei(amount, "ether")
        ).build_transaction(
            {
                "from": self.address,
                "value": 0,
                "nonce": self._w3.eth.get_transaction_count(self.address),
                "gasPrice": self._w3.eth.gas_price,
                "chainId": self.__chain_id,
            }
        )

        tx["gas"] = int(self._w3.eth.estimate_gas(tx))

        tx = self.sign_transaction(tx)
        return self.send_transaction(tx)

    def allowance(self, spender: str, contract: str, abi: str):
        contract = self._w3.eth.contract(
            address=self._w3.to_checksum_address(contract), abi=abi
        )
        return self._w3.from_wei(
            contract.functions.allowance(
                self._w3.to_checksum_address(self.address),
                self._w3.to_checksum_address(spender),
            ).call(),
            "ether",
        )

    def balance_of_erc20(self, address, contract_address):
        contract = self._w3.eth.contract(
            address=self._w3.to_checksum_address(contract_address),
            abi=abi.balance_of_erc20_abi,
        )
        return contract.functions.balanceOf(address).call()

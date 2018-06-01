from ethpm.pm import PM


def test_web3(w3):
    pkg_path = 'ethpm/assets/v2-packages/standard-token/1.0.0.json'

    # attach pm module to w3
    PM.attach(w3, 'pm')

    standard_token_pkg = w3.pm.get_package(pkg_path)
    StandardToken = standard_token_pkg.get_contract_type('StandardToken')

    # via web3: deploy contract with totalSupply of 1
    tx_hash = StandardToken.constructor(1).transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    simple_standard_token = StandardToken(tx_receipt.contractAddress)
    total_supply = simple_standard_token.functions.totalSupply().call()
    assert total_supply == 1

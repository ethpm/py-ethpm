from eth_utils import to_canonical_address
import pytest
from solc import compile_source
import web3

from ethpm import V2_PACKAGES_DIR, Package
from ethpm.exceptions import BytecodeLinkingError


@pytest.fixture
def compiled_safe_send():
    safe_send_source = V2_PACKAGES_DIR / "escrow" / "contracts" / "SafeSendLib.sol"
    safe_send_text = safe_send_source.read_text()
    compiled_sol = compile_source(safe_send_text)
    contract_interface = compiled_sol["<stdin>:SafeSendLib"]
    return contract_interface


def test_deployed_escrow_and_safe_send(escrow_manifest, compiled_safe_send, w3):
    # Deploy a SafeSendLib
    SafeSend = w3.eth.contract(
        abi=compiled_safe_send["abi"], bytecode=compiled_safe_send["bin"]
    )
    tx_hash = SafeSend.constructor().transact()
    tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    safe_send_address = to_canonical_address(tx_receipt["contractAddress"])

    EscrowPackage = Package(escrow_manifest, w3)
    EscrowFactory = EscrowPackage.get_contract_factory("Escrow")
    LinkedEscrowFactory = EscrowFactory.link_bytecode(
        {"SafeSendLib": safe_send_address}
    )

    # Deploy an Escrow Contract
    escrow_tx_hash = LinkedEscrowFactory.constructor(
        "0x4F5B11c860b37b68DE6D14Fb7e7b5f18A9A1bdC0"
    ).transact()
    escrow_tx_receipt = w3.eth.waitForTransactionReceipt(escrow_tx_hash)
    escrow_address = to_canonical_address(escrow_tx_receipt.contractAddress)

    # Cannot deploy with an unlinked factory
    with pytest.raises(BytecodeLinkingError):
        escrow_tx_hash = EscrowFactory.constructor(
            "0x4F5B11c860b37b68DE6D14Fb7e7b5f18A9A1bdC0"
        ).transact()

    # Cannot instantiate a contract instance from an unlinked factory
    with pytest.raises(BytecodeLinkingError):
        EscrowFactory(escrow_address)
    contract_instance = LinkedEscrowFactory(escrow_address)
    assert EscrowFactory.needs_bytecode_linking is True
    assert LinkedEscrowFactory.needs_bytecode_linking is False
    assert isinstance(contract_instance, web3.contract.Contract)
    assert to_canonical_address(safe_send_address) in LinkedEscrowFactory.bytecode
    assert (
        to_canonical_address(safe_send_address) in LinkedEscrowFactory.bytecode_runtime
    )
    assert to_canonical_address(safe_send_address) not in EscrowFactory.bytecode
    assert to_canonical_address(safe_send_address) not in EscrowFactory.bytecode_runtime

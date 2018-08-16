from typing import Any, Dict, List  # noqa: F401

import cytoolz
from eth_utils import is_address, to_canonical_address
from web3.contract import Contract
from web3.utils.decorators import combomethod

from ethpm.exceptions import BytecodeLinkingError


class LinkableContract(Contract):
    """
    A subclass of web3.contract.Contract that is capable of handling
    contract factories with link references in their package's manifest.
    """

    deployment_link_refs = None
    runtime_link_refs = None
    is_bytecode_linked = False

    def __init__(self, address: bytes = None, **kwargs: Dict[str, Any]) -> None:
        super(LinkableContract, self).__init__(address=address, **kwargs)

    @combomethod
    def has_linkable_bytecode(self) -> bool:
        """
        Return a boolean indicating the presence of linkable bytecode on this contract factory.
        """
        if self.deployment_link_refs or self.runtime_link_refs:
            return True
        return False

    @combomethod
    def link_bytecode(self, attr_dict: Dict[str, str]) -> None:
        """
        Link contract factory's deployment / runtime bytecode if refs are present in manifest.

        :attr_dict: Dict[`ContractType`: `Address`] for all deployment and runtime link references.
        """
        if not self.deployment_link_refs and not self.runtime_link_refs:
            raise BytecodeLinkingError("Contract factory has no linkable bytecode.")
        if self.is_bytecode_linked:
            raise BytecodeLinkingError(
                "Bytecode for this contract facotry has already been linked."
            )
        self.validate_attr_dict(self, attr_dict)
        self._link_links(self, attr_dict)

    def _link_links(self, attr_dict: Dict[str, str]) -> None:
        # Fill `bytecode` link references
        if self.deployment_link_refs:
            link_fns = (
                apply_link_reference(offset, ref["length"], attr_dict[ref["name"]])
                for ref in self.deployment_link_refs
                for offset in ref["offsets"]
            )
            linked_bytecode = cytoolz.pipe(self.bytecode, *link_fns)
            self.bytecode = linked_bytecode
        # Fill `bytecode_runtime` link references
        elif self.runtime_link_refs:
            link_fns = (
                apply_link_reference(offset, ref["length"], attr_dict[ref["name"]])
                for ref in self.runtime_link_refs
                for offset in ref["offsets"]
            )
            linked_bytecode_runtime = cytoolz.pipe(self.bytecode_runtime, *link_fns)
            self.bytecode_runtime = linked_bytecode_runtime

        self.is_bytecode_linked = True

    def validate_attr_dict(self, attr_dict: Dict[str, str]) -> None:
        """
        Validates that ContractType keys in attr_dict reference existing manifest ContractTypes.
        """
        attr_dict_names = list(attr_dict.keys())
        all_link_refs = (
            # Ignored type in case one of the following is None
            self.deployment_link_refs  # type: ignore
            + self.runtime_link_refs  # type: ignore
        )  # type: List[Dict[str, Any]]
        all_link_names = [ref["name"] for ref in all_link_refs]
        if set(attr_dict_names) != set(all_link_names):
            raise BytecodeLinkingError(
                """All link references must be defined when calling """
                """`link_bytecode` on a contract factory."""
            )
        for address in list(attr_dict.values()):
            if not is_address(address):
                raise BytecodeLinkingError(
                    "Address: {0} as specified in the attr_dict is not a valid address.".format(
                        address
                    )
                )


@cytoolz.curry
def apply_link_reference(
    offset: int, length: int, value: str, bytecode: bytes
) -> bytes:
    """
    Returns the new bytecode with `value` put into the location indicated by `offset` and `length`.
    """
    validate_empty_bytes(offset, length, bytecode)
    new_bytes = (
        # Ignore linting error b/c black conflict
        bytecode[:offset]
        + to_canonical_address(value)
        + bytecode[offset + length :]  # noqa: E201, E203
    )
    return new_bytes


def validate_empty_bytes(offset: int, length: int, bytecode: bytes) -> None:
    """
    Validates that segment [`offset`:`offset`+`length`] of
    `bytecode` is comprised of empty bytes (b'\00').
    """
    slot_length = offset + length
    slot = bytecode[offset:slot_length]
    if slot != b"\00" * length:
        raise BytecodeLinkingError(
            "Bytecode segment: [{0}:{1}] is not comprised of empty bytes, rather: {2}.".format(
                offset, slot_length, slot
            )
        )

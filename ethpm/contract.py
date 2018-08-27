from typing import Any, Dict, List, Type  # noqa: F401

import cytoolz
from eth_utils import is_canonical_address
from web3.contract import Contract
from web3.utils.decorators import combomethod

from ethpm.exceptions import BytecodeLinkingError, ValidationError
from ethpm.validation import validate_address, validate_empty_bytes


class LinkableContract(Contract):
    """
    A subclass of web3.contract.Contract that is capable of handling
    contract factories with link references in their package's manifest.
    """

    deployment_link_refs = []  # type: List[Dict[str, Any]]
    runtime_link_refs = []  # type: List[Dict[str, Any]]
    is_bytecode_linked = False

    def __init__(self, address: bytes = None, **kwargs: Dict[str, Any]) -> None:
        if self.has_linkable_bytecode() and not self.is_bytecode_linked:
            raise BytecodeLinkingError(
                "Contract cannot be instantiated until its bytecode is linked."
            )
        validate_address(address)
        super(LinkableContract, self).__init__(address=address, **kwargs)

    @combomethod
    def has_linkable_bytecode(self) -> bool:
        """
        Return a boolean indicating the presence of linkable bytecode
        on this contract factory or instance.
        """
        if self.deployment_link_refs or self.runtime_link_refs:
            return True
        return False

    @classmethod
    def link_bytecode(cls, attr_dict: Dict[str, str]) -> Type["LinkableContract"]:

        """
        Return a cloned contract factory with the deploymeny / runtime bytecode linked.

        :attr_dict: Dict[`ContractType`: `Address`] for all deployment and runtime link references.
        """
        if not cls.deployment_link_refs and not cls.runtime_link_refs:
            raise BytecodeLinkingError("Contract factory has no linkable bytecode.")
        if cls.is_bytecode_linked:
            raise BytecodeLinkingError(
                "Bytecode for this contract factory has already been linked."
            )
        linked_class = cls.factory(cls.web3)
        linked_class.validate_attr_dict(attr_dict)
        linked_class.bytecode = apply_all_link_references(
            linked_class.bytecode, linked_class.deployment_link_refs, attr_dict
        )
        linked_class.bytecode_runtime = apply_all_link_references(
            linked_class.bytecode_runtime, linked_class.runtime_link_refs, attr_dict
        )
        linked_class.is_bytecode_linked = True
        return linked_class

    @combomethod
    def validate_attr_dict(self, attr_dict: Dict[str, str]) -> None:
        """
        Validates that ContractType keys in attr_dict reference existing manifest ContractTypes.
        """
        attr_dict_names = list(attr_dict.keys())
        all_link_refs = (
            self.deployment_link_refs + self.runtime_link_refs
        )  # type: List[Dict[str, Any]]
        all_link_names = [ref["name"] for ref in all_link_refs]
        if set(attr_dict_names) != set(all_link_names):
            raise BytecodeLinkingError(
                "All link references must be defined when calling "
                "`link_bytecode` on a contract factory."
            )
        for address in attr_dict.values():
            if not is_canonical_address(address):
                raise BytecodeLinkingError(
                    "Address: {0} as specified in the attr_dict is not "
                    "a valid canoncial address.".format(address)
                )


def apply_all_link_references(
    bytecode: bytes, link_refs: List[Dict[str, Any]], attr_dict: Dict[str, str]
) -> bytes:
    """
    Applies all link references corresponding to a valid attr_dict to the bytecode.
    """
    if link_refs is None:
        return bytecode
    link_fns = (
        apply_link_reference(offset, ref["length"], attr_dict[ref["name"]])
        for ref in link_refs
        for offset in ref["offsets"]
    )
    linked_bytecode = cytoolz.pipe(bytecode, *link_fns)
    return linked_bytecode


@cytoolz.curry
def apply_link_reference(
    offset: int, length: int, value: bytes, bytecode: bytes
) -> bytes:
    """
    Returns the new bytecode with `value` put into the location indicated by `offset` and `length`.
    """
    try:
        validate_empty_bytes(offset, length, bytecode)
    except ValidationError:
        raise BytecodeLinkingError("Link references cannot be applied to bytecode")

    new_bytes = (
        # Ignore linting error b/c conflict b/w black & flake8
        bytecode[:offset]
        + value
        + bytecode[offset + length :]  # noqa: E201, E203
    )
    return new_bytes

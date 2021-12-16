from functools import reduce
from typing import Union

from starkware.cairo.lang.compiler.ast.cairo_types import (
    CairoType,
    TypePointer,
    TypeFelt,
)
from starkware.cairo.lang.compiler.identifier_definition import StructDefinition
from starkware.crypto.signature.signature import FIELD_PRIME
from starkware.starknet.services.api.gateway.transaction import (
    InvokeFunction as IF,
    Deploy as D,
    Transaction as T,
)


def is_felt_pointer(cairo_type: CairoType) -> bool:
    return isinstance(cairo_type, TypePointer) and isinstance(
        cairo_type.pointee, TypeFelt
    )


AddressRepresentation = Union[int, str]
Address = int


def parse_address(value: AddressRepresentation) -> Address:
    if isinstance(value, int):
        return value

    try:
        return int(value, 16)
    except TypeError as t_err:
        raise TypeError("Invalid address format.") from t_err


def net_address_from_net(net: str) -> str:
    return {
        "mainnet": "https://alpha-mainnet.starknet.io",
        "testnet": "https://alpha4.starknet.io",
    }.get(net, net)


InvokeFunction = IF
Deploy = D
Transaction = T


def is_uint256(definition: StructDefinition) -> bool:
    (struct_name, *_) = definition.full_name.path

    return (
        struct_name == "Uint256"
        and len(definition.members.items()) == 2
        and definition.members.get("low")
        and definition.members.get("high")
        and isinstance(definition.members["low"].cairo_type, TypeFelt)
        and isinstance(definition.members["high"].cairo_type, TypeFelt)
    )


MAX_UINT256 = (1 << 256) - 1
MIN_UINT256 = 0


def uint256_range_check(value: int):
    if not MIN_UINT256 <= value <= MAX_UINT256:
        raise ValueError(f"UInt256 is expected to be in range [0;2^256), got {value}")


MIN_FELT = -FIELD_PRIME / 2
MAX_FELT = FIELD_PRIME / 2


def cairo_vm_range_check(value: int):
    if not 0 <= value < FIELD_PRIME:
        raise ValueError(
            f"Felt is expected to be in range [0; {FIELD_PRIME}), got {value}"
        )


def encode_shortstring(value: str):
    if len(value) > 31:
        raise ValueError(
            f"Shortstring cannot be longer than 31 characters, got: {len(value)}"
        )
    return reduce(lambda acc, elem: (acc << 8) | elem, [ord(s) for s in value], 0)


def decode_shortstring(value: int):
    cairo_vm_range_check(value)
    return "".join([chr(i) for i in value.to_bytes(31, byteorder="big")]).replace(
        "\x00", ""
    )

#!/usr/bin/env python3
"""
parsedat_bedrock.parser

Little-Endian NBT (Bedrock) reader using standard 1-byte tag IDs.
Supports gzip/zlib/uncompressed inputs. Robust to small Bedrock preambles
before the root compound payload by brute-forcing plausible starts 0..32.

Exports
-------
parse_bedrock_leveldat(raw: bytes, preserve_types: bool, debug: bool = False) -> dict
"""

from __future__ import annotations
import gzip
import io
import struct
import zlib
from enum import IntEnum
from typing import Any, Dict, Optional, Tuple


class NBTTag(IntEnum):
    END = 0
    BYTE = 1
    SHORT = 2
    INT = 3
    LONG = 4
    FLOAT = 5
    DOUBLE = 6
    BYTE_ARRAY = 7
    STRING = 8
    LIST = 9
    COMPOUND = 10
    INT_ARRAY = 11
    LONG_ARRAY = 12

    @property
    def type_name(self) -> str:
        return {
            NBTTag.END: "end",
            NBTTag.BYTE: "byte",
            NBTTag.SHORT: "short",
            NBTTag.INT: "int",
            NBTTag.LONG: "long",
            NBTTag.FLOAT: "float",
            NBTTag.DOUBLE: "double",
            NBTTag.BYTE_ARRAY: "byte_array",
            NBTTag.STRING: "string",
            NBTTag.LIST: "list",
            NBTTag.COMPOUND: "compound",
            NBTTag.INT_ARRAY: "int_array",
            NBTTag.LONG_ARRAY: "long_array",
        }[self]


class NBTLEReader:
    """Little-Endian NBT reader over a bytes buffer (standard 1-byte tag IDs)."""

    def __init__(self, data: bytes) -> None:
        self._buf = io.BytesIO(data)

    # ----- raw I/O -----

    def tell(self) -> int:
        return self._buf.tell()

    def seek(self, pos: int) -> None:
        self._buf.seek(pos)

    def read_exact(self, n: int) -> bytes:
        b = self._buf.read(n)
        if len(b) != n:
            raise EOFError(f"Unexpected EOF at {self.tell()} while reading {n} bytes")
        return b

    def peek(self, n: int) -> bytes:
        pos = self.tell()
        b = self._buf.read(n)
        self.seek(pos)
        return b

    # ----- primitives -----

    def read_u8(self) -> int:
        return struct.unpack("<B", self.read_exact(1))[0]

    def read_i8(self) -> int:
        return struct.unpack("<b", self.read_exact(1))[0]

    def read_u16(self) -> int:
        return struct.unpack("<H", self.read_exact(2))[0]

    def read_i16(self) -> int:
        return struct.unpack("<h", self.read_exact(2))[0]

    def read_i32(self) -> int:
        return struct.unpack("<i", self.read_exact(4))[0]

    def read_i64(self) -> int:
        return struct.unpack("<q", self.read_exact(8))[0]

    def read_f32(self) -> float:
        return struct.unpack("<f", self.read_exact(4))[0]

    def read_f64(self) -> float:
        return struct.unpack("<d", self.read_exact(8))[0]

    def read_string(self) -> str:
        length = self.read_u16()
        raw = self.read_exact(length)
        return raw.decode("utf-8", errors="strict")

    # ----- NBT -----

    def read_tag_id(self) -> NBTTag:
        tid = self.read_u8()
        try:
            return NBTTag(tid)
        except ValueError:
            raise ValueError(f"Invalid tag id {tid} at offset {self.tell() - 1}")

    def read_tag_header(self) -> Tuple[NBTTag, Optional[str]]:
        """Read (tag_id, name). END has no name."""
        tag_id = self.read_tag_id()
        if tag_id == NBTTag.END:
            return tag_id, None
        name = self.read_string()
        return tag_id, name

    def read_payload(self, tag_id: NBTTag, preserve_types: bool) -> Any:
        if tag_id == NBTTag.BYTE:
            return self._wrap(self.read_i8(), tag_id, preserve_types)
        if tag_id == NBTTag.SHORT:
            return self._wrap(self.read_i16(), tag_id, preserve_types)
        if tag_id == NBTTag.INT:
            return self._wrap(self.read_i32(), tag_id, preserve_types)
        if tag_id == NBTTag.LONG:
            return self._wrap(self.read_i64(), tag_id, preserve_types)
        if tag_id == NBTTag.FLOAT:
            return self._wrap(self.read_f32(), tag_id, preserve_types)
        if tag_id == NBTTag.DOUBLE:
            return self._wrap(self.read_f64(), tag_id, preserve_types)

        if tag_id == NBTTag.BYTE_ARRAY:
            length = self.read_i32()
            if length < 0:
                raise ValueError("Negative byte array length")
            data = list(self.read_exact(length))
            return self._wrap(data, tag_id, preserve_types)

        if tag_id == NBTTag.STRING:
            s = self.read_string()
            return self._wrap(s, tag_id, preserve_types)

        if tag_id == NBTTag.LIST:
            elem_type = self.read_tag_id()
            length = self.read_i32()
            if length < 0:
                raise ValueError("Negative list length")
            items = [self._unwrap(self.read_payload(elem_type, preserve_types)) for _ in range(length)]
            if preserve_types:
                return {"type": NBTTag.LIST.type_name, "elem_type": elem_type.type_name, "value": items}
            return items

        if tag_id == NBTTag.COMPOUND:
            obj: Dict[str, Any] = {}
            while True:
                nxt = self.peek(1)
                if not nxt:
                    raise EOFError("EOF inside compound")
                if nxt[0] == NBTTag.END:
                    self.read_exact(1)  # consume END
                    break
                inner_id, name = self.read_tag_header()
                obj[name or ""] = self._unwrap(self.read_payload(inner_id, preserve_types))
            if preserve_types:
                return {"type": NBTTag.COMPOUND.type_name, "value": obj}
            return obj

        if tag_id == NBTTag.INT_ARRAY:
            length = self.read_i32()
            if length < 0:
                raise ValueError("Negative int array length")
            vals = [self.read_i32() for _ in range(length)]
            return self._wrap(vals, tag_id, preserve_types)

        if tag_id == NBTTag.LONG_ARRAY:
            length = self.read_i32()
            if length < 0:
                raise ValueError("Negative long array length")
            vals = [self.read_i64() for _ in range(length)]
            return self._wrap(vals, tag_id, preserve_types)

        if tag_id == NBTTag.END:
            return None

        raise ValueError(f"Unknown NBT tag id: {tag_id}")

    @staticmethod
    def _wrap(value: Any, tag: NBTTag, preserve: bool) -> Any:
        return {"type": tag.type_name, "value": value} if preserve else value

    @staticmethod
    def _unwrap(value: Any) -> Any:
        if isinstance(value, dict) and set(value.keys()) == {"type", "value"}:
            return value["value"]
        return value


def detect_and_decompress(raw: bytes) -> bytes:
    """
    Return decompressed payload bytes. Supports:
    - GZIP (1F 8B)
    - zlib (78 01 / 78 5E / 78 9C / 78 DA)
    - uncompressed
    """
    if len(raw) >= 2 and raw[0] == 0x1F and raw[1] == 0x8B:
        return gzip.decompress(raw)
    if len(raw) >= 2 and raw[0] == 0x78 and raw[1] in (0x01, 0x5E, 0x9C, 0xDA):
        return zlib.decompress(raw)
    try:
        return zlib.decompress(raw)
    except zlib.error:
        return raw


# ---------- Robust preamble handling (this is the bit that made your file work) ----------

def _parse_compound_payload_at(data: bytes, start: int, preserve_types: bool) -> Dict[str, Any]:
    """
    Parse a compound *payload* (sequence of named tags ending with END) starting at `start`.
    Raises on any structural error.
    """
    rdr = NBTLEReader(data)
    rdr.seek(start)
    obj: Dict[str, Any] = {}
    while True:
        tid_byte = rdr.read_u8()
        if tid_byte == NBTTag.END:
            break
        try:
            tag_id = NBTTag(tid_byte)
        except ValueError:
            raise ValueError(f"Invalid tag id {tid_byte} at offset {rdr.tell()-1}")
        name = rdr.read_string()
        obj[name] = rdr._unwrap(rdr.read_payload(tag_id, preserve_types))
    return obj


def _normal_root_header_parse(data: bytes, preserve_types: bool) -> Optional[Dict[str, Any]]:
    """
    Try the spec path: [COMPOUND][u16 name_len][name] then payload.
    Return dict on success with >=1 key, else None.
    """
    if len(data) < 3 or data[0] != NBTTag.COMPOUND:
        return None
    rdr = NBTLEReader(data)
    tag_id, name = rdr.read_tag_header()
    if tag_id != NBTTag.COMPOUND:
        return None
    obj = rdr.read_payload(tag_id, preserve_types)
    if isinstance(obj, dict) and obj:
        return {"name": name or "", "value": obj, "type": NBTTag.COMPOUND.type_name} if preserve_types else {"name": name or "", "value": obj}
    # Empty under normal header → treat as suspicious; fall back to brute force
    return None


def _bruteforce_preamble_parse(data: bytes, preserve_types: bool, window: int = 32) -> Optional[Dict[str, Any]]:
    """
    Brute-force offsets 0..window to find a plausible compound payload.
    Picks the candidate with the most keys.
    """
    best = None
    best_len = -1
    limit = min(window, max(0, len(data) - 4))
    for start in range(0, limit + 1):
        try:
            obj = _parse_compound_payload_at(data, start, preserve_types=False)  # raw dict for scoring
            if isinstance(obj, dict):
                n = len(obj)
                if n > best_len:
                    best = (start, obj)
                    best_len = n
        except Exception:
            continue
    if best is None:
        return None
    start, obj = best
    # If caller asked for preserve_types, wrap only the root (children remain plain)
    out: Dict[str, Any] = {"name": "", "value": obj}
    if preserve_types:
        out["type"] = NBTTag.COMPOUND.type_name
    # Stash debug breadcrumb so --debug can show where we started
    out["_debug_start"] = start
    out["_debug_mode"] = "bruteforce"
    out["_debug_keys"] = list(obj.keys())[:10]
    return out


# ---------- Public API ----------

def parse_bedrock_leveldat(raw: bytes, preserve_types: bool, debug: bool = False) -> Dict[str, Any]:
    """
    Parse a Minecraft Bedrock `level.dat` blob (Little-Endian NBT) into a Python dict.

    Parameters
    ----------
    raw : bytes
        Raw file contents of `level.dat` (may be gzip/zlib-compressed or uncompressed).
    preserve_types : bool
        If True, wrap primitives and arrays as {"type": <str>, "value": <Any>}.
    debug : bool
        If True, include a `_debug` key in the result with parse info.

    Returns
    -------
    dict
        Normal form: {"name": <str>, "value": <dict>}
        Typed form (if preserve_types=True): {"name": <str>, "type": "compound", "value": <dict>}
    """
    data = detect_and_decompress(raw)

    # 1) Try strict spec path first.
    result = _normal_root_header_parse(data, preserve_types)
    if result is not None:
        if debug:
            result["_debug"] = {"mode": "root-header"}
        return result

    # 2) Fall back to brute-force preamble skipper (this is what your file needs).
    result = _bruteforce_preamble_parse(data, preserve_types, window=32)
    if result is None:
        raise ValueError("Could not locate a valid compound payload in first 32 bytes")
    if debug:
        # Consolidate the internal breadcrumbs into a single _debug field
        result["_debug"] = {
            "mode": result.pop("_debug_mode", "bruteforce"),
            "start": result.pop("_debug_start", None),
            "first_keys": result.pop("_debug_keys", []),
            "num_keys": len(result["value"]) if isinstance(result.get("value"), dict) else None,
        }
    return result

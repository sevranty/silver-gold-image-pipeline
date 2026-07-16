from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
KNOWN_CRITICAL = {b"IHDR", b"PLTE", b"IDAT", b"IEND"}
SEMANTIC_ANCILLARY = {b"tRNS"}
PACKAGABLE_COLOR_TYPES = {0, 2, 4, 6}
VALID_DEPTHS = {
    0: {1, 2, 4, 8, 16},
    2: {8, 16},
    3: {1, 2, 4, 8},
    4: {8, 16},
    6: {8, 16},
}
MODES = {0: "L", 2: "RGB", 3: "P", 4: "LA", 6: "RGBA"}


@dataclass(frozen=True)
class PngChunk:
    kind: bytes
    payload: bytes


@dataclass(frozen=True)
class PngInfo:
    width: int
    height: int
    bit_depth: int
    color_type: int
    compression: int
    filter_method: int
    interlace: int
    chunks: tuple[PngChunk, ...]

    @property
    def mode(self) -> str:
        return MODES[self.color_type]

    @property
    def alpha(self) -> bool:
        return self.color_type in {4, 6} or any(chunk.kind == b"tRNS" for chunk in self.chunks)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def parse_png(data: bytes) -> PngInfo:
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("not a PNG file")

    offset = len(PNG_SIGNATURE)
    chunks: list[PngChunk] = []
    seen: set[bytes] = set()
    idat_started = False
    idat_finished = False
    saw_idat = False
    saw_iend = False
    width = height = bit_depth = color_type = compression = filter_method = interlace = None

    while offset < len(data):
        if saw_iend:
            raise ValueError("trailing data after IEND")
        if offset + 12 > len(data):
            raise ValueError("truncated PNG chunk header")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        if len(kind) != 4 or not all((65 <= value <= 90) or (97 <= value <= 122) for value in kind):
            raise ValueError("invalid PNG chunk type")
        payload_start = offset + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if crc_end > len(data):
            raise ValueError("truncated PNG chunk payload")
        payload = data[payload_start:payload_end]
        expected_crc = struct.unpack(">I", data[payload_end:crc_end])[0]
        actual_crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise ValueError(f"invalid PNG CRC for {kind.decode('ascii')}")

        if not chunks and kind != b"IHDR":
            raise ValueError("IHDR must be the first PNG chunk")
        if kind == b"IHDR":
            if b"IHDR" in seen:
                raise ValueError("duplicate PNG IHDR")
            if chunks or length != 13:
                raise ValueError("invalid PNG IHDR")
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", payload)
            if width <= 0 or height <= 0:
                raise ValueError("invalid PNG dimensions")
            if color_type not in VALID_DEPTHS or bit_depth not in VALID_DEPTHS[color_type]:
                raise ValueError("unsupported PNG bit depth or color type")
            if compression != 0 or filter_method != 0 or interlace not in {0, 1}:
                raise ValueError("unsupported PNG header")
        elif kind == b"PLTE":
            if b"PLTE" in seen:
                raise ValueError("duplicate PNG PLTE")
            if idat_started:
                raise ValueError("PLTE must precede IDAT")
            if color_type in {0, 4}:
                raise ValueError("PLTE is not allowed for grayscale PNG")
            if length == 0 or length % 3 != 0 or length > 768:
                raise ValueError("invalid PNG PLTE")
        elif kind == b"tRNS":
            if b"tRNS" in seen:
                raise ValueError("duplicate PNG tRNS")
            if idat_started:
                raise ValueError("tRNS must precede IDAT")
            if color_type not in {0, 2, 3}:
                raise ValueError("tRNS is not allowed for this PNG color type")
        elif kind == b"IDAT":
            if idat_finished:
                raise ValueError("PNG IDAT chunks must be consecutive")
            idat_started = True
            saw_idat = True
        else:
            if idat_started:
                idat_finished = True
            if kind == b"IEND":
                if b"IEND" in seen:
                    raise ValueError("duplicate PNG IEND")
                if length != 0:
                    raise ValueError("PNG IEND must be empty")
                saw_iend = True
            elif kind[0] & 0x20 == 0 and kind not in KNOWN_CRITICAL:
                raise ValueError(f"unknown critical PNG chunk: {kind.decode('ascii')}")

        chunks.append(PngChunk(kind=kind, payload=payload))
        seen.add(kind)
        offset = crc_end

    if not chunks or chunks[0].kind != b"IHDR":
        raise ValueError("missing PNG IHDR")
    if color_type == 3 and b"PLTE" not in seen:
        raise ValueError("indexed PNG requires PLTE")
    if not saw_idat:
        raise ValueError("missing PNG IDAT")
    if not saw_iend:
        raise ValueError("missing PNG IEND")
    if chunks[-1].kind != b"IEND":
        raise ValueError("IEND must be the final PNG chunk")

    assert None not in (width, height, bit_depth, color_type, compression, filter_method, interlace)
    return PngInfo(
        width=int(width),
        height=int(height),
        bit_depth=int(bit_depth),
        color_type=int(color_type),
        compression=int(compression),
        filter_method=int(filter_method),
        interlace=int(interlace),
        chunks=tuple(chunks),
    )


def clean_png(data: bytes) -> tuple[bytes, PngInfo]:
    info = parse_png(data)
    if info.bit_depth != 8 or info.color_type not in PACKAGABLE_COLOR_TYPES or info.interlace != 0:
        raise ValueError("packaging supports only non-interlaced 8-bit grayscale, RGB, grayscale-alpha, or RGBA PNG")

    preserved = bytearray(PNG_SIGNATURE)
    for chunk in info.chunks:
        if chunk.kind in KNOWN_CRITICAL or chunk.kind in SEMANTIC_ANCILLARY:
            preserved.extend(_chunk(chunk.kind, chunk.payload))
    cleaned = bytes(preserved)
    clean_info = parse_png(cleaned)
    return cleaned, clean_info

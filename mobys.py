import io
import struct

import typing


def read_ighw_headers(stream: io.BufferedReader):
    magic1, magic2, count, length = struct.unpack('>4I', stream.read(0x10))
    return {
        'magic1': magic1,
        'magic2': magic2,
        'chunks_count': count,
        'length': length
    }


def read_ighw_chunks(stream: io.BufferedReader, headers: dict[str, int]):
    for i in range(headers["chunks_count"]):
        cid, offset, count, length = struct.unpack('>4I', stream.read(0x10))
        yield {
            'id': cid,
            'offset': offset,
            'count': count,
            'length': length
        }


class Moby:
    def __init__(self, stream: io.BufferedReader, moby_ref: dict[str, int]):
        stream.seek(moby_ref["offset"])
        self.ighw_headers: dict[str, int] = read_ighw_headers(stream)
        stream.seek(moby_ref["offset"] + 0x20)
        self.ighw_chunks: typing.Generator[dict[str, int]] = read_ighw_chunks(stream, self.ighw_headers)
        for chunk in self.ighw_chunks:
            print("MOBY_CHUNKS {0} {1}: {2}".format(hex(moby_ref["tuid"]), hex(chunk["id"]), chunk))

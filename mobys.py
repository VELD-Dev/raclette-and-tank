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
        cid, offset, length, count = struct.unpack('>4I', stream.read(0x10))
        yield {
            'id': cid,
            'offset': offset,
            'count': count,
            'length': length
        }


def read_bangles(stream: io.BufferedReader):
    offset, count = struct.unpack('>2I', stream.read(0x08))
    yield {
        'offset': offset,
        'count': count
    }

def read_new_moby(stream: io.BufferedReader, offset: int, headers: dict[str, int]):
    for i1 in range(headers["count"]):
        #stream.seek(offset) # SPHERE BOUNDING (?)
        #sb_x, sb_y, sb_z, sb_radius = struct.unpack('>3He', stream.read(0x8))

        stream.seek(offset + 0x18) # REACHING BANGLES
        banglesCount1, banglesCount2 = struct.unpack('>2H', stream.read(0x04))

        stream.seek(offset + 0x24)
        for i2 in range(banglesCount1):
            offset, count = struct.unpack('>2I', stream.read(0x8))
            print("BANGLE?: (offset: {0}, count: {1})".format(offset, count))
            yield {
                'offset': offset,
                'count': count
            }


def read_moby_mesh_metadata(stream: io.BufferedReader, headers: dict[str, int]):
    for i in range(headers["count"]):
        index, vertexOffset, shaderIndex, vertexCount, boneMapIndexCount, vertexType, boneMapIndex, _uk1, _uk2, indexCount, _uk3, _uk4, _uk5, boneMapOffset = struct.unpack(
            '>2I2H4B2H4I', stream.read(0x40))
        yield {
            'index': index,
            'vertexOffset': vertexOffset,
            'shaderIndex': shaderIndex,
            'vertexCount': vertexCount,
            'boneMapIndexCount': boneMapIndexCount,
            'vertexType': vertexType,
            'boneMapIndex': boneMapIndex,
            'indexCount': indexCount,
            'boneMapOffset': boneMapOffset
        }


class Moby:
    def __init__(self, stream: io.BufferedReader, moby_ref: dict[str, int]):
        stream.seek(moby_ref["offset"])
        self.ighw_headers: dict[str, int] = read_ighw_headers(stream)
        stream.seek(moby_ref["offset"] + 0x20)
        self.ighw_chunks: typing.Generator[dict[str, int]] = read_ighw_chunks(stream, self.ighw_headers)
        for chunk in self.ighw_chunks:
            print("MOBY_CHUNKS {0} {1}: {2}".format(hex(moby_ref["tuid"]), hex(chunk["id"]), chunk))
            if chunk["id"] != 0xD100:
                continue
            self.moby_bangles = read_new_moby(stream, (moby_ref["offset"] + chunk["offset"]), chunk)
            #stream.seek(moby_ref["offset"] + chunk["offset"])
            #self.moby_bangles: typing.Generator[dict[str, int]] = read_bangles(stream, chunk)
            for bangle in self.moby_bangles:
                print("MOBY_BANGLE {0} {1}: {2}".format(hex(moby_ref["tuid"]), hex(chunk["id"]), bangle))

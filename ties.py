import typing

import io
import struct

from . import types


def read_tie(offset: int, stream: io.BufferedReader):
    res: Tie = Tie()
    stream.seek(offset)
    res.meshes_offset = struct.unpack('>I', stream.read(0x04))[0]
    stream.seek(offset + 0x0F)
    res.metadata_count = struct.unpack('>B', stream.read(0x01))[0]
    # KINDA UNSURE /// B is for Unsigned Byte, b is for Signer Byte / Means that B can't be negative, and b can be !
    stream.seek(offset + 0x14)
    res.vertex_buffer_start, res.vertex_buffer_size = struct.unpack('>2I', stream.read(0x08))
    stream.seek(offset + 0x20)
    res.scale = struct.unpack('>3f', stream.read(0x0C))
    print(res.scale)
    stream.seek(offset + 0x64)
    res.name_offset, res.tuid = struct.unpack('>IQ', stream.read(0x0C))
    return res


def read_tie_mesh(offset: int, stream: io.BufferedReader):
    res: TieMesh = TieMesh()
    stream.seek(offset)
    print(offset)
    res.indexIndex, res.vertexIndex = struct.unpack('>IH', stream.read(0x06))
    stream.seek(offset + 0x08)
    res.vertexCount = struct.unpack('>H', stream.read(0x02))
    stream.seek(offset + 0x12)
    res.indexCount = struct.unpack('>H', stream.read(0x02))
    stream.seek(offset + 0x28)
    res.oldShaderIndex = struct.unpack('>H', stream.read(0x02))
    stream.seek(offset + 0x2A)
    res.newShaderIndex = struct.unpack('>B', stream.read(0x01))
    return res


def read_ighw_header(stream: io.BufferedReader):
    res: types.IGHeader = types.IGHeader()
    magic1, magic2, count, length = struct.unpack('>4I', stream.read(0x10))
    res.magic1 = magic1
    res.magic2 = magic2
    res.chunks_count = count
    res.length = length
    return res


def read_ighw_chunks(stream: io.BufferedReader, headers: types.IGHeader, base_offset: int):
    for i in range(headers.chunks_count):
        cid, offset, length, count = struct.unpack('>4I', stream.read(0x10))
        yield {
            'id': cid,
            'offset': offset,
            'count': count,
            'length': length,
            'this_offset': base_offset
        }
        base_offset = base_offset + 0x10


class TieRefReader:
    def __init__(self, stream: io.BufferedReader, tie_ref: dict[str, int]):
        stream.seek(tie_ref["offset"])
        self.ighw_headers: types.IGHeader = read_ighw_header(stream)
        stream.seek(tie_ref['offset'] + 0x20)
        self.ighw_chunks: typing.Generator[dict[str, int]] = read_ighw_chunks(
            stream,
            self.ighw_headers,
            tie_ref['offset'] + 0x20
        )
        for chunk in self.ighw_chunks:
            print("TIE_CHUNK {0} {1}: {2}".format(hex(tie_ref['tuid']), hex(chunk['id']), chunk))
            if chunk['id'] != 0x3400:
                continue
            tie = list[CTie]().append(CTie(chunk['this_offset'], stream))


class CTie:
    def __init__(self, base_offset: int, stream: io.BufferedReader):
        tie = read_tie(base_offset, stream)
        tie_meshes: list[TieMesh] = list[TieMesh]()
        tie_mesh_offset = base_offset + tie.meshes_offset
        stream.seek(tie_mesh_offset)
        for i in range(tie.metadata_count):
            tie_mesh = read_tie_mesh(tie_mesh_offset, stream)
            tie_meshes.append(tie_mesh)
            tie_mesh_offset = tie_mesh_offset + 0x40
        self.tie = tie
        self.tie_meshes = tie_meshes
        print("TIE {0}: {1}".format(hex(self.tie.tuid), self.tie.__dict__))


class Tie(dict):
    """0x80 bytes long"""
    meshes_offset: int
    # meshes_count: int
    metadata_count: int
    vertex_buffer_start: int
    vertex_buffer_size: int
    scale: (float, float, float)
    name_offset: int
    tuid: int


class TieMesh(dict):
    """0x40 bytes long"""
    indexIndex: int
    vertexIndex: int
    vertexCount: int
    indexCount: int
    oldShaderIndex: int
    newShaderIndex: int

import typing

import io
import struct

from . import types
from .stream_helper import (StreamHelper, open_helper)


def read_tie(stream: StreamHelper):
    res: Tie = Tie()
    res.meshes_offset = stream.readUInt(0x00)
    res.metadata_count = stream.readUByte(0x0F)
    res.vertex_buffer_start = stream.readUInt(0x14)
    res.vertex_buffer_size = stream.readUInt(0x18)
    res.scale = stream.readVector3(0x20)
    res.name_offset = stream.readUInt(0x64)
    res.tuid = stream.readULong(0x68)
    print("o:{0} TIE {1}: {2}".format(hex(stream.offset), hex(res.tuid), res.__dict__))
    return res


def read_tie_mesh(stream: StreamHelper):
    res: TieMesh = TieMesh()
    res.indexIndex = stream.readUInt(0x00)
    res.vertexIndex = stream.readUShort(0x04)
    res.vertexCount = stream.readUShort(0x08)
    res.indexCount = stream.readUShort(0x12)
    res.oldShaderIndex = stream.readUShort(0x28)
    res.newShaderIndex = stream.readUByte(0x2A)
    print("o:{0} TIE_MESH {1}: {2}".format(hex(stream.offset), res.indexIndex, res.__dict__))
    return res


def read_ighw_header(stream: StreamHelper):
    res: types.IGHeader = types.IGHeader()
    res.magic1 = stream.readUInt(0x00)
    res.magic2 = stream.readUInt(0x04)
    res.chunks_count = stream.readUInt(0x08)
    res.length = stream.readUInt(0x0C)
    return res


def read_ighw_chunks(stream: StreamHelper, headers: types.IGHeader):
    for i in range(headers.chunks_count):
        ighw_chunk: types.IGSectionChunk = types.IGSectionChunk()
        ighw_chunk.id = stream.readUInt(0x00)
        ighw_chunk.offset = stream.readUInt(0x04)
        ighw_chunk.count = stream.readUInt(0x08) & 0x00FFFFFF
        ighw_chunk.length = stream.readUInt(0x0C)
        stream.jump(0x10)
        yield ighw_chunk


class TieRefReader:
    def __init__(self, stream: StreamHelper, tie_ref: types.IGAssetRef):
        stream.seek(tie_ref.offset)
        self.ighw_headers: types.IGHeader = read_ighw_header(stream)
        stream.jump(0x20)
        self.ighw_chunks: typing.Generator[types.IGSectionChunk] = read_ighw_chunks(stream, self.ighw_headers)
        for chunk in self.ighw_chunks:
            if chunk.id != 0x3400:
                continue
            print("o:{3} TIE_CHUNK {0} {1}: {2}".format(hex(tie_ref.tuid), hex(chunk.id), chunk.__dict__, hex(stream.offset)))
            ties = list[CTie]()
            stream.seek(chunk.offset + tie_ref.offset)
            for i in range(chunk.count):
                ties.append(CTie(stream))
                stream.jump(0x80)
            print(ties)


class CTie:
    def __init__(self, stream: StreamHelper):
        tie = read_tie(stream)
        tie_meshes: list[TieMesh] = list[TieMesh]()
        stream.jump(tie.meshes_offset)
        for i in range(tie.metadata_count):
            tie_mesh = read_tie_mesh(stream)
            tie_meshes.append(tie_mesh)
            stream.jump(0x40)
        self.tie = tie
        self.tie_meshes = tie_meshes


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

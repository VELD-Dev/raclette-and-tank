import typing

import io
import struct

from . import types
from .stream_helper import (StreamHelper, open_helper)


def read_tie(stream: StreamHelper, subfile_offset: int) -> types.Tie:
    res: types.Tie = types.Tie()
    res.meshes_offset = stream.readUInt(0x00)
    res.metadata_count = stream.readUByte(0x0F)
    res.vertex_buffer_start = stream.readUInt(0x14)
    res.vertex_buffer_size = stream.readUInt(0x18)
    res.scale = stream.readVector3Float(0x20)
    name_offset = stream.readUInt(0x64)
    res.tuid = stream.readULong(0x68)

    # Read name
    # previous_offset = stream.offset
    # stream.seek(subfile_offset + name_offset)
    # res.name = stream.readString()
    # stream.seek(previous_offset)
    # print("o:{0} TIE {1}: {2}".format(hex(stream.offset), hex(res.tuid), res.__dict__))
    return res


def read_tie_mesh(stream: StreamHelper):
    res: types.TieMesh = types.TieMesh()
    res.indexIndex = stream.readUInt(0x00)
    res.vertexIndex = stream.readUShort(0x04)
    res.vertexCount = stream.readUShort(0x08)
    res.indexCount = stream.readUShort(0x12)
    res.oldShaderIndex = stream.readUShort(0x28)
    res.newShaderIndex = stream.readUByte(0x2A)
    # print("o:{0} TIE_MESH {1}: {2}".format(hex(stream.offset), res.indexIndex, res.__dict__))
    return res


'''
def read_vertex(stream: StreamHelper, tie: CTie):
    res: types.MeshVertex = types.MeshVertex()
    res.location = stream.readVector3Short(0x00)
    res.UVs = (stream.readFloat16(0x08), stream.readFloat16(0x0A))
    print("o:{0} VERTEX (TUID:{1}): {2}".format(hex(stream.offset), hex(tuid), res.__dict__))
    return res
'''


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


def query_section(section_id: int, chunks: list[types.IGSectionChunk]):
    if section_id in types.TieSectionIDTypeEnum._value2member_map_:
        for section in chunks:
            if section.id == section_id:
                return section


class TieRefReader:
    def __init__(self, stream: StreamHelper, tie_ref: types.IGAssetRef):
        stream.seek(tie_ref.offset)
        self.ighw_headers: types.IGHeader = read_ighw_header(stream)
        stream.jump(0x20)
        self.ighw_chunks: list[types.IGSectionChunk] = list(read_ighw_chunks(stream, self.ighw_headers))
        vertices = list[list[types.MeshVertex]]()
        indices = []

        # READ TIES
        chunk = query_section(0x3400, self.ighw_chunks)
        # print("o:{3} TIE_CHUNK {0} {1}: {2}".format(hex(tie_ref.tuid), hex(chunk.id), chunk.__dict__, hex(stream.offset)))
        stream.seek(chunk.offset + tie_ref.offset)
        self.tie: CTie = CTie(stream, tie_ref)
        # print(self.tie.__str__())

        # READ VERTICES
        chunk = query_section(0x3000, self.ighw_chunks)
        stream.seek(chunk.offset + tie_ref.offset)
        for tie_mesh in self.tie.tie_meshes:
            mesh_vertices = list[types.MeshVertex]()
            for i in range(tie_mesh.vertexCount):
                mesh_vertices.append(self.tie.read_vertex(stream))

                stream.jump(0x14)
            vertices.append(mesh_vertices)
        self.vertices = vertices

        # READ INDICES
        chunk = query_section(0x3200, self.ighw_chunks)
        stream.seek(tie_ref.offset + chunk.offset)
        for tie_mesh in self.tie.tie_meshes:
            mesh_indices = []
            # stream.seek(tie_ref.offset + chunk.offset + (tie_mesh.indexIndex * 2))  # jump(0x06) does the same thing
            for i in range(tie_mesh.indexCount // 3):
                mesh_indices.append(read_indices(stream))
                stream.jump(0x06)
            indices.append(mesh_indices)
        self.indices = indices


def read_indices(stream: StreamHelper):
    indice: tuple[int, int, int] = (stream.readUShort(0x04), stream.readUShort(0x02), stream.readUShort(0x00))
    return indice


class CTie:
    def __init__(self, stream: StreamHelper, tie_ref: types.IGAssetRef):
        tie = read_tie(stream, stream.offset)
        tie_meshes: list[types.TieMesh] = list[types.TieMesh]()
        stream.seek(tie_ref.offset + tie.meshes_offset)
        for i in range(tie.metadata_count):
            tie_mesh = read_tie_mesh(stream)
            tie_meshes.append(tie_mesh)
            stream.jump(0x40)
        self.tie = tie
        self.tie_meshes = tie_meshes

    def read_vertex(self, stream: StreamHelper):
        res: types.MeshVertex = types.MeshVertex()
        x, z, y = stream.readVector3Short(0x00)
        sx, sz, sy = self.tie.scale
        res.location = (x * sx, y * sy, z * sz)
        res.UVs = (stream.readFloat16(0x08), stream.readFloat16(0x0A))
        # print("o:{0} VERTEX (TUID:{1}): {2}".format(hex(stream.offset), hex(self.tie.tuid), res.__dict__))
        return res

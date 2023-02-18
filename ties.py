import math

from . import rat_types
from .stream_helper import (StreamHelper)
import re


def read_tie(stream: StreamHelper, subfile_offset: int) -> rat_types.Tie:
    res: rat_types.Tie = rat_types.Tie()
    res.meshes_offset = stream.readUInt(0x00)
    res.metadata_count = stream.readUByte(0x0F)
    res.vertex_buffer_start = stream.readUInt(0x14)
    res.vertex_buffer_size = stream.readUInt(0x18)
    res.scale = stream.readVector3Float32(0x20)
    name_offset = stream.readUInt(0x64)
    res.tuid = stream.readULong(0x68)
    res.name = stream.readString(subfile_offset + name_offset, False).split("/")[-1]
    return res


def read_tie_mesh(stream: StreamHelper):
    res: rat_types.TieMesh = rat_types.TieMesh()
    res.indexIndex = stream.readUInt(0x00)
    res.vertexIndex = stream.readUShort(0x04)
    res.vertexCount = stream.readUShort(0x08)
    res.indexCount = stream.readUShort(0x12)
    res.oldShaderIndex = stream.readUShort(0x28)
    res.newShaderIndex = stream.readUByte(0x2A)
    return res


def read_ighw_header(stream: StreamHelper):
    res: rat_types.IGHeader = rat_types.IGHeader()
    res.magic1 = stream.readUInt(0x00)
    res.magic2 = stream.readUInt(0x04)
    res.chunks_count = stream.readUInt(0x08)
    res.length = stream.readUInt(0x0C)
    return res


def read_ighw_chunks(stream: StreamHelper, headers: rat_types.IGHeader):
    for i in range(headers.chunks_count):
        ighw_chunk: rat_types.IGSectionChunk = rat_types.IGSectionChunk()
        ighw_chunk.id = stream.readUInt(0x00)
        ighw_chunk.offset = stream.readUInt(0x04)
        ighw_chunk.count = stream.readUInt(0x08) & 0x00FFFFFF
        ighw_chunk.length = stream.readUInt(0x0C)
        stream.jump(0x10)
        yield ighw_chunk


def query_section(section_id: int, chunks: list[rat_types.IGSectionChunk]):
    if section_id in rat_types.TieSectionIDTypeEnum._value2member_map_:
        for section in chunks:
            if section.id == section_id:
                return section


class TieRefReader:
    def __init__(self, stream: StreamHelper, tie_ref: rat_types.IGAssetRef):
        stream.seek(tie_ref.offset)
        self.ighw_headers: rat_types.IGHeader = read_ighw_header(stream)
        stream.jump(0x20)
        self.ighw_chunks: list[rat_types.IGSectionChunk] = list(read_ighw_chunks(stream, self.ighw_headers))
        vertices = list[list[rat_types.MeshVertex]]()
        indices = []

        # READ TIE
        chunk = query_section(0x3400, self.ighw_chunks)
        stream.seek(chunk.offset + tie_ref.offset)
        self.tie: CTie = CTie(stream, tie_ref)

        # READ VERTICES
        chunk = query_section(0x3000, self.ighw_chunks)
        for tie_mesh in self.tie.tie_meshes:
            mesh_vertices = list[rat_types.MeshVertex]()
            stream.seek(chunk.offset + tie_ref.offset + (tie_mesh.vertexIndex * 0x14))
            for i in range(tie_mesh.vertexCount):
                mesh_vertices.append(self.tie.read_vertex(stream))
                stream.jump(0x14)
            vertices.append(mesh_vertices)
        self.vertices = vertices

        # READ INDICES
        chunk = query_section(0x3200, self.ighw_chunks)
        for tie_mesh in self.tie.tie_meshes:
            mesh_indices = []
            stream.seek(tie_ref.offset + chunk.offset + (tie_mesh.indexIndex * 2))  # Here for security reasons.
            for i in range(tie_mesh.indexCount // 3):
                mesh_indices.append(read_indices(stream))
                stream.jump(0x06)
            indices.append(mesh_indices)
        self.indices = indices


def read_indices(stream: StreamHelper):
    index: tuple[int, int, int] = (stream.readUShort(0x00), stream.readUShort(0x02), stream.readUShort(0x04))
    return index


class CTie:
    def __init__(self, stream: StreamHelper, tie_ref: rat_types.IGAssetRef):
        tie = read_tie(stream, tie_ref.offset)
        tie_meshes: list[rat_types.TieMesh] = list[rat_types.TieMesh]()
        stream.seek(tie_ref.offset + tie.meshes_offset)
        for i in range(tie.metadata_count):
            tie_mesh = read_tie_mesh(stream)
            tie_meshes.append(tie_mesh)
            stream.jump(0x40)
        self.tie = tie
        self.tie_meshes = tie_meshes

    def read_vertex(self, stream: StreamHelper) -> rat_types.MeshVertex:
        res: rat_types.MeshVertex = rat_types.MeshVertex()
        x, y, z = stream.readVector3Short(0x00)
        sx, sy, sz = self.tie.scale
        res.location = (x * sx, y * sy, z * sz)
        res.UVs = (stream.readFloat16(0x08), stream.readFloat16(0x0A))
        a, b, c = stream.readVector3Short(0x0C)  # stream.readUShort(0x06)
        norm = math.sqrt(a**2 + b**2)
        res.normals = (a / norm, b / norm, c / norm)
        return res

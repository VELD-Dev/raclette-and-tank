from . import types
from .stream_helper import (StreamHelper)
import re


def read_tie(stream: StreamHelper, subfile_offset: int) -> types.Tie:
    res: types.Tie = types.Tie()
    res.meshes_offset = stream.readUInt(0x00)
    res.metadata_count = stream.readUByte(0x0F)
    res.vertex_buffer_start = stream.readUInt(0x14)
    res.vertex_buffer_size = stream.readUInt(0x18)
    res.scale = stream.readVector3Float32(0x20)
    name_offset = stream.readUInt(0x64)
    res.tuid = stream.readULong(0x68)
    res.name = stream.readString(subfile_offset + name_offset, False).split("/")[-1]
    print(res.name)

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

        # READ TIE
        chunk = query_section(0x3400, self.ighw_chunks)
        # print("o:{3} TIE_CHUNK {0} {1}: {2}".format(hex(tie_ref.tuid), hex(chunk.id), chunk.__dict__, hex(stream.offset)))
        stream.seek(chunk.offset + tie_ref.offset)
        self.tie: CTie = CTie(stream, tie_ref)
        # print(self.tie.__str__())

        # READ VERTICES
        chunk = query_section(0x3000, self.ighw_chunks)
        for tie_mesh in self.tie.tie_meshes:
            mesh_vertices = list[types.MeshVertex]()
            stream.seek(chunk.offset + tie_ref.offset + (tie_mesh.vertexIndex * 0x14))
            for i in range(tie_mesh.vertexCount):
                mesh_vertices.append(self.tie.read_vertex(stream))

                stream.jump(0x14)
            vertices.append(mesh_vertices)
            print("VERTEX (TUID:{0}): {1}".format(hex(self.tie.tie.tuid), mesh_vertices[0].__dict__))
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
    index: tuple[int, int, int] = (stream.readUShort(0x04), stream.readUShort(0x02), stream.readUShort(0x00))
    return index


class CTie:
    def __init__(self, stream: StreamHelper, tie_ref: types.IGAssetRef):
        tie = read_tie(stream, tie_ref.offset)
        tie_meshes: list[types.TieMesh] = list[types.TieMesh]()
        stream.seek(tie_ref.offset + tie.meshes_offset)
        for i in range(tie.metadata_count):
            tie_mesh = read_tie_mesh(stream)
            tie_meshes.append(tie_mesh)
            stream.jump(0x40)
        self.tie = tie
        self.tie_meshes = tie_meshes

    def read_vertex(self, stream: StreamHelper) -> types.MeshVertex:
        res: types.MeshVertex = types.MeshVertex()
        x, y, z = stream.readVector3Short(0x00)
        sx, sy, sz = self.tie.scale
        res.location = (x * sx, y * sy, z * sz)
        res.multiplier = 0x7FFF # stream.readUShort(0x06)
        # print(f"o:{hex(stream.offset)} - divider: {res.multiplier}")
        res.UVs = (stream.readFloat16(0x08), stream.readFloat16(0x0A))
        nx, ny, nz = stream.readVector3Short(0x0C)
        res.normals = (nx / res.multiplier, ny / res.multiplier, nz / res.multiplier)
        # res.normals = (stream.readVector3Float16(0x0C))
        # print("o:{0} VERTEX (TUID:{1}): {2}".format(hex(stream.offset), hex(self.tie.tuid), res.__dict__))
        return res

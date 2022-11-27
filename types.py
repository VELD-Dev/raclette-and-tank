import enum


class MobyIDTypeEnum(enum.Enum):
    MOBY = 0xD100
    MOBY_MODELS = 0xD700
    MOBY_MESHES = 0xDD00
    MOBY_VERTICES = 0xE200
    MOBY_INDICES = 0xE100


class SectionIDTypeEnum(enum.Enum):
    MOBYS = 0x1D600
    TIES = 0x1D300


class TieSectionIDTypeEnum(enum.Enum):
    TIE = 0x3400
    VERTICES = 0x3000
    INDICES = 0x3200


class IGHeader(dict):
    magic1: int
    magic2: int
    chunks_count: int
    length: int


class IGSectionChunk(dict):
    id: int
    offset: int
    count: int
    length: int


class IGAssetRef(dict):
    tuid: int
    offset: int
    length: int


class MeshVertex(dict):
    location: tuple[int, int, int] | tuple[float, float, float]
    UVs: tuple[float, float]

    def __loctuple__(self):
        return self.location

    def __uvstuple__(self):
        return self.UVs


class Tie(dict):
    """0x80 bytes long"""
    meshes_offset: int
    # meshes_count: int
    metadata_count: int
    vertex_buffer_start: int
    vertex_buffer_size: int
    scale: tuple[float, float, float]
    name: str
    tuid: int


class TieMesh(dict):
    """0x40 bytes long"""
    indexIndex: int
    vertexIndex: int
    vertexCount: int
    indexCount: int
    oldShaderIndex: int
    newShaderIndex: int
    vertices: list[MeshVertex]

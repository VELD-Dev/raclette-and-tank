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


class IGHeader(dict):
    magic1: int
    magic2: int
    chunks_count: int
    length: int

import file_manager
import types
import mathutils
import stream_helper
from math import radians


class TieInstance(dict):
    """0x80 Long"""
    transformation: mathutils.Matrix
    """0x40 Long"""
    boundingPosition: mathutils.Vector | tuple[float, float, float]
    """0x0C Long"""
    boundingRadius: float
    """0x04 Long"""
    tieIndex: int
    """0x04 Long"""
    tie: types.Tie

def read_zone(stream: stream_helper, subfile_offset: int):


def read_ighw_header(stream: stream_helper.StreamHelper) -> types.IGHeader:
    header: types.IGHeader = types.IGHeader()
    header.magic1 = stream.readUInt(0x00)
    header.magic2 = stream.readUInt(0x04)
    header.chunks_count = stream.readUInt(0x08)
    header.length = stream.readUInt(0x0C)
    return header


def read_ighw_chunks(stream: stream_helper.StreamHelper, headers: types.IGHeader):
    for i in range(headers.chunks_count):
        ighw_chunk: types.IGSectionChunk = types.IGSectionChunk()
        ighw_chunk.id = stream.readUInt(0x00)
        ighw_chunk.offset = stream.readUInt(0x04)
        ighw_chunk.count = stream.readUInt(0x08) & 0x00FFFFFF
        ighw_chunk.length = stream.readUInt(0x0C)
        stream.jump(0x10)
        yield ighw_chunk


def query_section(section_id: int, chunks: list[types.IGSectionChunk]):
    if section_id in types.ZoneSectionIDTypeEnum._value2member_map_:
        for section in chunks:
            if section.id == section_id:
                return section


class ZoneReader:
    def __init__(self, stream: stream_helper.StreamHelper, zone_ref: types.IGAssetRef):
        stream.seek(zone_ref.offset)
        self.ighw_headers: types.IGHeader = read_ighw_header(stream)
        stream.jump(0x20)
        self.ighw_chunks: list[types.IGSectionChunk] = list[types.IGSectionChunk]()

        # READ TIES INSTANCES
        chunk = query_section(0x72C0, self.ighw_chunks)
        self.ties_instances


class CTieInstance(TieInstance):
    def __init__(self, stream: stream_helper.StreamHelper, tie: types.Tie):
        super().__init__()

        tuid = tie.tuid
        self.transformation = stream.readMatrix4x4(0x00)
        self.boundingPosition = stream.readVector3Float(0x40)
        self.boundingRadius = stream.readFloat32(0x4C)
        self.tieIndex = tuid
        self.tie = tie
import mathutils
from . import (file_manager, stream_helper, types)
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
    for section in chunks:
        if section.id == section_id:
            return section


class ZoneReader:
    def __init__(self, stream: stream_helper.StreamHelper, zone_ref: types.IGAssetRef):
        stream.seek(zone_ref.offset)
        self.ighw_headers: types.IGHeader = read_ighw_header(stream)
        stream.jump(0x20)
        self.ighw_chunks: list[types.IGSectionChunk] = list(read_ighw_chunks(stream, self.ighw_headers))
        self.zone_tuid = zone_ref.tuid

        # READ TIES TUIDS
        chunk = query_section(0x7200, self.ighw_chunks)
        self.ties_tuids = []
        stream.seek(zone_ref.offset + chunk.offset)
        for i in range(chunk.count):
            tuid = stream.readULong(0x00)
            print(f"o:{hex(stream.offset)} TIE_INST_TUID {i}: {hex(tuid)}")
            self.ties_tuids.append(tuid)
            stream.jump(0x08)  # Jump to the next Tie TUID
        print(self.ties_tuids)

        # READ TIES INSTANCE
        chunk = query_section(0x7240, self.ighw_chunks)
        stream.seek(zone_ref.offset + chunk.offset)
        self.ties_instances = {}
        for i in range(chunk.count):
            tie_instance = CTieInstance(stream)
            tie_instance.tuid = self.ties_tuids[tie_instance.tieIndex]
            print(f"o:{hex(stream.offset)} TIE_INST {i}: {tie_instance.__dict__}")
            stream.jump(0x80)  # Jump to the next Tie Instance
            self.ties_instances[tie_instance.tuid] = tie_instance


class CTieInstance(TieInstance):
    def __init__(self, stream: stream_helper.StreamHelper):
        super().__init__()

        self.transformation = stream.readMatrix4x4(0x00)
        self.boundingPosition = stream.readVector3Float(0x40)
        self.boundingRadius = stream.readFloat32(0x4C)
        self.tieIndex = stream.readUInt(0x50)
        self.tuid = int()

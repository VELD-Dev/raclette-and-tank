import mathutils
from . import stream_helper
from . import rat_types


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


def read_ighw_header(stream: stream_helper.StreamHelper) -> rat_types.IGHeader:
    header: rat_types.IGHeader = rat_types.IGHeader()
    header.magic1 = stream.readUInt(0x00)
    header.magic2 = stream.readUInt(0x04)
    header.chunks_count = stream.readUInt(0x08)
    header.length = stream.readUInt(0x0C)
    return header


def read_ighw_chunks(stream: stream_helper.StreamHelper, headers: rat_types.IGHeader):
    for i in range(headers.chunks_count):
        ighw_chunk: rat_types.IGSectionChunk = rat_types.IGSectionChunk()
        ighw_chunk.id = stream.readUInt(0x00)
        ighw_chunk.offset = stream.readUInt(0x04)
        ighw_chunk.count = stream.readUInt(0x08) & 0x00FFFFFF
        ighw_chunk.length = stream.readUInt(0x0C)
        stream.jump(0x10)
        yield ighw_chunk


def query_section(section_id: int, chunks: list[rat_types.IGSectionChunk]):
    for section in chunks:
        if section.id == section_id:
            return section


class CTieInstance(TieInstance):
    def __init__(self, stream: stream_helper.StreamHelper):
        super().__init__()

        self.transformation = stream.readMatrix4x4(0x00)
        self.boundingPosition = stream.readVector3Float32(0x40)
        self.boundingRadius = stream.readFloat32(0x4C)
        self.tieIndex = stream.readUInt(0x50)
        self.tuid = int()


class ZoneReader:
    ighw_headers: rat_types.IGHeader
    ighw_chunks: list[rat_types.IGSectionChunk]
    zone_tuid: int
    ties_tuids: list[int]
    ties_instances: list[CTieInstance]

    def __init__(self, stream: stream_helper.StreamHelper, zone_ref: rat_types.IGAssetRef):
        self.ighw_headers = None
        self.ighw_chunks = None
        self.zone_tuid = None
        self.ties_tuids = None
        self.ties_instances = None
        stream.seek(zone_ref.offset)
        self.ighw_headers: rat_types.IGHeader = read_ighw_header(stream)
        stream.jump(0x20)
        self.ighw_chunks: list[rat_types.IGSectionChunk] = list(read_ighw_chunks(stream, self.ighw_headers))
        self.zone_tuid = zone_ref.tuid

        # READ TIES TUIDS
        chunk = query_section(0x7200, self.ighw_chunks)
        if chunk is None:
            return
        self.ties_tuids = []
        stream.seek(zone_ref.offset + chunk.offset)
        for i in range(chunk.count):
            tuid = stream.readULong(0x00)
            self.ties_tuids.append(tuid)
            stream.jump(0x08)  # Jump to the next Tie TUID

        # READ TIES INSTANCE
        chunk = query_section(0x7240, self.ighw_chunks)
        if chunk is None:
            return
        self.ties_instances: list[CTieInstance] = []
        stream.seek(zone_ref.offset + chunk.offset)
        for i in range(chunk.count):
            tie_instance = CTieInstance(stream)
            tie_instance.tuid = self.ties_tuids[tie_instance.tieIndex]
            stream.jump(0x80)  # Jump to the next Tie Instance
            self.ties_instances.append(tie_instance)

    def gettietransform(self, tie_tuid: int, index: int = 0) -> mathutils.Matrix:
        filtered_ties = []
        for tie_instance in self.ties_instances:
            if tie_tuid is tie_instance.tuid:
                filtered_ties.append(tie_instance)
        if filtered_ties[index] is not None:
            return filtered_ties[index].transformation

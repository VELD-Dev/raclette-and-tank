import stream_helper
import types
from .utils import (read_sections_chunks, read_ighw_header, query_section)


class Debug:
    stream: stream_helper.StreamHelper
    header: types.IGHeader
    chunks: list[types.IGSectionChunk]

    def __init__(self, stream: stream_helper.StreamHelper):
        self.stream = stream
        stream.seek(0x00)
        self.header = read_ighw_header(stream)
        self.chunks = list(read_sections_chunks(self.header, stream))

    def GetMobysInstancesNames(self):
        stream = self.stream
        mobysInstNames = query_section(self.chunks, 0x73C0)
        stream.seek(mobysInstNames.offset)
        for i in range(mobysInstNames.count):
            nameinst = read_instance_name(stream)
            stream.jump(0x18)
            yield nameinst

    def GetTiesInstancesNames(self):
        stream = self.stream
        tiesInstNames = query_section(self.chunks, 0x72C0)
        stream.seek(tiesInstNames)
        for i in range(tiesInstNames.count):
            nameinst = read_instance_name(stream)
            stream.jump(0x18)
            yield nameinst

    def GetMobyPrototypeName(self, index: int):
        stream = self.stream
        mobysNames = query_section(self.chunks, 0x9480)
        stream.seek(mobysNames.offset + index * 0x10)
        return read_prototype_name(stream)

    def GetTiePrototypeName(self, index: int):
        stream = self.stream
        tiesnames = query_section(self.chunks, 0x9280)
        stream.seek(tiesnames.offset + index * 0x10)
        return read_prototype_name(stream)

    def GetShaderName(self, index: int):
        stream = self.stream
        shadernames = query_section(self.chunks, 0x5D00)
        stream.seek(shadernames + index * 0x30)
        return read_shader_name(stream)


class DebugInstanceName(dict):
    """0x18 Long"""
    tuid1: int
    tuid2: int
    name: str
    ukwn: int


class DebugAssetName(dict):
    """0x10 Long"""
    tuid: int
    name: str


class DebugMaterialName(dict):
    """0x30 Long\nGeneraly called Shader."""
    shaderTuid: int
    shaderName: str
    albedoTuid: int
    normalTuid: int
    expensiveTuid: int
    wthTuid: int
    albedoName: str
    normalName: str
    expensiveName: str
    wthName: str


def read_instance_name(stream: stream_helper.StreamHelper) -> DebugInstanceName:
    din = DebugInstanceName()
    din.tuid1 = stream.readULong(0x00)
    din.tuid2 = stream.readULong(0x08)
    din.name = stream.readString(stream.readUInt(0x10), False)
    din.ukwn = stream.readUInt(0x14)
    return din


def read_prototype_name(stream: stream_helper.StreamHelper) -> DebugAssetName:
    dan = DebugAssetName()
    dan.tuid = stream.readULong(0x00)
    dan.name = stream.readString(stream.readUInt(0x08), False)
    return dan


def read_shader_name(stream: stream_helper.StreamHelper) -> DebugMaterialName:
    dmn = DebugMaterialName()
    dmn.shaderTuid = stream.readULong(0x00)
    dmn.shaderName = stream.readString(stream.readUInt(0x08), False)
    dmn.albedoTuid = stream.readUInt(0x10)
    dmn.normalTuid = stream.readUInt(0x14)
    dmn.expensiveTuid = stream.readUInt(0x18)
    dmn.wthTuid = stream.readUInt(0x1C)
    dmn.albedoName = stream.readString(stream.readUInt(0x20), False)
    dmn.normalName = stream.readString(stream.readUInt(0x24), False)
    dmn.expensiveName = stream.readString(stream.readUInt(0x28), False)
    dmn.wthName = stream.readString(stream.readUInt(0x2C), False)
    return dmn

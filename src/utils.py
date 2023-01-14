from .types import (IGHeader, IGSectionChunk, SectionIDTypeEnum, ZoneSectionIDTypeEnum, TieSectionIDTypeEnum,
                    MobyIDTypeEnum)
from .stream_helper import StreamHelper


def read_ighw_header(stream: StreamHelper):
    header: IGHeader = IGHeader()
    header.magic1 = stream.readUInt(0x00)
    header.magic2 = stream.readUInt(0x04)
    header.chunks_count = stream.readUInt(0x08)
    header.length = stream.readUInt(0x0C)
    return header


def read_sections_chunks(headers: IGHeader, stream: StreamHelper, __relative_offset: int = 0):
    stream.seek(__relative_offset + 0x20)
    for i in range(headers.length // 0x10):
        sectionChunk: IGSectionChunk = IGSectionChunk()
        sectionChunk.id = stream.readUInt(0x00)
        sectionChunk.offset = stream.readUInt(0x04)
        sectionChunk.count = stream.readUInt(0x08)
        sectionChunk.length = stream.readUInt(0x0C)
        stream.jump(0x10)
        yield sectionChunk


def query_section(chunks: list[IGSectionChunk], section_id: int):
    if section_id in SectionIDTypeEnum._value2member_map_ or section_id in ZoneSectionIDTypeEnum._value2member_map_ or section_id in TieSectionIDTypeEnum._value2member_map_:
        for section in chunks:
            if section.id == section_id:
                return section

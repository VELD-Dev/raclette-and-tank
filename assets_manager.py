import struct
import typing
import enum

import types
from . import (file_manager, mobys, ties)
from .stream_helper import (StreamHelper, open_helper)
from .types import (SectionIDTypeEnum, MobyIDTypeEnum, IGHeader, IGAssetRef, IGSectionChunk)


class AssetManager:
    def __init__(self, fm: file_manager.FileManager, operator):
        print("AssetManager: INIT")
        isOld = fm.isIE2
        self.fm: file_manager.FileManager = fm
        self.mobys: list[IGAssetRef] = list[IGAssetRef]()
        self.ties: list[IGAssetRef] = list[IGAssetRef]()
        if isOld is False:
            print("AssetManager: Is Not Old!")
            print(fm.igfiles)
            for idx, igfile in enumerate(fm.igfiles):
                stream = fm.igfiles[igfile]
                stream.seek(0x00)
                headers = read_ighw_header(stream)
                print("----\nIGFILE {0}: {1}".format(igfile, headers.__dict__))
                if igfile == "assetlookup.dat":
                    sections_chunks = read_sections_chunks(headers, stream)
                    self.sections: list[IGSectionChunk] = list[IGSectionChunk]()
                    for section_chunk in sections_chunks:
                        self.sections.append(section_chunk)
                        print("o:{2} IGCHNK {0}: {1}".format(hex(section_chunk.id), section_chunk, stream.offset))

            for idx, igfile in enumerate(fm.otherfiles):
                stream = fm.otherfiles[igfile]
                headers = read_ighw_header(stream)
                print("----\nAM-OTHER_IGFILE {0}: {1}".format(igfile, headers.__dict__))
                if igfile == "ties.dat" and operator.use_ties:
                    self.LoadTies()
                    ties_refs = self.ties
                    for tie_ref in ties_refs:
                        print("----")
                        ties.TieRefReader(stream, tie_ref)

                '''
                if igfile == "mobys.dat" and operator.use_mobys == True:
                    self.LoadMobys()
                    mobys_refs = self.mobys
                    for moby_ref in mobys_refs:
                        print("----")
                        mobys.Moby(stream, moby_ref)
                '''
        else:
            print("AssetManager: Is Old! Aborting...")

    def LoadTies(self):
        if self.fm.isIE2:
            print("TIE_STREAM: Unsupported format !")
        else:
            self.LoadNewTies()

    def LoadNewTies(self):
        assetlookup: StreamHelper = self.fm.igfiles["assetlookup.dat"]
        tieSection = query_section(self.sections, 0x1D300)
        assetlookup.seek(tieSection.offset)
        self.ties = list[IGAssetRef]()
        for i in range(int(tieSection.length / 0x10)):
            asset_ref = IGAssetRef()
            asset_ref.tuid = assetlookup.readULong(0x00)
            asset_ref.offset = assetlookup.readUInt(0x08)
            asset_ref.length = assetlookup.readUInt(0x0C)
            print("o:{2} TIE_RAW-REF {0}: {1}".format(hex(asset_ref.tuid), asset_ref.__dict__, hex(assetlookup.offset)))

            self.ties.append(asset_ref)

    def LoadMobys(self):
        if self.fm.isIE2:
            print("MOBY_STREAM: Unsupported format!")
            # self.LoadOldMobys()
        else:
            self.LoadNewMobys()

    def LoadNewMobys(self):
        assetlookup: StreamHelper = self.fm.igfiles["assetlookup.dat"]
        mobySection = query_section(self.sections, 0x1D600)
        print("o:{2} / MOBY_SECTION {0}: {1}".format(hex(mobySection["id"]), mobySection, hex(assetlookup.offset)))
        assetlookup.seek(mobySection["offset"])

        for i in range(int(mobySection["length"] / 0x10)):
            tuid, offset, length = struct.unpack('>Q2I', assetlookup.read(0x10))
            res = {
                'tuid': tuid,
                'offset': offset,
                'length': length
            }
            print("o:{2} MOBY_RAW-REF {0}: {1}".format(hex(tuid), res, hex(assetlookup.offset)))
            self.mobys.append(res)


def read_ighw_header(stream: StreamHelper):
    header: IGHeader = IGHeader()
    header.magic1 = stream.readUInt(0x00)
    header.magic2 = stream.readUInt(0x04)
    header.chunks_count = stream.readUInt(0x08)
    header.length = stream.readUInt(0x0C)
    return header


def read_sections_chunks(headers: IGHeader, stream: StreamHelper):
    stream.seek(0x20)  # 0x20 is the constant offset for IGHW files
    for i in range(int(headers.length / 0x10)):
        sectionChunk: IGSectionChunk = IGSectionChunk()
        sectionChunk.id = stream.readUInt(0x00)
        sectionChunk.offset = stream.readUInt(0x04)
        sectionChunk.count = stream.readUInt(0x08)
        sectionChunk.length = stream.readUInt(0x0C)
        print("o:{2} IGHW_SectHeader {0}: {1}".format(hex(sectionChunk.id), sectionChunk.__dict__, hex(stream.offset)))
        stream.jump(0x10)
        yield sectionChunk


def query_section(chunks: list[IGSectionChunk], section_id: int):
    if section_id in SectionIDTypeEnum._value2member_map_:
        for section in chunks:
            if section.id == section_id:
                return section

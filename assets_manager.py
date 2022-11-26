import bpy
import bpy_extras
import io
import struct
import os
import os.path
import typing
import enum
from . import (file_manager, mobys, ties)
from .types import (SectionIDTypeEnum, MobyIDTypeEnum)


class AssetManager:
    def __init__(self, fm: file_manager.FileManager, operator):
        print("AssetManager: INIT")
        isOld = fm.isIE2
        self.fm: file_manager.FileManager = fm
        self.mobys: list[dict[str, int]] = list[dict[str, int]]()
        self.ties: list[dict[str, int]] = list[dict[str, int]]()
        if isOld is False:
            print("AssetManager: Is Not Old!")
            print(fm.igfiles)
            for idx, igfile in enumerate(fm.igfiles):
                stream = fm.igfiles[igfile]
                headers = IGHWHeaders(stream).result
                print("----\nIGFILE {0}: {1}".format(igfile, headers.__dict__))
                if igfile == "assetlookup.dat":
                    sections_chunks = IGHWSectionsChunks(headers, stream)
                    self.sections: IGHWSectionsChunks = sections_chunks
                    for section_chunk in sections_chunks.result:
                        print("IGCHNK {0}: {1}".format(hex(section_chunk["id"]), section_chunk))

            for idx, igfile in enumerate(fm.otherfiles):
                stream = fm.otherfiles[igfile]
                headers = IGHWHeaders(stream).result
                print("----\nAM-OTHER_IGFILE {0}: {1}".format(igfile, headers.__dict__))
                if igfile == "ties.dat" and operator.use_ties:
                    self.LoadTies()
                    ties_refs = self.ties
                    for tie_ref in ties_refs:
                        stream.seek(tie_ref['offset'])
                        print('----')
                        print("TIE {0}".format(tie_ref['tuid']))
                        subigfile_header: IGHeader = IGHeader()
                        magic1, magic2, count, length = struct.unpack('>4I', stream.read(0x10))

                        subigfile_header.magic1 = magic1
                        subigfile_header.magic2 = magic2
                        subigfile_header.chunks_count = count
                        subigfile_header.length = length

                        relative_offset = tie_ref['offset'] + 0x20
                        all_ties: list[ties.CTie] = list[ties.CTie]()
                        for i in range(subigfile_header.chunks_count):
                            print(hex(relative_offset))
                            all_ties.append(ties.CTie(relative_offset, stream))
                            relative_offset = relative_offset + 0x80

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
        assetlookup: io.BufferedReader = self.fm.igfiles["assetlookup.dat"]
        tieSection = self.sections.query_section(0x1D300)
        assetlookup.seek(tieSection["offset"])
        for i in range(tieSection["count"]):
            tuid, offset, length = struct.unpack('>Q2I', assetlookup.read(0x10))
            res = {
                'tuid': tuid,
                'offset': offset,
                'length': length
            }
            print("TIE_RAW-REF {0}: {1}".format(hex(tuid), res))

            self.ties.append(res)

    def LoadMobys(self):
        if self.fm.isIE2:
            print("MOBY_STREAM: Unsupported format!")
            # self.LoadOldMobys()
        else:
            self.LoadNewMobys()

    def LoadNewMobys(self):
        assetlookup: io.BufferedReader = self.fm.igfiles["assetlookup.dat"]
        mobySection = self.sections.query_section(0x1D600)
        print("MOBY_SECTION {0}: {1}".format(hex(mobySection["id"]), mobySection))
        assetlookup.seek(mobySection["offset"])

        for i in range(int(mobySection["length"] / 0x10)):
            tuid, offset, length = struct.unpack('>Q2I', assetlookup.read(0x10))
            res = {
                'tuid': tuid,
                'offset': offset,
                'length': length
            }
            print("MOBY_RAW-REF {0}: {1}".format(hex(tuid), res))
            self.mobys.append(res)


class IGHWHeaders:
    def __init__(self, stream: io.BufferedReader):
        stream.seek(0x00)
        magic1, magic2, count, length = struct.unpack('>4I', stream.read(0x10))
        self.result: IGHeader = IGHeader()
        self.result.magic1 = magic1
        self.result.magic2 = magic2
        self.result.chunks_count = count
        self.result.length = length


class IGHeader(dict):
    magic1: int
    magic2: int
    chunks_count: int
    length: int


class IGHWSectionsChunks:
    def __init__(self, headers: IGHeader, stream: io.BufferedReader):
        stream.seek(0x20)  # 0x20 is the constant offset for IGHW files
        self.result: list[dict] = list()
        for i in range(int(headers.length / 0x10)):
            cid, offset, count, length = struct.unpack('>4I', stream.read(0x10))
            self.result.append({
                "id": cid,
                "offset": offset,
                "count": count,
                "length": length
            })

    def query_section(self, section_id: int):
        if section_id in SectionIDTypeEnum._value2member_map_:
            for section in self.result:
                if section["id"] == section_id:
                    return section

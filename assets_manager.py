import bpy
import bpy_extras
import io
import struct
import os
import os.path
import typing
import enum
from . import file_manager

class AssetManager:
    def __init__(self, fm: file_manager.FileManager, operator):
        print("AssetManager: INIT")
        isOld = fm.isIE2
        self.fm = fm
        if isOld is False:
            print("AssetManager: Is Not Old!")
            for idx, igfile in enumerate(fm.igfiles):
                stream = fm.igfiles[igfile]
                headers = IGHWHeaders(stream).result
                print("----\nIGFILE {0}: {1}".format(igfile, headers))
                if igfile == "assetlookup.dat":
                    sections_chunks = IGHWSectionsChunks(headers, stream)
                    self.sections: IGHWSectionsChunks = sections_chunks
                    for section_chunk in sections_chunks.result:
                        print("IGCHNK {0}: {1}".format(hex(section_chunk["id"]), section_chunk))
            
            for idx, igfile in enumerate(fm.otherfiles):
                stream = fm.otherfiles[igfile]
                headers = IGHWHeaders(stream).result
                print("----\nIGFILE {0}: {1}".format(igfile, headers))
                if igfile == "mobys.dat" and operator.use_mobys == True:
                    self.LoadMobys()
                    mobys_refs = self.mobys
                    for moby_ref in mobys_refs:
                        print("MOBY {0}: {1}".format(moby_ref["tuid"], moby_ref))
                else:
                    print("IGFILE_CODE0: Mobys reading aborted: mobys.dat doesn't exist or 'Import Mobys' have been unchecked.")
        else:
            print("AssetManager: Is Old! Aborting...")
    def LoadMobys(self):
        if self.fm.isIE2:
            print("MOBY_STREAM: Unsupported format!")
            #self.LoadOldMobys()
        else:
            self.LoadNewMobys()
    
    def LoadNewMobys(self):
        assetlookup: io.BufferedReader = self.fm.igfiles["assetlookup.dat"]
        mobySection = self.sections.query_section(0x1D600)
        print(mobySection)
        assetlookup.seek(mobySection["offset"])
        mobyStream: io.BufferedReader = self.fm.otherfiles["mobys.dat"]
        tuid1, tuid2, offset, length = struct.unpack('>4I', assetlookup.read(0x10))
        tuid = int(str(int(str(tuid1), 16)) + str(int(str(tuid2), 16)).replace('0x', ''))

        print("FIRST-MOBYRAW {0}: ('tuid':{1}, 'offset': {2}, 'length': {3})".format(hex(tuid), tuid, offset, length))
        self.mobys: list = list()
        self.mobys.append({
            'tuid': tuid,
            'offset': offset,
            'length': length,
        })



class IGHWHeaders:
    def __init__(self, stream: io.BufferedReader):
        stream.seek(0x00)
        magic1, magic2, count, length = struct.unpack('>4I', stream.read(0x10))
        self.result = {
            "magic1": magic1,
            "magic2": magic2,
            "chunks_count": count,
            "length": length
        }

class IGHWSectionsChunks:
    def __init__(self, headers: dict, stream: io.BufferedReader):
        stream.seek(0x20) # 0x20 is the constant offset for IGHW files
        self.result: list(dict) = list()
        for i in range(headers["chunks_count"]):
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




class Moby:
    def __init__(self, mobystream: io.BufferedReader, tuid: int, offset: int, length: int):
        mobystream.seek(offset)
        self.result = list()
        for i in range(headers["chunks_count"]):
            cid, offset, count, length = struct.unpack('>I', mobystream.read(0x10))
            self.result.append({
                "id": cid,
                "offset": offset,
                "count": count,
                "length": length
            })

class MobyIDTypeEnum(enum.Enum):
    MOBY = 0xD100
    MOBY_MODELS = 0xD700
    MOBY_MESHES = 0xDD00
    MOBY_VERTICES = 0xE200
    MOBY_INDICES = 0xE100
class SectionIDTypeEnum(enum.Enum):
    MOBYS = 0x1D600
    TIES = 0x1D300
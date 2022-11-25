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
    def __init__(self, fm: file_manager.FileManager):
        print("AssetManager: INIT")
        isOld = fm.isIE2
        if isOld is False:
            print("AssetManager: Is Not Old!")
            for idx, igfile in enumerate(fm.igfiles):
                stream = fm.igfiles[igfile]
                headers = IGHWHeaders(stream).result
                print("----\nIGFILE {0}: {1}".format(igfile, headers))
                if igfile == "assetlookup.dat":
                    sections_chunks = IGHWSectionsChunks(headers, stream).result
                    for section_chunk in sections_chunks:
                        print("IGCHNK {0}: {1}".format(hex(section_chunk["id"]), section_chunk))
            
            for idx, igfile in enumerate(fm.otherfiles):
                stream = fm.otherfiles[igfile]
                headers = IGHWHeaders(stream).result
                print("----\nIGFILE {0}: {1}".format(igfile, headers))
                if igfile == "mobys.dat":
                    mobys_refs = Mobys(headers, stream).result
                    for moby_ref in mobys_refs:
                        if moby_ref["id"] in MobyIDTypeEnum._value2member_map_:
                            print("{0} {1}: {2}".format(MobyIDTypeEnum(moby_ref["id"]).name, moby_ref["id"], moby_ref))
                        else:
                            print("UMOBY {0}: {1}".format(moby_ref["id"], moby_ref))
        else:
            print("AssetManager: Is Old! Aborting...")

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
        self.result = list()
        for i in range(headers["chunks_count"]):
            cid, offset, count, length = struct.unpack('>4I', stream.read(0x10))
            self.result.append({
                "id": cid,
                "offset": offset,
                "count": count,
                "length": length
            })



class Mobys:
    def __init__(self, headers: dict, stream: io.BufferedReader):
        stream.seek(0x20)
        self.result = list()
        for i in range(headers["chunks_count"]):
            cid, offset, count, length = struct.unpack('>4I', stream.read(0x10))
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
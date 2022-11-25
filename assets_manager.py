import bpy
import bpy_extras
import io
import struct
import os
import os.path
import typing
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
                print("IGFILE {0}: {1}".format(igfile, headers))
                if igfile == "assetlookup.dat":
                    sections_chunks = IGHWSectionsChunks(headers, stream).result
                    for section_chunk in sections_chunks:
                        print("IGCHNK {0}: {1}".format(hex(section_chunk["id"]), section_chunk))
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



#class Moby:
#    def __init__(stream: io.BufferedReader):

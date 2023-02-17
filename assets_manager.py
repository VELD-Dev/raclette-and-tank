from . import zones
from . import ties
from . import textures
from . import file_manager
from .stream_helper import (StreamHelper)
from .types import (IGAssetRef, IGSectionChunk)
from .utils import (read_sections_chunks, read_ighw_header, query_section)


class AssetManager:
    def __init__(self, fm: file_manager.FileManager, operator):
        self.textures_ref: list[IGAssetRef] = list[IGAssetRef]()
        print("AssetManager: INIT")
        isOld = fm.isIE2
        self.fm: file_manager.FileManager = fm
        self.mobys_refs: list[IGAssetRef] = list[IGAssetRef]()
        self.ties_refs: list[IGAssetRef] = list[IGAssetRef]()
        self.zones_refs: list[IGAssetRef] = list[IGAssetRef]()
        self.ties_instances: list[zones.CTieInstance] = list[zones.CTieInstance]()
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
                    self.ties = dict()
                    for tie_ref in self.ties_refs:
                        # print("----")
                        tie = ties.TieRefReader(stream, tie_ref)
                        self.ties[tie.tie.tie.tuid] = tie
                elif igfile == "zones.dat" and operator.use_zones:
                    self.LoadZones()
                    self.zones = list[zones.ZoneReader]()
                    for zone_ref in self.zones_refs:
                        print("----")
                        print(zone_ref.__dict__)
                        zone = zones.ZoneReader(stream, zone_ref)
                        if zone.ties_instances is not None:
                            self.zones.append(zone)
                #elif igfile == "highmips.dat" and operator.use_textures:
                #    self.LoadTextures()
                #    self.textures = list[textures.TextureReader]()
                #    for texture_ref in self.textures_ref:
                #        print("----")
                #        print(texture_ref.__dict__)
                #        texture = textures.TextureReader(stream, texture_ref)

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

    ##############
    #### TIES ####
    ##############
    def LoadTies(self):
        if self.fm.isIE2:
            print("TIE_STREAM: Unsupported format !")
        else:
            self.LoadNewTies()

    def LoadNewTies(self):
        assetlookup: StreamHelper = self.fm.igfiles["assetlookup.dat"]
        tieSection = query_section(self.sections, 0x1D300)
        assetlookup.seek(tieSection.offset)
        self.ties_refs = list[IGAssetRef]()
        for i in range(int(tieSection.length / 0x10)):
            asset_ref = IGAssetRef()
            asset_ref.tuid = assetlookup.readULong(0x00)
            asset_ref.offset = assetlookup.readUInt(0x08)
            asset_ref.length = assetlookup.readUInt(0x0C)
            assetlookup.jump(0x10)
            self.ties_refs.append(asset_ref)

    ##################
    #### TEXTURES ####
    ##################
    def LoadTextures(self):
        if self.fm.isIE2:
            print("UNSUPPORTED GAME VERSION")
            return
        else:
            self.LoadTexturesNew()

    def LoadTexturesNew(self):
        assetlookup: StreamHelper = self.fm.igfiles["assetlookup.dat"]
        highresTexturesSection = query_section(self.sections, 0x1D1C0)
        assetlookup.seek(highresTexturesSection.offset)
        self.textures_ref = list[IGAssetRef]()
        for i in range(int(highresTexturesSection.length / 0x10)):
            asset_ref = IGAssetRef()
            asset_ref.tuid = assetlookup.readULong(0x00)
            asset_ref.offset = assetlookup.readUInt(0x08)
            asset_ref.length = assetlookup.readUInt(0x0C)
            assetlookup.jump(0x10)
            self.textures_ref.append(asset_ref)


    ###############
    #### ZONES ####
    ###############
    def LoadZones(self):
        if self.fm.isIE2:
            print("UNSUPPORTED GAME VERSION")
            return
            # self.LoadOldZones()
            # TISection = query_section(zones_chunks, 0x9240)
            # if "debug.dat" in self.fm.igfiles:
        else:
            self.LoadZonesNew()

    def LoadZonesNew(self):
        assetlookup: StreamHelper = self.fm.igfiles["assetlookup.dat"]
        zonesSection = query_section(self.sections, 0x1DA00)
        assetlookup.seek(zonesSection.offset)
        self.zones_refs = list[IGAssetRef]()
        for i in range(zonesSection.length // 0x10):
            asset_ref = IGAssetRef()
            asset_ref.tuid = assetlookup.readULong(0x00)
            asset_ref.offset = assetlookup.readUInt(0x08)
            asset_ref.length = assetlookup.readUInt(0x0C)
            print(f"o:{hex(assetlookup.offset)} ZONE_RAW-REF {hex(asset_ref.tuid)}: {asset_ref.__dict__}")
            assetlookup.jump(0x10)
            self.zones_refs.append(asset_ref)

    ###############
    #### MOBYS ####
    ###############
    def LoadMobys(self):
        if self.fm.isIE2:
            print("MOBY_STREAM: Unsupported format!")
            # self.LoadOldMobys()
        else:
            self.LoadNewMobys()

    def LoadNewMobys(self):
        assetlookup: StreamHelper = self.fm.igfiles["assetlookup.dat"]
        mobySection = query_section(self.sections, 0x1D600)
        print("o:{2} / MOBY_SECTION {0}: {1}".format(hex(mobySection.id), mobySection, hex(assetlookup.offset)))
        assetlookup.seek(mobySection.offset)

        for i in range(int(mobySection["length"] / 0x10)):
            res: IGAssetRef = IGAssetRef()
            res.tuid = assetlookup.readULong(0x00)
            res.offset = assetlookup.readUInt(0x08)
            res.length = assetlookup.readUInt(0x0C)
            assetlookup.jump(0x10)
            print("o:{2} MOBY_RAW-REF {0}: {1}".format(hex(res.tuid), res.__dict__, hex(assetlookup.offset)))
            self.mobys.append(res)

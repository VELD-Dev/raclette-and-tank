import enum


class MobyIDTypeEnum(enum.Enum):
    MOBY = 0xD100
    MOBY_MODELS = 0xD700
    MOBY_MESHES = 0xDD00
    MOBY_VERTICES = 0xE200
    MOBY_INDICES = 0xE100


class SectionIDTypeEnum(enum.Enum):
    MOBYS = 0x1D600
    TIES = 0x1D300
    ZONES = 0x1DA00


class TieSectionIDTypeEnum(enum.Enum):
    TIE = 0x3400
    VERTICES = 0x3000
    INDICES = 0x3200


class ZoneSectionIDTypeEnum(enum.Enum):
    TIES_INSTANCES_REFS_OLD = 0x9240
    TIES_INSTANCES_REFS_NEW = 0x72C0
    TIES_INSTANCES_TUIDS = 0x7200


class LevelNamesEnum(enum.Enum):
    level_transitions = "Level Transitions"
    npc_island = "QFB - Merdegraw: Hoolefar Island"
    prologue = "QFB - Merdegraw: Azorean Sea"
    viper_caverns = "QFB - Merdegraw: Morrow Caverns"
    treasure_island = "QFB - Merdegraw: Darkwater Cove"
    apogeeµspaceµstation = "TOD - Nundac Belt: Apogee Space Station"
    cobalia = "TOD - Cobalia: Spaceport"
    cragmiteµruins = "TOD - Reepor: Cragmite Ruins"
    fastoon = "TOD - Fastoon: Lombax Ruins"
    fastoon_return = "TOD - Fastoon: Lombax Ruins (return)"
    imperialµfightµfest = "TOD - Mukow: Imperial Fight Festival"
    iris = "TOD - Kreeli Comet: I.R.I.S. Supercalculator"
    kerchuµcity = "TOD - Jasindu: Kerchu Fort"
    meridianµcity = "TOD - Igliak: Meridian City"
    metropolis = "TOD - Kerwan: Metropolis"
    pirateµbase = "TOD - Ardolis: Pirate Base"
    rykanµv = "TOD - Rykan V: Spaceport"
    sargasso = "TOD - Sargasso: Kerchu Complex, Outpost L-51"
    slags_fleet = "TOD - Ublik Passage: Slag's Fleet"
    spaceµcombatµi = "TOD - Voron Asteroid Belt"
    spaceµcombatµii = "TOD - Rakar Star Cluster"
    spaceµcombatµiii = "TOD - Verdigris Black Hole"
    stratusµcity = "TOD - Kortog: Stratus City"
    viceron = "TOD - Viceron: Zordoom Prison"
    agorian_arena = "ACIT - Agorian Arena"
    axiom_city = "ACIT - Terachnos: Axiom City"
    front_end = "Front End (?)"
    galacton_ship = "ACIT - Vorselon's Warship"
    gimlick_valley = "ACIT - Morklon: Gimlick Valley"
    great_clock_a = "ACIT - The Great Clock: Sector 1"
    great_clock_b = "ACIT - The Great Clock: Sector 2"
    great_clock_c = "ACIT - The Great Clock: Sector 3"
    great_clock_d = "ACIT - The Great Clock: Sector 4"
    great_clock_e = "ACIT - The Great Clock: Orvus Chamber"
    insomniac_museum = "ACIT - Insomniac Museum"
    krell_canyon = "ACIT - Lumos: Krell Canyon"
    molonoth = "ACIT - Torren IV: Molonoth Fields"
    nefarious_station = "ACIT - Nefarious Space Station"
    space_sector_1 = "ACIT - SS1"
    space_sector_2 = "ACIT - SS2"
    space_sector_3 = "ACIT - SS3"
    space_sector_4 = "ACIT - SS4"
    space_sector_5 = "ACIT - Bregus Sector"
    tombli = "ACIT - Zanifar: Tombli Outpost"
    valkyrie_fleet = "ACIT - Vapedia: Valkyrie Citadel"
    zolar_forest = "ACIT - Quantos: Zolar Forest"
    # ADD FFA MAPS
    # ADD A4O MAPS
    # ADD ITN MAPS
    # ADD RESISTANCE 2 MAPS
    # ADD RESISTANCE 3 MAPS


class IGHeader(dict):
    magic1: int
    magic2: int
    chunks_count: int
    length: int


class IGSectionChunk(dict):
    id: int
    offset: int
    count: int
    length: int


class IGAssetRef(dict):
    tuid: int
    offset: int
    length: int


class MeshVertex(dict):
    location: tuple[int, int, int] | tuple[float, float, float]
    multiplier: int
    UVs: tuple[float, float]
    normals: tuple[float, float, float]

    def __loctuple__(self):
        return self.location

    def __uvstuple__(self):
        return self.UVs

    def __nortuple__(self):
        return self.normals


class Tie(dict):
    """0x80 bytes long"""
    meshes_offset: int
    # meshes_count: int
    metadata_count: int
    vertex_buffer_start: int
    vertex_buffer_size: int
    scale: tuple[float, float, float]
    name: str
    tuid: int


class TieMesh(dict):
    """0x40 bytes long"""
    indexIndex: int
    vertexIndex: int
    vertexCount: int
    indexCount: int
    oldShaderIndex: int
    newShaderIndex: int
    vertices: list[MeshVertex]

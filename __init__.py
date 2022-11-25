# MIT License
# 
# Copyright (c) 2022 VELD-Dev
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

bl_info = {
    "name" : "raclette-and-tank-importer",
    "author" : "VELD-Dev",
    "description" : (
        "Raclette & Tank importer is an asset extractor and importer for Blender. "
        "R&T Importer was made for animators, fangame developers and all those fan stuff. "
        "R&T Importer IS NOT made for level editing ! Use Lunacy Level Editor instead."),
    "blender" : (3, 2, 0),
    "version" : (0, 0, 1),
    "location" : "File > Import > Extract & Import RAC Assets",
    "warning" : "Work in progress, be careful, the mod may crash Blender, always backup your files !",
    "doc_url": "https://github.com/VELD-Dev/raclette-and-tank",
    "category" : "Reverse-Engineering"
}

from . import auto_load

auto_load.init()


import bpy
import bpy_extras
import os
import os.path
import io
import struct
import enum

if 'bpy' in locals():
    import importlib
    importlib.reload(file_manager)
    importlib.reload(assets_manager)
else:
    from . import file_manager
    from . import assets_manager



###############################################
################# CONSTANTS ###################
###############################################

IG_SECTION_ID_MOBY = 0x1D100
IG_CHUNK_ID_MOBY = 0xD100
IG_CHUNK_ID_MOBY_MODELS = 0xD700
IG_CHUNK_ID_MOBY_MESHES = 0xDD00
IG_CHUNK_ID_MOBY_VERTICES = 0xE200
IG_CHUNK_ID_MOBY_INDICES = 0xE100

##############################################
########## GLOBAL FUNCTIONS LIBRARY ##########
##############################################

def extract_and_import(operator, context):
    dirname = operator.directory
    print(dirname)
    filemanager = file_manager.FileManager(dirname)
    assets_manager.AssetManager(filemanager, operator)

'''
def extract_and_import(operator, context):
    dirname = operator.directory
    print(dirname)
    dir_content = os.listdir(dirname)
    print(dir_content)

    offset = list[int]()
    count = list[int]()
    oid = list[int]()
    length = list[int]()

    filesonly = [file for file in dir_content if os.path.isfile(os.path.join(dirname, file))]

    for file in filesonly:
        filepath = os.path.join(dirname, file)
        base_stream = open(filepath, 'rb')
        print("\n----\n" + file)
        headers = read_file_header(base_stream)
        print(headers)
        if int(headers["magic1"]) == 0x49474857:

            # DOES NOT SUPPORT ToD & QFB GAMES *YET*
            if file == "main.dat":
                continue
            
            # DOES SUPPORT POST-R2 GAMES
            if file == "assetlookup.dat":
                stream = read_chunks_headers(base_stream, headers['chunks_count'])
                for idx, (h, soid, scount, soffset, slength) in enumerate(stream):
                    print("{0} {1}".format(hex(soid), soid))
                    if soid != IG_CHUNK_ID_MOBY or soid != IG_CHUNK_ID_MOBY_MODELS or soid != IG_CHUNK_ID_MOBY_MESHES or soid != IG_CHUNK_ID_MOBY_INDICES or soid != IG_CHUNK_ID_MOBY_VERTICES:
                        continue
                    print("{6} {0}: ({7}) {1} / (oid:{2}, offset:{3}, count:{4}, length:{5})".format(idx, h, hex(soid), hex(soffset), hex(scount), hex(slength), file, hex(soid)))
                    oid.append(int(soid))
                    count.append(int(scount))
                    offset.append(int(soffset))
                    length.append(int(slength))
'''
##############################################
########### HEXA FUNCTIONS LIBRARY ###########
##############################################

def read_file_header(stream):
    stream.seek(0)
    magic1, magic2, chunks_count, header_length = struct.unpack(">4I", stream.read(0x10))
    return {
        "magic1": magic1,
        "magic2": magic2,
        "chunks_count": chunks_count,
        "header_length": header_length,
    }

def read_chunks_headers(stream, count: int):
    stream.seek(0x20) # 0x20 is the base offset of all the IGHW files for chunks headers
    for i in range(count):
        buff = stream.read(0x10)
        if buff.__len__() < 0x10:
            return
        oid, offset, count, length = struct.unpack(">4I", buff)
        yield ({
            "oid": oid,
            "offset": offset,
            "count": count,
            "length": length
        }, oid, offset, count, length)

##############################################
########## EXTRACT AND IMPORT CLASS ##########
##############################################

class ExtractAndImport(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Extracts and imports assets from a Ratchet & Clank level. Level have to be uncompressed."""
    bl_idname="import_scene.eai"
    bl_label="Select this folder"
    bl_description="Extracts and imports assets from a Ratchet & Clank level. Level have to be uncompressed."
    bl_options={"REGISTER"}

    filename_ext = ".dat"
    #filter_glob: bpy.props.StringProperty(
    #    default="*main.dat;*assetlookup.dat;*debug.dat",
    #    options={"HIDDEN"}
    #)

    #directory: bpy.props.StringProperty(
    #    name="Level Folder",
    #    description="Path to the uncompressed level folder. There should be .dat files inside.",
    #    subtype="DIR_PATH"
    #)
    directory: bpy.props.StringProperty()
    filter_glob: bpy.props.StringProperty(
        default="*.dat",
        options={'HIDDEN'},
        maxlen=255
    )
    use_mobys: bpy.props.BoolProperty(
        name="Import Mobys",
        description="Wether mobys should be imported or not. Pretty useful to have a clean map.",
        default=True
    )
    use_shrubs: bpy.props.BoolProperty(
        name="Import Shrubs",
        description="Wether shrubs should be imported or not. If it is enabled, the map can be heavy.",
        default=True
    )
    
    def draw(self, context):
        pass

    def execute(self, context):
        extract_and_import(self, context)
        return {"FINISHED"}

class EAI_PT_import_include(bpy.types.Panel):
    bl_space_type="FILE_BROWSER"
    bl_region_type="TOOL_PROPS"
    bl_label="Include"
    bl_parent_id="FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_eai"

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'use_mobys')
        layout.prop(operator, 'use_shrubs')

class EAI_PT_import_settings(bpy.types.Panel):
    bl_space_type="FILE_BROWSER"
    bl_region_type="TOOL_PROPS"
    bl_label="Settings"
    bl_parent_id="FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_eai"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split=True
        layout.use_property_decorate=False

        sfile=context.space_data
        operator=sfile.active_operator

########################################
########## END OF THE CLASSES ##########
########################################



def menu_func_import(self, context):
    self.layout.operator(ExtractAndImport.bl_idname, text="Extract & Import RAC Level (level folder)")

classes = [
    ExtractAndImport,
    EAI_PT_import_include,
    EAI_PT_import_settings,
]

def register():
    auto_load.register()
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    auto_load.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

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
import os.path
import random
import typing

import bpy
import bpy_extras
import bmesh
import mathutils

bl_info = {
    "name": "raclette-and-tank-importer",
    "author": "VELD-Dev",
    "description": (
        "Raclette & Tank importer is an asset extractor and importer for Blender. "
        "R&T Importer was made for animators, fangame developers and all those fan stuff. "
        "R&T Importer IS NOT made for level editing ! Use Lunacy Level Editor instead."),
    "blender": (3, 3, 0),
    "version": (1, 0, 0),
    "location": "File > Import > Extract & Import RAC Assets",
    "warning": "Work in progress, be careful, the mod may crash Blender, always backup your files !",
    "doc_url": "https://github.com/VELD-Dev/raclette-and-tank",
    "category": "Reverse-Engineering"
}

from . import auto_load

auto_load.init()

if 'bpy' in locals():
    import importlib

    importlib.reload(file_manager)
    importlib.reload(assets_manager)
    importlib.reload(mobys)
    importlib.reload(types)
    importlib.reload(ties)
    importlib.reload(zones)
else:
    from . import file_manager
    from . import assets_manager
    from . import types
    from .zones import (CTieInstance, TieInstance, ZoneReader)

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
    assetmanager = assets_manager.AssetManager(filemanager, operator)

    # Level name is completely decorative. It is completely useless.
    level_name = os.path.basename(os.path.dirname(dirname))
    encodedlvlname = level_name.replace(' ', '??', -1)
    print("Checking levelname {0}...".format(level_name))
    lvl_collection: typing.Any
    lvl_collection_pname: str
    final_lvlname: str
    if encodedlvlname in types.LevelNamesEnum.__dict__:
        print("Levelname exists in ENUM !")
        final_lvlname = types.LevelNamesEnum[encodedlvlname].value
    else:
        final_lvlname = level_name.replace(' ', '_', -1)

    if final_lvlname not in bpy.data.collections:
        print("Linking new collection to scene...")
        lvl_collection = bpy.data.collections.new(final_lvlname)
        lvl_collection_pname = final_lvlname
        bpy.context.scene.collection.children.link(lvl_collection)
    else:
        lvl_collection = bpy.data.collections[final_lvlname]
        lvl_collection_pname = final_lvlname

    # If ties are enabled, add ties.
    if operator.use_ties:
        ties_collection_name = f"Ties {level_name}"
        ties_collection = object()
        if operator.put_in_collections:
            if ties_collection_name in bpy.data.collections:
                ties_collection = bpy.data.collections[ties_collection_name]
            else:
                ties_collection = bpy.data.collections.new(ties_collection_name)
                lvl_collection.children.link(ties_collection)
        else:
            ties_collection = bpy.data.collections[lvl_collection_pname]

        zones = {}
        for zone in assetmanager.zones:
            print(zone)
            zones[zone.zone_tuid] = zone
            print(f"Zone {zone.zone_tuid} Class Inst: {zone} - Ties: {zone.ties_instances}")
        for zone in zones.values():
            for tie_inst in zone.ties_instances:
                if operator.parent_meshes_to_objects:
                    ties = assetmanager.ties
                    tie = ties[tie_inst.tuid]

                    #objname = str()
                    #if tie.tie.tie.name is not None:
                    #    objname = tie.tie.tie.name
                    #else:
                    objname = f"Tie_{str(tie.tie.tie.tuid)[:6]}"

                    verts = list[tuple[float, float, float]]()
                    faces = list[tuple[int, int, int]]()
                    edges = []  # Ignore
                    uvs = []  # Ignore for now

                    max_index = 0
                    for i in range(len(tie.tie.tie_meshes)):
                        for k in range(tie.tie.tie_meshes[i].indexCount // 3):
                            faces.append((
                                tie.indices[i][k][0] + max_index,
                                tie.indices[i][k][1] + max_index,
                                tie.indices[i][k][2] + max_index
                            ))
                            k += 3
                        max_index += tie.tie.tie_meshes[i].vertexCount
                    for vertices in tie.vertices:
                        for vertex in vertices:
                            verts.append(vertex.__loctuple__())
                            uvs.append(vertex.__uvstuple__())
                    meshdata = bpy.data.meshes.new(f"TieData_{tie_inst.tuid}.{tie_inst.tieIndex}")
                    tie_inst_matrix = tie_inst.transformation
                    meshdata.from_pydata(verts, edges, faces)
                    meshdata.transform(tie_inst_matrix)
                    obj = bpy.data.objects.new(name=objname, object_data=meshdata)
                    ties_collection.objects.link(obj)

        # if not operator.parent_meshes_to_objects:
        #     for tie in assetmanager.ties.values():
        #         parent_obj = bpy.data.objects.new(name="Tie_{0}".format(str(tie.tie.tie.tuid)[:6]), object_data=None)
        #         ties_collection.objects.link(parent_obj)
        #         for idx, vertex in enumerate(tie.vertices):
        #             meshdataname = "TieData_{0}_{1}".format(str(tie.tie.tie.tuid)[:6], idx)
        #             verts = list[tuple[float, float, float]]()
        #             faces = tie.indices[idx]
        #             uvs = []
        #             edges = []  # Ignore
        #             for mesh_vertex in vertex:
        #                 verts.append(mesh_vertex.__loctuple__())
        #                 uvs.append(mesh_vertex.__uvstuple__())
        #             meshdata = bpy.data.meshes.new(meshdataname)
        #             tie_instance_matrix: mathutils.Matrix = [zone.gettietransform(tie.tie.tie.tuid)
        #                                                      for zone in list(zones.values())
        #                                                      if zone.gettietransform(tie.tie.tie.tuid)][0]
        #             meshdata.from_pydata(verts, edges, faces)
        #             meshdata.transform(tie_instance_matrix)
        #             obj = bpy.data.objects.new(name="Tie_{0}_{1}".format(str(tie.tie.tie.tuid)[:6], idx),
        #                                        object_data=bpy.data.meshes[meshdataname])
        #             ties_collection.objects.link(obj)
        #             obj.parent = parent_obj

        # bm = bmesh.from_edit_mesh(meshdata)
        # uv = bm.loops.layers.uv.new()
        # bpy.ops.object.mode_set(mode="edit")
        # for face in bm.faces:
        #    for loop in face.loops:
        #        loop[uv].iv = uvs[loop.vert.index]


##############################################
########## EXTRACT AND IMPORT CLASS ##########
##############################################

class ExtractAndImport(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Extracts and imports assets from a Ratchet & Clank level. Level have to be uncompressed."""
    bl_idname = "import_scene.eai"
    bl_label = "Select this folder"
    bl_description = "Extracts and imports assets from a Ratchet & Clank level. Level have to be uncompressed."
    bl_options = {"REGISTER"}

    filename_ext = ".dat"
    directory: bpy.props.StringProperty()
    filter_glob: bpy.props.StringProperty(
        default="*.dat",
        options={'HIDDEN'},
        maxlen=255
    )
    use_mobys: bpy.props.BoolProperty(
        name="Import Mobys",
        description="Wether mobys should be imported or not. Pretty useful to have a clean map.",
        default=False
    )
    use_shrubs: bpy.props.BoolProperty(
        name="Import Shrubs",
        description="Wether shrubs should be imported or not. If it is enabled, the map can be heavy.",
        default=True
    )
    use_ties: bpy.props.BoolProperty(
        name="Import Ties",
        description="Wether the base terrain should be imported or not. If unsure, do not uncheck.",
        default=True
    )
    use_ufrags: bpy.props.BoolProperty(
        name="Import UFrags",
        description="Wether UFrags should be imported or not. UFrags are globally all the tesselated terrain. If unsure, do not change.",
        default=True
    )

    put_in_collections: bpy.props.BoolProperty(
        name="Create Collections",
        description="Wether a creation should be created for each mesh type (Mobys, Ties, Shrubs, UFrags) or everything should be put at root.",
        default=True
    )
    use_textures: bpy.props.BoolProperty(
        name="Textures",
        description="Wether textures should be extracted, imported and applied or not.",
        default=True
    )
    use_lightning: bpy.props.BoolProperty(
        name="Lightning",
        description="Wether light points should be extracted and imported or not.",
        default=False
    )
    use_zones: bpy.props.BoolProperty(
        name="Zones",
        description="Wether every mesh supported by zones should be put into its zone. Creating subfolders in Collection.",
        default=True
    )
    parent_meshes_to_objects: bpy.props.BoolProperty(
        name="Parent meshes to objects",
        description="Disable it only if you know what you're doing! / Wether meshes of an object (tie, moby) should be parented/merged into one Blender object or not.",
        default=True
    )

    def draw(self, context):
        pass

    def execute(self, context):
        extract_and_import(self, context)
        return {"FINISHED"}


class EAI_PT_import_include(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "Include"
    bl_parent_id = "FILE_PT_operator"

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
        layout.prop(operator, 'use_ties')
        layout.prop(operator, 'use_ufrags')


class EAI_PT_import_settings(bpy.types.Panel):
    bl_space_type = "FILE_BROWSER"
    bl_region_type = "TOOL_PROPS"
    bl_label = "Settings"
    bl_parent_id = "FILE_PT_operator"

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

        layout.prop(operator, 'use_textures')
        layout.prop(operator, 'use_lightning')
        layout.prop(operator, 'use_zones')
        layout.prop(operator, 'put_in_collections')
        layout.prop(operator, 'parent_meshes_to_objects')


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

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
import typing

import bpy
import bpy_extras

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
    importlib.reload(stream_helper)
    importlib.reload(bmesh_manager)
else:
    import file_manager
    import assets_manager
    import types
    import bmesh_manager
    import utils

###############################################
################# CONSTANTS ################### (These are here just for documentation purposes)
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

    level_name = os.path.basename(os.path.dirname(dirname))
    clean_lvlname = utils.find_cleanlvlname(level_name)
    if clean_lvlname not in bpy.data.collections:
        lvl_collection = bpy.data.collections.new(clean_lvlname)
        bpy.context.scene.collection.children.link(lvl_collection)
    else:
        lvl_collection = bpy.data.collections[clean_lvlname]

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
            ties_collection = bpy.data.collections[clean_lvlname]

        # Putting every existing tie meshes into a dictionnary
        ties = dict[typing.Any, list[object] | object]()
        for tie in assetmanager.ties.values():
            submeshes = []
            for i in range(len(tie.tie.tie_meshes)):
                mesh = bpy.data.meshes.new(f"TieData_{tie.tie.tie.tuid}.{i}")
                verts = list[tuple[float, float, float]]()
                faces = list[tuple[int, int, int]]()
                normals = list[tuple[float, float, float]]()
                uvs = list[tuple[float, float]]()
                for k in range(tie.tie.tie_meshes[i].indexCount // 3):
                    faces.append((
                        tie.indices[i][k][0],
                        tie.indices[i][k][1],
                        tie.indices[i][k][2]
                    ))
                for vertex in tie.vertices[i]:
                    verts.append(vertex.__loctuple__())
                    uvs.append(vertex.__uvstuple__())
                    normals.append(vertex.__nortuple__())
                mesh.from_pydata(verts, [], faces)
                mesh = bmesh_manager.mapUVs(mesh, uvs)
                mesh = bmesh_manager.mapNormals(mesh, normals)
                mesh.update()
                submeshes.append(mesh)
            ties[tie.tie.tie.tuid] = submeshes

        # If parent meshes to object, then will pack all the ties submeshes into ties meshes.
        if operator.parent_meshes_to_objects:
            for i in ties.keys():
                tie = ties[i]
                finalmesh = bmesh_manager.packMeshes(tie)
                finalmesh.update()
                ties[i] = finalmesh

        zones = {}
        for zone in assetmanager.zones:
            print(zone)
            zones[zone.zone_tuid] = zone
            print(f"Zone {zone.zone_tuid} Class Inst: {zone.__dict__} - Ties: {len(zone.ties_instances)}")
        for zone in zones.values():
            for tie_inst in zone.ties_instances:
                ties_data = assetmanager.ties
                tie_data = ties_data[tie_inst.tuid]
                tie = ties[tie_inst.tuid]
                meshes = []

                objname = str()
                if tie_data.tie.tie.name != "" or tie_data.tie.tie.name is not None:
                    objname = tie_data.tie.tie.name
                else:
                    objname = f"Tie_{str(tie_data.tie.tie.tuid)}"

                if operator.parent_meshes_to_objects:
                    meshes.append(bmesh_manager.clone(tie))
                else:
                    [meshes.append(bmesh_manager.clone(submesh)) for submesh in tie]

                for mesh in meshes:
                    mesh.transform(tie_inst.transformation)
                    obj = bpy.data.objects.new(name=objname, object_data=mesh)
                    ties_collection.objects.link(obj)
                    bmesh_manager.center_origin_to_geometry(obj)


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

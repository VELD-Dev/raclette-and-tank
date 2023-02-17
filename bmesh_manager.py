import bmesh
import bpy
import mathutils


def mapUVs(mesh, uvs):
    bm = bmesh.new()
    bm.from_mesh(mesh)

    uv = bm.loops.layers.uv.new()
    for face in bm.faces:
        for loop in face.loops:
            loop[uv].uv = uvs[loop.vert.index]
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def mapNormals(mesh, normals):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    verts = bm.verts
    for i in range(len(verts)):
        normal = normals[i]
        verts[i].normal = normal

    bm.to_mesh(mesh)
    return mesh


def packMeshes(meshes: list[object], final_meshname: str = "MeshData"):
    mesh = bpy.data.meshes.new(final_meshname)
    bm = bmesh.new()
    for m in meshes:
        bm.from_mesh(m)
        bm.to_mesh(mesh)
    bm.free()
    return mesh


def clone(mesh):
    mesh_clone = bpy.data.meshes.new(name=mesh.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.to_mesh(mesh_clone)
    bm.free()
    return mesh_clone


def center_origin_to_geometry(obj):
    # Obtient la référence au mesh de l'objet
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    # Calcule le centre de masse du mesh
    center_of_mass = mathutils.Vector()
    for v in bm.verts:
        center_of_mass += v.co
    center_of_mass /= len(bm.verts)
    # Calcule le vecteur de translation pour déplacer les sommets du mesh
    translate_vec = -center_of_mass
    # Déplace les sommets du mesh avec le vecteur de translation
    bmesh.ops.translate(bm, vec=translate_vec, verts=bm.verts)
    # Déplace l'origine de l'objet vers le centre de masse du mesh
    obj.location += center_of_mass
    # Met à jour le mesh à partir du BMesh
    bm.to_mesh(mesh)
    bm.free()

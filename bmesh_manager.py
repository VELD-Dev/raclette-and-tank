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


def set_normals(mesh, normals):
    bm = bmesh.new()
    bm.from_mesh(mesh)

    for i, poly in enumerate(bm.faces):
        poly.normal_update()
        poly.normal = normals[i]

    bm.to_mesh(mesh)
    bm.free()
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
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    center_of_mass = mathutils.Vector()
    for v in bm.verts:
        center_of_mass += v.co
    center_of_mass /= len(bm.verts)
    translate_vec = -center_of_mass
    bmesh.ops.translate(bm, vec=translate_vec, verts=bm.verts)
    obj.location += center_of_mass
    bm.to_mesh(mesh)
    bm.free()

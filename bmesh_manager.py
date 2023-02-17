import bmesh
import bpy
from mathutils import Vector


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


def center_origin_to_center_of_mass(obj):
    # get the mesh data from the object
    mesh = obj.data
    # create a bmesh from the mesh data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # calculate the center of mass
    center_of_mass = sum(v.co for v in bm.verts) / len(bm.verts)

    # calculate the displacement needed to center the origin
    displacement = -center_of_mass

    # translate the mesh data and update the bmesh
    bmesh.ops.translate(bm, vec=displacement, verts=bm.verts)

    # update the mesh data and free the bmesh
    bm.to_mesh(mesh)
    bm.free()
